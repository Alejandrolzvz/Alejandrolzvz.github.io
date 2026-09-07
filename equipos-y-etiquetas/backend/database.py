from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Example: postgresql://postgres:password@localhost/equipos_db
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/equipos_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

PIPELINE_VENTAS_DATABASE_URL = os.getenv("PIPELINE_VENTAS_DATABASE_URL")
ventas_engine = create_engine(PIPELINE_VENTAS_DATABASE_URL, pool_pre_ping=True) if PIPELINE_VENTAS_DATABASE_URL else None
VentasSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ventas_engine) if ventas_engine else None

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
