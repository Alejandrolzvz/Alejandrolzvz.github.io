from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    is_superadmin: bool = False
    is_admin: bool = False
    must_change_password: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class PasswordReset(BaseModel):
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class EquipmentBase(BaseModel):
    serie: Optional[str] = None
    serie_fabrica: Optional[str] = None
    marca: Optional[str] = None
    num_factura: Optional[str] = None
    fecha_compra: Optional[str] = None
    descripcion: Optional[str] = None
    qr: Optional[str] = None
    serie_ant: Optional[str] = None
    fecha: Optional[str] = None
    cod_cliente: Optional[str] = None
    cliente: Optional[str] = None
    direccion: Optional[str] = None
    observacion: Optional[str] = None
    estatus: Optional[str] = "Disponible"
    fisicamente: Optional[str] = None
    entrega_cliente: Optional[str] = None
    cliente2: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: int

    class Config:
        orm_mode = True

class EquipmentTypeBase(BaseModel):
    prefix: str
    description: Optional[str] = None

class EquipmentTypeCreate(EquipmentTypeBase):
    pass

class EquipmentType(EquipmentTypeBase):
    id: int

    class Config:
        orm_mode = True

class BrandBase(BaseModel):
    name: str

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int

    class Config:
        orm_mode = True

class SystemSettingsBase(BaseModel):
    key: str
    value: str

class SystemSettingsCreate(SystemSettingsBase):
    pass

class SystemSettings(SystemSettingsBase):
    id: int

    class Config:
        orm_mode = True

class NextSerial(BaseModel):
    serial: str
class AuditLogBase(BaseModel):
    user_id: int
    action: str
    equipment_id: Optional[int]
    details: Optional[str]
    timestamp: datetime

class AuditLog(AuditLogBase):
    id: int

    class Config:
        orm_mode = True
