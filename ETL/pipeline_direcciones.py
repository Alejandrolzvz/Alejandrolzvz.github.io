import polars as pl
from sqlalchemy import text
from sqlalchemy.types import Date
import os
import glob
import sys
from db_utils import get_engine

engine = get_engine()

# Buscar automáticamente archivos que empiecen con "direcciones"
archivos_encontrados = glob.glob("direcciones.*")

if not archivos_encontrados:
    raise FileNotFoundError("❌ No se encontró ningún archivo que empiece con 'direcciones' en esta carpeta.")

ARCHIVO_ENTRADA = archivos_encontrados[0]
extensión = os.path.splitext(ARCHIVO_ENTRADA)[1].lower()

print(f"📂 Archivo de direcciones detectado: {ARCHIVO_ENTRADA}")

DICCIONARIO_MAPEO = {
    "UDN": "udn",
    "estado_sistema": "estado_sistema",
    "cod_cliente": "cod_cliente",
    "cod_directorio": "cod_directorio",
    "razon_social": "razon_social",
    "den_comercial": "den_comercial",
    "tipo_fiscal": "tipo_fiscal",
    "tipo_entrega": "tipo_entrega",
    "responsable": "responsable",
    "telefono": "telefono",
    "calle": "calle",
    "num_calle_ext": "num_calle_ext",
    "num_calle_int": "num_calle_int",
    "colonia": "colonia",
    "entrecalle1": "entrecalle1",
    "entrecalle2": "entrecalle2",
    "cp": "cp",
    "map_x": "map_x",
    "map_y": "map_y",
    "observaciones": "observaciones",
    "frecuencia": "frecuencia",
    "ruta_preventa": "ruta_preventa",
    "ruta_entrega": "ruta_entrega",
    "ruta_autoventa": "ruta_autoventa",
    "S_GUID": "s_guid",
    "secuencia": "secuencia",
    "secuencia_ent": "secuencia_ent",
    "fecha_alta": "fecha_alta",
    "paq_servicio": "paq_servicio",
    "correo": "correo",
    "estado_credito": "estado_credito",
    "dias_credito": "dias_credito",
    "limite_credito": "limite_credito",
    "observaciones_cred": "observaciones_cred",
    "cp_sat": "cp_sat"
}

# ==========================================
# LECTURA CON POLARS (CSV o Excel)
# ==========================================
if extensión in ['.xlsx', '.xls']:
    print("📊 Leyendo formato Excel...")
    df_raw = pl.read_excel(ARCHIVO_ENTRADA, engine="fastexcel")
elif extensión == '.csv':
    print("📝 Leyendo formato CSV con codificación Latin1...")
    
    # Reading headers as string
    columnas_reales = pl.read_csv(
        ARCHIVO_ENTRADA, 
        n_rows=0, 
        separator=",", 
        encoding="latin1",
        infer_schema_length=0
    ).columns
    
    columnas_limpias = [col.strip().replace('\xef\xbb\xbf', '') for col in columnas_reales]
    
    # Forzamos todo a String en la lectura inicial
    esquema_string = {col: pl.String for col in columnas_limpias}
    
    df_raw = pl.read_csv(
        ARCHIVO_ENTRADA,
        separator=",",
        ignore_errors=True,
        new_columns=columnas_limpias,
        encoding="latin1",
        schema_overrides=esquema_string
    )
else:
    raise ValueError(f"❌ Formato {extensión} no soportado.")

# ==========================================
# PROCESAMIENTO Y LIMPIEZA
# ==========================================
df_final = (
    df_raw
    # Filtramos filas sin S_GUID válido
    .filter(pl.col("S_GUID").is_not_null() & (pl.col("S_GUID").str.strip_chars() != ""))
    .rename(DICCIONARIO_MAPEO)
    .with_columns([
        # Fechas
        pl.col("fecha_alta").cast(pl.Date) if extensión in ['.xlsx', '.xls'] else pl.col("fecha_alta").str.to_date("%d/%m/%Y", strict=False),
        
        # Enteros: cast directo en String con strict=False (convierte 'S/N' o '' a null sin error)
        pl.col("estado_sistema").cast(pl.Int32, strict=False),
        pl.col("tipo_fiscal").cast(pl.Int32, strict=False),
        pl.col("tipo_entrega").cast(pl.Int32, strict=False),
        pl.col("secuencia").cast(pl.Int32, strict=False),
        pl.col("secuencia_ent").cast(pl.Int32, strict=False),
        pl.col("estado_credito").cast(pl.Int32, strict=False),
        pl.col("dias_credito").cast(pl.Int32, strict=False),
        
        # Flotantes / Coordenadas
        pl.col("map_x").cast(pl.Float64, strict=False),
        pl.col("map_y").cast(pl.Float64, strict=False),
        pl.col("limite_credito").cast(pl.Float64, strict=False),
    ])
)

# ==========================================
# ADUANA DE CONTROL DE DUPLICADOS REALES
# ==========================================
df_duplicados = df_final.filter(pl.col("s_guid").is_duplicated())

