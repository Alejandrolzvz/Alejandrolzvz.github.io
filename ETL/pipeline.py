import polars as pl
from sqlalchemy import text
from sqlalchemy.types import Date
import os
import glob
import sys
from db_utils import get_engine

engine = get_engine()

# Buscar automáticamente cualquier archivo que empiece con "ventas"
archivos_encontrados = glob.glob("ventas.*")

if not archivos_encontrados:
    raise FileNotFoundError("❌ No se encontró ningún archivo que empiece con 'ventas' (ej. ventas.csv o ventas.xlsx) en esta carpeta.")

ARCHIVO_ENTRADA = archivos_encontrados[0]
extensión = os.path.splitext(ARCHIVO_ENTRADA)[1].lower()

print(f"📂 Archivo detectado automáticamente: {ARCHIVO_ENTRADA}")

# ==========================================
# DICCIONARIO DE MAPEO
# ==========================================
DICCIONARIO_MAPEO = {
    "SYSUDN_CODIGO_K": "udn",
    "LIQUID_REFERENCIA": "ref_liquidacion",
    "CTECLI_CODIGO_K": "cod_cliente",
    "CFGEPL_CODIGO_K": "id_vendedor",
    "CFGEPL_NOMBRE": "nombre_vendedor",
    "CFGECO_CODIGO_K": "ruta_eco",
    "CFGECO_DESCRIPCION": "eco_descr",
    "LIQUID_AYUDANTE1": "ayudante_1",
    "LIQUID_AYUDANTE2": "ayudante_2",
    "LIQUID_FECHAENT": "fecha_liquidacion",
    "VTARUT_CODIGO_K": "ruta",
    "VTARUT_DESCRIPCION": "nombre_ruta",
    "PRODUC_CODIGO_K": "id_producto",
    "PRODUC_DESCRIPCION": "descripcion_producto",
    "PROPRE_CODIGO_K": "codigo_transaccion",
    "FACDOC_FECHA": "fecha_factura",
    "TPO_VTA": "tipo_venta",
    "PIEZAS": "piezas",
    "COSTO": "costo_unitario",
    "IMPORTE": "importe",
    "LIQUIDACION": "liquidacion",
    "VENTA": "venta_total"
}

# ==========================================
# LECTURA INDISTINTA (CSV o Excel)
# ==========================================
if extensión in ['.xlsx', '.xls']:
    print("📊 Leyendo formato Excel...")
    df_original = pl.read_excel(ARCHIVO_ENTRADA, engine="fastexcel")
    lazy_df = df_original.lazy()
    
elif extensión == '.csv':
    print("📝 Leyendo formato CSV (Separado por Comas de forma estricta)...")
    
    columnas_reales = pl.read_csv(
        ARCHIVO_ENTRADA, 
        n_rows=0, 
        separator=",", 
        encoding="latin1", 
        infer_schema_length=0
    ).columns
    columnas_limpias = [col.strip() for col in columnas_reales]
    
    df_original = pl.read_csv(
        ARCHIVO_ENTRADA, 
        separator=",", 
        ignore_errors=True, 
        new_columns=columnas_limpias,
        encoding="latin1",
        schema_overrides={
            "CFGEPL_CODIGO_K": pl.String,
            "SYSUDN_CODIGO_K": pl.String,
            "CFGECO_CODIGO_K": pl.String,
            "VTARUT_CODIGO_K": pl.String,
            "PRODUC_CODIGO_K": pl.String,
            "PROPRE_CODIGO_K": pl.String
        }
    )
    lazy_df = df_original.lazy()
else:
    raise ValueError(f"❌ Formato {extensión} no soportado.")

