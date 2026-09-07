import polars as pl
from db_utils import get_engine

engine = get_engine()

# ==========================================
# CONSULTA SQL PARA ÚLTIMAS 5 FECHAS POR UDN
# ==========================================
query = """
WITH fechas_ordenadas AS (
    SELECT 
        udn,
        fecha_liquidacion,
        ROW_NUMBER() OVER (
            PARTITION BY udn 
            ORDER BY fecha_liquidacion DESC
        ) AS ranking
    FROM (
        SELECT DISTINCT 
            udn, 
            fecha_liquidacion 
        FROM staging_ventas 
        WHERE fecha_liquidacion IS NOT NULL
    ) sub_fechas
)
SELECT 
    udn,
    ranking AS nro,
    fecha_liquidacion AS ultima_fecha
FROM fechas_ordenadas
WHERE ranking <= 5
ORDER BY 
    udn ASC, 
    fecha_liquidacion DESC;
"""

print("🔍 Consultando las últimas 5 fechas de liquidación por UDN...\n")

with engine.connect() as conn:
    df_fechas = pl.read_database(query, connection=conn)

# Mostramos todas las filas para ver la lista completa
pl.Config.set_tbl_rows(-1)
print(df_fechas)