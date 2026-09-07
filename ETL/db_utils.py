import os
import urllib.parse
from sqlalchemy import create_engine

def get_engine():
    # ==========================================
    # CONFIGURACIÓN Y CONEXIÓN SEGURA
    # ==========================================
    DB_USER = "postgres"
    DB_PASS = os.environ.get("PIPELINE_DB_PASSWORD", "")
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "pipeline_ventas"

    password_segura = urllib.parse.quote_plus(DB_PASS)
    CON_STR = f"postgresql://{DB_USER}:{password_segura}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(CON_STR)