# ==========================================
# PROCESAMIENTO Y LIMPIEZA
# ==========================================
df_final = (
    lazy_df
    # 1. Filtramos para eliminar filas vacías
    .filter(
        pl.col("SYSUDN_CODIGO_K").is_not_null() & 
        (pl.col("SYSUDN_CODIGO_K").str.strip_chars() != "")
    )
    # 2. Renombramos columnas
    .rename(DICCIONARIO_MAPEO)
    .with_columns([
        # Formateo de fechas
        pl.col("fecha_liquidacion").cast(pl.Date) if extensión in ['.xlsx', '.xls'] else pl.col("fecha_liquidacion").str.to_date("%d/%m/%Y", strict=False),
        pl.col("fecha_factura").cast(pl.Date) if extensión in ['.xlsx', '.xls'] else pl.col("fecha_factura").str.to_date("%d/%m/%Y", strict=False),
        
        # Conversiones numéricas
        pl.col("piezas").cast(pl.Int32, strict=False),
        pl.col("costo_unitario").cast(pl.Float64, strict=False),
        pl.col("importe").cast(pl.Float64, strict=False),
        pl.col("liquidacion").cast(pl.Float64, strict=False),
        pl.col("venta_total").cast(pl.Float64, strict=False),
    ])
    .collect(engine="streaming")
)

print(f"📊 Datos transformados con éxito. Total de filas en el archivo: {df_final.shape[0]}")

# ==========================================
# ADUANA DE CONTROL DE FECHAS REPETIDAS
# ==========================================
print("\n🔍 Verificando coincidencias de fechas en la base de datos...")

# Extraemos las combinaciones únicas (udn, fecha_liquidacion) que vienen en el archivo
fechas_archivo = (
    df_final
    .filter(pl.col("fecha_liquidacion").is_not_null())
    .select(["udn", "fecha_liquidacion"])
    .unique()
)

# Consultamos a PostgreSQL qué fechas ya existen en staging_ventas
query_fechas_db = """
SELECT DISTINCT 
    udn, 
    fecha_liquidacion 
FROM staging_ventas 
WHERE fecha_liquidacion IS NOT NULL;
"""

with engine.connect() as conn:
    df_fechas_db = pl.read_database(query_fechas_db, connection=conn)

# Convertimos tipo de fecha a Date en df_fechas_db por compatibilidad
if df_fechas_db.shape[0] > 0:
    df_fechas_db = df_fechas_db.with_columns(pl.col("fecha_liquidacion").cast(pl.Date))
    
    # Hacemos INNER JOIN para encontrar cruces exactos (mismo UDN y misma Fecha)
    coincidencias = fechas_archivo.join(df_fechas_db, on=["udn", "fecha_liquidacion"], how="inner")
    
    if coincidencias.shape[0] > 0:
        print("\n⚠️  ¡ADVERTENCIA DE FECHAS REPETIDAS!")
        print("El archivo contiene información de fechas que YA existen en la base de datos:")
        print("-" * 65)
        
        for fila in coincidencias.iter_rows(named=True):
            fecha_str = fila['fecha_liquidacion'].strftime('%d/%m/%Y') if fila['fecha_liquidacion'] else 'N/A'
            print(f"👉 UDN: {fila['udn']} | Fecha de Liquidación existente: {fecha_str}")
            
        print("-" * 65)
        
        # Pausa interactiva para decidir si continuar
        respuesta = input("❓ ¿Deseas ingresar estos datos de todas formas? (s/n): ").strip().lower()
        
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Carga cancelada por el usuario. La base de datos no fue modificada.")
            sys.exit(0)
        else:
            print("⚠️  Continuando con la inserción bajo responsabilidad del usuario...")
    else:
        print("✅ No se detectaron fechas repetidas en la base de datos.")
else:
    print("ℹ️  La tabla staging_ventas está vacía o no tiene registros previos.")

# ==========================================
# INSERCIÓN EN POSTGRESQL
# ==========================================
print("\n📥 Insertando datos en PostgreSQL...")

df_pandas = df_final.to_pandas()
df_pandas = df_pandas.where(df_pandas.notnull(), None)

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    df_pandas.to_sql(
        name='staging_ventas', 
        con=conn, 
        if_exists='append', 
        index=False,
        dtype={
            'fecha_liquidacion': Date(),
            'fecha_factura': Date()
        }
    )

print("✅ ¡Pipeline ejecutado con éxito! Tus datos ya están guardados en PostgreSQL.")