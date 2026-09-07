import polars as pl
from sqlalchemy import text
from sqlalchemy.types import Date
import os
import glob
import sys
from db_utils import get_engine

engine = get_engine()

# Buscar automáticamente archivos que empiecen con "clientes"
archivos_encontrados = glob.glob("clientes.*")

if not archivos_encontrados:
    raise FileNotFoundError("❌ No se encontró ningún archivo que empiece con 'clientes' en esta carpeta.")

ARCHIVO_ENTRADA = archivos_encontrados[0]
extensión = os.path.splitext(ARCHIVO_ENTRADA)[1].lower()

print(f"📂 Archivo de clientes detectado: {ARCHIVO_ENTRADA}")

DICCIONARIO_MAPEO = {
    "UDN": "udn",
    "ESTADO": "estado",
    "CODIGO": "codigo",
    "Razon_Social": "razon_social",
    "CLIENTE": "cliente",
    "RFC": "rfc",
    "FECHA_ALTA": "fecha_alta",
    "FECHA_BAJA": "fecha_baja",
    "CONTACTO": "contacto",
    "VALES": "vales",
    "ESTADO_CRED": "estado_cred",
    "DIAS_CRED": "dias_cred",
    "LIMITE_CRED": "limite_cred",
    "OBSERVACIONES": "observaciones",
    "OBSERVACIONES_CRED": "observaciones_cred"
}

# ==========================================
# LECTURA CON POLARS (CSV o Excel)
# ==========================================
if extensión in ['.xlsx', '.xls']:
    print("📊 Leyendo formato Excel...")
    df_raw = pl.read_excel(ARCHIVO_ENTRADA, engine="fastexcel")
elif extensión == '.csv':
    print("📝 Leyendo formato CSV con codificación Latin1...")
    
    # 1. infer_schema_length=0 evita que intente adivinar tipos al leer las cabeceras
    columnas_reales = pl.read_csv(
        ARCHIVO_ENTRADA, 
        n_rows=0, 
        separator=",", 
        encoding="latin1",
        infer_schema_length=0
    ).columns
    
    columnas_limpias = [col.strip().replace('\xef\xbb\xbf', '') for col in columnas_reales]
    
    # 2. Forzamos todas las columnas a String para aceptar notación científica '1E+12' y evitar errores
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
# PROCESAMIENTO Y LIMPIEZA INICIAL
# ==========================================
df_final = (
    df_raw
    .filter(pl.col("CODIGO").is_not_null() & (pl.col("CODIGO").str.strip_chars() != ""))
    .rename(DICCIONARIO_MAPEO)
    .with_columns([
        # Formateo de fechas
        pl.col("fecha_alta").cast(pl.Date) if extensión in ['.xlsx', '.xls'] else pl.col("fecha_alta").str.to_date("%d/%m/%Y", strict=False),
        pl.col("fecha_baja").cast(pl.Date) if extensión in ['.xlsx', '.xls'] else pl.col("fecha_baja").str.to_date("%d/%m/%Y", strict=False),
        
        # Tipos enteros tolerando posibles nulos o texto
        pl.col("estado").cast(pl.Int32, strict=False),
        pl.col("vales").cast(pl.Int32, strict=False),        
        pl.col("estado_cred").cast(pl.Int32, strict=False),  
        pl.col("dias_cred").cast(pl.Int32, strict=False),
        
        # Float64 convierte perfectamente notaciones exponenciales como '1E+12'
        pl.col("limite_cred").cast(pl.Float64, strict=False),
    ])
)

# ==========================================
# ADUANA DE CONTROL DE DUPLICADOS INTERNOS
# ==========================================
df_duplicados = df_final.filter(pl.col("codigo").is_duplicated())

if df_duplicados.shape[0] > 0:
    print("\n🛑 ¡ERROR CRÍTICO! Se detectaron códigos duplicados dentro del mismo archivo.")
    print("La carga ha sido cancelada para proteger la base de datos.\n")
    print("📋 LISTA DE REGISTROS DUPLICADOS:")
    print("-" * 80)
    
    df_reporte = df_duplicados.select(["codigo", "cliente"]).unique()
    
    for fila in df_reporte.iter_rows(named=True):
        print(f"👉 Código Duplicado: {fila['codigo']} | Cliente: {fila['cliente']}")
        
    print("-" * 80)
    print("❌ Proceso abortado. Corrige el archivo de origen y vuelve a intentarlo.")
    sys.exit(1)

print(f"📊 Archivo validado. Clientes limpios y únicos en memoria: {df_final.shape[0]} filas.")

# ==========================================
# ESTRATEGIA UPSERT EN POSTGRESQL
# ==========================================
df_pandas = df_final.to_pandas().where(df_final.to_pandas().notnull(), None)

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    conn.execute(text("TRUNCATE TABLE staging_clientes;"))
    
    print("📥 Volcando datos a la tabla temporal...")
    df_pandas.to_sql(
        name='staging_clientes', 
        con=conn, 
        if_exists='append', 
        index=False,
        dtype={'fecha_alta': Date(), 'fecha_baja': Date()}
    )
    
    print("🔄 Aplicando combinación (UPSERT) en PostgreSQL...")
    upsert_query = """
        INSERT INTO dim_clientes (
            udn, estado, codigo, razon_social, cliente, rfc, fecha_alta, fecha_baja, 
            contacto, vales, estado_cred, dias_cred, limite_cred, observaciones, observaciones_cred
        )
        SELECT 
            udn, estado, codigo, razon_social, cliente, rfc, fecha_alta, fecha_baja, 
            contacto, vales, estado_cred, dias_cred, limite_cred, observaciones, observaciones_cred
        FROM staging_clientes
        ON CONFLICT (codigo) 
        DO UPDATE SET 
            udn = EXCLUDED.udn,
            estado = EXCLUDED.estado,
            razon_social = EXCLUDED.razon_social,
            cliente = EXCLUDED.cliente,
            rfc = EXCLUDED.rfc,
            fecha_alta = EXCLUDED.fecha_alta,
            fecha_baja = EXCLUDED.fecha_baja,
            contacto = EXCLUDED.contacto,
            vales = EXCLUDED.vales,
            estado_cred = EXCLUDED.estado_cred,
            dias_cred = EXCLUDED.dias_cred,
            limite_cred = EXCLUDED.limite_cred,
            observaciones = EXCLUDED.observaciones,
            observaciones_cred = EXCLUDED.observaciones_cred,
            fecha_actualizacion = CURRENT_TIMESTAMP;
    """
    conn.execute(text(upsert_query))
    
print("✅ ¡Pipeline de clientes completado con éxito! Datos sincronizados.")