if df_duplicados.shape[0] > 0:
    print("\n🛑 ¡ERROR CRÍTICO! Se detectaron registros de dirección con el mismo S_GUID duplicado en el archivo.")
    print("La carga ha sido cancelada para proteger la base de datos.\n")
    print("📋 LISTA DE DIRECCIONES DUPLICADAS:")
    print("-" * 80)
    
    df_reporte = df_duplicados.select(["s_guid", "cod_cliente", "den_comercial", "calle"]).unique()
    for fila in df_reporte.iter_rows(named=True):
        print(f"👉 Cliente: {fila['cod_cliente']} | GUID: {fila['s_guid']} | Nombre: {fila['den_comercial']} | Calle: {fila['calle']}")
        
    print("-" * 80)
    print("❌ Proceso abortado. Corrige el archivo de origen y vuelve a intentarlo.")
    sys.exit(1)

print(f"📊 Archivo validado. Direcciones limpias y únicas en memoria: {df_final.shape[0]} filas.")

# ==========================================
# ESTRATEGIA UPSERT EN POSTGRESQL
# ==========================================
df_pandas = df_final.to_pandas().where(df_final.to_pandas().notnull(), None)

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    conn.execute(text("TRUNCATE TABLE staging_direcciones;"))
    
    print("📥 Volcando datos a la tabla temporal...")
    df_pandas.to_sql(
        name='staging_direcciones', 
        con=conn, 
        if_exists='append', 
        index=False,
        dtype={'fecha_alta': Date()}
    )
    
    print("🔄 Aplicando combinación (UPSERT) en PostgreSQL por S_GUID...")
    upsert_query = """
        INSERT INTO dim_direcciones (
            udn, estado_sistema, cod_cliente, cod_directorio, razon_social, den_comercial,
            tipo_fiscal, tipo_entrega, responsable, telefono, calle, num_calle_ext,
            num_calle_int, colonia, entrecalle1, entrecalle2, cp, map_x, map_y,
            observaciones, frecuencia, ruta_preventa, ruta_entrega, ruta_autoventa,
            s_guid, secuencia, secuencia_ent, fecha_alta, paq_servicio, correo,
            estado_credito, dias_credito, limite_credito, observaciones_cred, cp_sat
        )
        SELECT 
            udn, estado_sistema, cod_cliente, cod_directorio, razon_social, den_comercial,
            tipo_fiscal, tipo_entrega, responsable, telefono, calle, num_calle_ext,
            num_calle_int, colonia, entrecalle1, entrecalle2, cp, map_x, map_y,
            observaciones, frecuencia, ruta_preventa, ruta_entrega, ruta_autoventa,
            s_guid, secuencia, secuencia_ent, fecha_alta, paq_servicio, correo,
            estado_credito, dias_credito, limite_credito, observaciones_cred, cp_sat
        FROM staging_direcciones
        ON CONFLICT (s_guid) 
        DO UPDATE SET 
            udn = EXCLUDED.udn,
            estado_sistema = EXCLUDED.estado_sistema,
            cod_cliente = EXCLUDED.cod_cliente,
            cod_directorio = EXCLUDED.cod_directorio,
            razon_social = EXCLUDED.razon_social,
            den_comercial = EXCLUDED.den_comercial,
            tipo_fiscal = EXCLUDED.tipo_fiscal,
            tipo_entrega = EXCLUDED.tipo_entrega,
            responsable = EXCLUDED.responsable,
            telefono = EXCLUDED.telefono,
            calle = EXCLUDED.calle,
            num_calle_ext = EXCLUDED.num_calle_ext,
            num_calle_int = EXCLUDED.num_calle_int,
            colonia = EXCLUDED.colonia,
            entrecalle1 = EXCLUDED.entrecalle1,
            entrecalle2 = EXCLUDED.entrecalle2,
            cp = EXCLUDED.cp,
            map_x = EXCLUDED.map_x,
            map_y = EXCLUDED.map_y,
            observaciones = EXCLUDED.observaciones,
            frecuencia = EXCLUDED.frecuencia,
            ruta_preventa = EXCLUDED.ruta_preventa,
            ruta_entrega = EXCLUDED.ruta_entrega,
            ruta_autoventa = EXCLUDED.ruta_autoventa,
            secuencia = EXCLUDED.secuencia,
            secuencia_ent = EXCLUDED.secuencia_ent,
            fecha_alta = EXCLUDED.fecha_alta,
            paq_servicio = EXCLUDED.paq_servicio,
            correo = EXCLUDED.correo,
            estado_credito = EXCLUDED.estado_credito,
            dias_credito = EXCLUDED.dias_credito,
            limite_credito = EXCLUDED.limite_credito,
            observaciones_cred = EXCLUDED.observaciones_cred,
            cp_sat = EXCLUDED.cp_sat,
            fecha_actualizacion = CURRENT_TIMESTAMP;
    """
    conn.execute(text(upsert_query))

print("✅ ¡Pipeline de direcciones completado con éxito! Datos sincronizados.")