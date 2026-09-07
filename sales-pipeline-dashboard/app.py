import os
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sales Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB config setup using env vars (standard practice)
DB_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/db_name")
try:
    engine = create_engine(DB_URI)
except Exception as e:
    logger.error(f"Error initializing DB engine: {e}")
    engine = None

@app.get("/")
def read_root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return JSONResponse(status_code=404, content={"error": "Client not found"})

@app.get("/api/data")
def get_data(start_date: str = Query(None), end_date: str = Query(None)):
    if not engine:
        return JSONResponse(status_code=500, content={"error": "Database configuration missing"})

    try:
        query = """
        SELECT 
            ruta, 
            fecha_recorrido as fecha, 
            hora_inicio as hora,
            COALESCE(vta_total, 0) as vta_total,
            COALESCE(vta_4000, 0) as producto_x,
            COALESCE(vta_chulas, 0) as producto_y,
            COALESCE(vta_otros, 0) as otros,
            1 as programados,
            COALESCE(es_visitado, 0) as es_visitado,
            COALESCE(es_compra, 0) as es_compra
        FROM staging_recorridos
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND fecha_recorrido >= %(start_date)s"
            params['start_date'] = start_date
        if end_date:
            query += " AND fecha_recorrido <= %(end_date)s"
            params['end_date'] = end_date

        df = pd.read_sql(query, engine, params=params)

        if df.empty:
            return {"data": [], "min_date": None, "max_date": None}

        df['fecha'] = pd.to_datetime(df['fecha'])
        min_date = df['fecha'].min().strftime('%Y-%m-%d')
        max_date = df['fecha'].max().strftime('%Y-%m-%d')

        dias_map = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
        df['dia_semana'] = df['fecha'].dt.dayofweek.map(dias_map)
        df['mes_anio'] = df['fecha'].dt.strftime('%Y-%m')

        def get_time_bucket(t):
            if pd.isna(t): return 'regular'
            if t.hour < 8: return 'before8'
            if t.hour >= 16: return 'after16'
            return 'regular'

        df['time_bucket'] = df['hora'].apply(get_time_bucket)
        df['ruta'] = df['ruta'].astype(str).str.strip().str.upper()

        routes_result = []

        for ruta_str, group in df.groupby('ruta'):
            # Route classification logic
            if "HO" in ruta_str: 
                tipo_ruta, tipo_label = "HOGAR", "HOGAR - Reparto Doméstico"
            elif "MA" in ruta_str: 
                tipo_ruta, tipo_label = "PDV_MA", "PDV / MAYORISTA"
            elif "CO" in ruta_str: 
                tipo_ruta, tipo_label = "DFS_CO", "DFS / COMERCIOS"
            elif "EM" in ruta_str: 
                tipo_ruta, tipo_label = "EMP", "EMP / EMPRESARIAL"
            else: 
                tipo_ruta, tipo_label = "OTRO", "OTRO"

            # UDN mapping logic
            if ruta_str.startswith("01"): udn = "ELEC"
            elif ruta_str.startswith("02"): udn = "ACIA"
            else: udn = "OTRO"

            dias_dict = { d: {"before8": {}, "regular": {}, "after16": {}} for d in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'] }

            for dia in dias_dict.keys():
                for bucket in ["before8", "regular", "after16"]:
                    sdf = group[(group['dia_semana'] == dia) & (group['time_bucket'] == bucket)]
                    
                    dias_dict[dia][bucket] = {
                        "vta": float(sdf["vta_total"].sum()) if not sdf.empty else 0,
                        "producto_x": int(sdf["producto_x"].sum()) if not sdf.empty else 0,
                        "producto_y": int(sdf["producto_y"].sum()) if not sdf.empty else 0,
                        "otros": float(sdf["otros"].sum()) if not sdf.empty else 0,
                        "clientes": len(sdf[sdf['vta_total'] > 0]),
                        "programados": len(sdf) if not sdf.empty else 0,
                        "visitados": int(sdf["es_visitado"].sum()) if not sdf.empty else 0,
                        "compraron": int(sdf["es_compra"].sum()) if not sdf.empty else 0
                    }

            meses_dict = {}
            for mes, mdf in group.groupby('mes_anio'):
                meses_dict[mes] = {
                    "vta": float(mdf["vta_total"].sum()) if not mdf.empty else 0,
                    "producto_x": int(mdf["producto_x"].sum()) if not mdf.empty else 0,
                    "producto_y": int(mdf["producto_y"].sum()) if not mdf.empty else 0,
                    "otros": float(mdf["otros"].sum()) if not mdf.empty else 0,
                    "clientes": len(mdf[mdf['vta_total'] > 0]),
                    "programados": len(mdf) if not mdf.empty else 0,
                    "visitados": int(mdf["es_visitado"].sum()) if not mdf.empty else 0,
                    "compraron": int(mdf["es_compra"].sum()) if not mdf.empty else 0
                }

            routes_result.append({
                "ruta": ruta_str, "udn": udn, "tipo": tipo_ruta, "tipo_label": tipo_label,
                "dias": dias_dict, "meses": meses_dict
            })

        return { "min_date": min_date, "max_date": max_date, "data": routes_result }
        
    except Exception as e:
        logger.error(f"API Error processing data: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal Processing Error", "detail": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)