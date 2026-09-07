from sqlalchemy import Column, Integer, String, Boolean, DateTime
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_superadmin = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=True)

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    serie = Column(String, index=True)
    serie_fabrica = Column(String)
    marca = Column(String)
    num_factura = Column(String)
    fecha_compra = Column(String)
    descripcion = Column(String)
    qr = Column(String)
    serie_ant = Column(String)
    fecha = Column(String)
    cod_cliente = Column(String)
    cliente = Column(String)
    direccion = Column(String)
    observacion = Column(String)
    estatus = Column(String, default="Disponible", nullable=False)
    fisicamente = Column(String)
    entrega_cliente = Column(String)
    cliente2 = Column(String)

class EquipmentType(Base):
    __tablename__ = "equipment_types"

    id = Column(Integer, primary_key=True, index=True)
    prefix = Column(String, unique=True, index=True)  # e.g. "ANAQ"
    description = Column(String)  # e.g. "ANAQUEL"

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    action = Column(String) # "CREATE", "UPDATE", "DELETE"
    equipment_id = Column(Integer)
    details = Column(String) # optional details
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
