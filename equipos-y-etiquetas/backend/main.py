from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
import openpyxl
import io
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import timedelta
import os

from . import models, schemas, auth, database

models.Base.metadata.create_all(bind=database.engine)

def migrate_equipment_status():
    """Add the explicit status field and migrate the legacy field once."""
    with database.engine.begin() as connection:
        inspector = inspect(connection)
        columns = {column['name'] for column in inspector.get_columns('equipment')}
        if 'estatus' not in columns:
            connection.execute(text('ALTER TABLE equipment ADD COLUMN estatus VARCHAR'))
            connection.execute(text("UPDATE equipment SET estatus = CASE LOWER(COALESCE(fisicamente, '')) WHEN 'asignado' THEN 'Asignado' WHEN 'baja' THEN 'Baja' ELSE 'Disponible' END"))
            connection.execute(text("ALTER TABLE equipment ALTER COLUMN estatus SET DEFAULT 'Disponible'"))
            connection.execute(text("UPDATE equipment SET estatus = 'Disponible' WHERE estatus IS NULL"))
        if 'direccion' not in columns:
            connection.execute(text('ALTER TABLE equipment ADD COLUMN direccion VARCHAR'))

migrate_equipment_status()

app = FastAPI(title="Equipos API")

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except auth.JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_superadmin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not enough permissions (Superadmin required)")
    return current_user

def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_superadmin and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions (Admin required)")
    return current_user

# Setup initial superadmin if table is empty
@app.on_event("startup")
def create_initial_superadmin():
    db = database.SessionLocal()
    user = db.query(models.User).filter(models.User.username == "admin").first()
    if not user:
        hashed_pw = auth.get_password_hash("admin123")
        new_admin = models.User(username="admin", hashed_password=hashed_pw, is_superadmin=True, is_admin=True, must_change_password=False)
        db.add(new_admin)
        db.commit()
    db.close()


@app.post("/api/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, is_superadmin=user.is_superadmin, is_admin=user.is_admin, must_change_password=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/api/users", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    return db.query(models.User).order_by(models.User.id).all()

@app.post("/api/users/me/change-password")
def change_password(payload: schemas.PasswordChange, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not auth.verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    current_user.hashed_password = auth.get_password_hash(payload.new_password)
    current_user.must_change_password = False
    db.commit()
    return {"ok": True}

@app.post("/api/users/{user_id}/reset-password")
def reset_password(user_id: int, payload: schemas.PasswordReset, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = auth.get_password_hash(payload.new_password)
    user.must_change_password = True
    db.commit()
    return {"ok": True}

# --- EQUIPMENT CRUD ---

def log_action(db: Session, user_id: int, action: str, equipment_id: int, details: str = ""):
    log = models.AuditLog(user_id=user_id, action=action, equipment_id=equipment_id, details=details)
    db.add(log)
    db.commit()

VALID_EQUIPMENT_STATUS = {'Disponible', 'Asignado', 'Baja'}

def normalize_equipment_status(value):
    return value if value in VALID_EQUIPMENT_STATUS else 'Disponible'

@app.get("/api/equipos", response_model=list[schemas.Equipment])
def read_equipos(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    equipos = db.query(models.Equipment).offset(skip).limit(limit).all()
    return equipos

@app.get("/api/clientes")
def search_clientes(q: str = "", current_user: models.User = Depends(get_current_user)):
    if not database.VentasSessionLocal:
        return []
    search = q.strip()
    if len(search) < 2:
        return []
    db = database.VentasSessionLocal()
    try:
        query = text("""
            SELECT codigo, razon_social, cliente
            FROM public.dim_clientes
                WHERE codigo ILIKE :pattern
                ORDER BY codigo
            LIMIT 20
        """)
        rows = db.execute(query, {"pattern": f"%{search}%"}).mappings().all()
        return [
            {
                "codigo": (row["codigo"] or "").strip(),
                "nombre_comercial": (row["cliente"] or row["razon_social"] or "").strip()
            }
            for row in rows
        ]
    except Exception:
        return []
    finally:
        db.close()

@app.get("/api/direcciones")
def search_direcciones(cod_cliente: str = "", current_user: models.User = Depends(get_current_user)):
    if not database.VentasSessionLocal or not cod_cliente.strip():
        return []
    db = database.VentasSessionLocal()
    try:
        query = text("""
            SELECT calle, num_calle_ext, num_calle_int, colonia
            FROM public.dim_direcciones
            WHERE TRIM(cod_cliente) = :cod_cliente
        """)
        rows = db.execute(query, {"cod_cliente": cod_cliente.strip()}).mappings().all()
        addresses = []
        for row in rows:
            parts = [row["calle"], row["num_calle_ext"], row["num_calle_int"], row["colonia"]]
            address = ", ".join(str(part).strip() for part in parts if part not in (None, "") and str(part).strip())
            if address:
                addresses.append({"direccion": address})
        return addresses
    except Exception:
        return []
    finally:
        db.close()

@app.post("/api/equipos", response_model=schemas.Equipment)
def create_equipo(equipo: schemas.EquipmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    equipo.estatus = normalize_equipment_status(equipo.estatus)
    if equipo.estatus != 'Asignado':
        equipo.cliente = None
    db_equipo = models.Equipment(**equipo.dict())
    db.add(db_equipo)
    db.commit()
    db.refresh(db_equipo)
    log_action(db, current_user.id, "CREATE", db_equipo.id)
    return db_equipo

@app.put("/api/equipos/{equipo_id}", response_model=schemas.Equipment)
def update_equipo(equipo_id: int, equipo: schemas.EquipmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_equipo = db.query(models.Equipment).filter(models.Equipment.id == equipo_id).first()
    if not db_equipo:
        raise HTTPException(status_code=404, detail="Equipo not found")
    
    equipo.estatus = normalize_equipment_status(equipo.estatus)
    if equipo.estatus != 'Asignado':
        equipo.cliente = None
    for var, value in equipo.dict().items():
        setattr(db_equipo, var, value)
    
    db.commit()
    db.refresh(db_equipo)
    log_action(db, current_user.id, "UPDATE", db_equipo.id)
    return db_equipo

@app.delete("/api/equipos/{equipo_id}")
def delete_equipo(equipo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    db_equipo = db.query(models.Equipment).filter(models.Equipment.id == equipo_id).first()
    if not db_equipo:
        raise HTTPException(status_code=404, detail="Equipo not found")
    db.delete(db_equipo)
    db.commit()
    log_action(db, current_user.id, "DELETE", equipo_id)
    return {"ok": True}

@app.post("/api/equipos/upload")
async def upload_equipos(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    contents = await file.read()
    wb = openpyxl.load_workbook(filename=io.BytesIO(contents), data_only=True)
    ws = wb.active
    
    headers = [str(cell.value).strip() if cell.value else "" for cell in ws[1]]
    
    count = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row): continue
        row_dict = dict(zip(headers, row))
        
        equipo = models.Equipment(
            serie=str(row_dict.get('SERIE', '')) if row_dict.get('SERIE') else None,
            serie_fabrica=str(row_dict.get('SERIE FABRICA', '')) if row_dict.get('SERIE FABRICA') else None,
            marca=str(row_dict.get('MARCA', '')) if row_dict.get('MARCA') else None,
            num_factura=str(row_dict.get('NUM DE FACTURA', '')) if row_dict.get('NUM DE FACTURA') else None,
            fecha_compra=str(row_dict.get('FECHA DE COMPRA', '')) if row_dict.get('FECHA DE COMPRA') else None,
            descripcion=str(row_dict.get('DESCRIPCIÓN', '')) if row_dict.get('DESCRIPCIÓN') else None,
            qr=str(row_dict.get('QR', '')) if row_dict.get('QR') else None,
            serie_ant=str(row_dict.get('SERIE ANT', '')) if row_dict.get('SERIE ANT') else None,
            fecha=str(row_dict.get('FECHA', '')) if row_dict.get('FECHA') else None,
            cod_cliente=str(row_dict.get('COD CLIENTE', '')) if row_dict.get('COD CLIENTE') else None,
            cliente=str(row_dict.get('CLIENTE', '')) if row_dict.get('CLIENTE') else None,
            observacion=str(row_dict.get('OBSERVACIÓN', '')) if row_dict.get('OBSERVACIÓN') else None,
            estatus=normalize_equipment_status(str(row_dict.get('ESTATUS', row_dict.get('FISICAMENTE', 'Disponible')))) if row_dict.get('ESTATUS', row_dict.get('FISICAMENTE')) else 'Disponible',
            fisicamente=str(row_dict.get('FISICAMENTE', '')) if row_dict.get('FISICAMENTE') else None,
            entrega_cliente=str(row_dict.get('ENTREGA CLIENTE', '')) if row_dict.get('ENTREGA CLIENTE') else None,
            cliente2=str(row_dict.get('CLIENTE2', '')) if row_dict.get('CLIENTE2') else None,
        )
        db.add(equipo)
        count += 1
        
    db.commit()
    log_action(db, current_user.id, "UPLOAD_EXCEL", 0, f"Imported {count} items")
    return {"ok": True, "count": count}

# --- EQUIPMENT TYPES CRUD ---
import re

@app.get("/api/tipos", response_model=list[schemas.EquipmentType])
def read_tipos(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.EquipmentType).order_by(models.EquipmentType.prefix).all()

@app.post("/api/tipos", response_model=schemas.EquipmentType)
def create_tipo(tipo: schemas.EquipmentTypeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    existing = db.query(models.EquipmentType).filter(models.EquipmentType.prefix == tipo.prefix.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Prefix already exists")
    db_tipo = models.EquipmentType(prefix=tipo.prefix.upper(), description=tipo.description)
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

@app.delete("/api/tipos/{tipo_id}")
def delete_tipo(tipo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    db_tipo = db.query(models.EquipmentType).filter(models.EquipmentType.id == tipo_id).first()
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo not found")
    db.delete(db_tipo)
    db.commit()
    return {"ok": True}

@app.get("/api/equipos/next-serial/{prefix}", response_model=schemas.NextSerial)
def next_serial(prefix: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    prefix = prefix.upper()
    # Find all equipment whose serie starts with this prefix
    equipos = db.query(models.Equipment.serie).filter(
        models.Equipment.serie.like(f"{prefix}-%")
    ).all()
    
    max_num = 0
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    for (serie,) in equipos:
        if serie:
            m = pattern.match(serie)
            if m:
                num = int(m.group(1))
                if num > max_num:
                    max_num = num
    
    next_num = max_num + 1
    return {"serial": f"{prefix}-{next_num:04d}"}

@app.post("/api/tipos/upload")
async def upload_tipos(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    contents = await file.read()
    wb = openpyxl.load_workbook(filename=io.BytesIO(contents), data_only=True)
    ws = wb.active
    
    headers = [str(cell.value).strip().upper() if cell.value else "" for cell in ws[1]]
    
    count = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row): continue
        row_dict = dict(zip(headers, row))
        
        prefix_val = str(row_dict.get('SERIE', row_dict.get('SERI', row_dict.get('PREFIJO', '')))).strip().upper() if row_dict.get('SERIE', row_dict.get('SERI', row_dict.get('PREFIJO'))) else None
        desc_val = str(row_dict.get('DESCRIPCIÓN', row_dict.get('DESCRIPCION', ''))).strip() if row_dict.get('DESCRIPCIÓN', row_dict.get('DESCRIPCION')) else None
        
        if not prefix_val:
            continue
            
        existing = db.query(models.EquipmentType).filter(models.EquipmentType.prefix == prefix_val).first()
        if existing:
            existing.description = desc_val or existing.description
        else:
            db.add(models.EquipmentType(prefix=prefix_val, description=desc_val))
            count += 1
    
    db.commit()
    log_action(db, current_user.id, "UPLOAD_TIPOS_EXCEL", 0, f"Imported {count} types")
    return {"ok": True, "count": count}

# --- BRANDS CRUD ---
@app.get("/api/marcas", response_model=list[schemas.Brand])
def read_marcas(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Brand).order_by(models.Brand.name).all()

@app.post("/api/marcas", response_model=schemas.Brand)
def create_marca(marca: schemas.BrandCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    existing = db.query(models.Brand).filter(models.Brand.name == marca.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Brand already exists")
    db_marca = models.Brand(name=marca.name)
    db.add(db_marca)
    db.commit()
    db.refresh(db_marca)
    return db_marca

@app.delete("/api/marcas/{marca_id}")
def delete_marca(marca_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    db_marca = db.query(models.Brand).filter(models.Brand.id == marca_id).first()
    if not db_marca:
        raise HTTPException(status_code=404, detail="Marca not found")
    db.delete(db_marca)
    db.commit()
    return {"ok": True}

# --- SETTINGS CRUD ---
@app.get("/api/settings", response_model=list[schemas.SystemSettings])
def read_settings(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.SystemSettings).all()

@app.post("/api/settings")
def update_setting(setting: schemas.SystemSettingsCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_superadmin)):
    db_setting = db.query(models.SystemSettings).filter(models.SystemSettings.key == setting.key).first()
    if db_setting:
        db_setting.value = setting.value
    else:
        db_setting = models.SystemSettings(key=setting.key, value=setting.value)
        db.add(db_setting)
    db.commit()
    return {"ok": True}

# Serve frontend statically
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
