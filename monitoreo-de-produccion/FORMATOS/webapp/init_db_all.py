import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'database.db'))

def init_db():
    db_dir = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Tabla de Roles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Tabla de Usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    ''')

    # Roles por defecto
    roles_def = [(1, 'ADMIN'), (2, 'SUPER'), (3, 'PRODUC')]
    for r_id, r_name in roles_def:
        cursor.execute('INSERT OR IGNORE INTO roles (id, name) VALUES (?, ?)', (r_id, r_name))

    # Usuario admin por defecto si la tabla está vacía
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        admin_pass = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, role_id, role) 
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_pass, 1, 'ADMIN'))
        print("Usuario administrador inicial 'admin' (password: 'admin123') creado.")

    # Tabla original (Ósmosis)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_osmosis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            planta TEXT,
            hora_monitoreo TEXT,
            estatus_equipo TEXT,
            
            presion_arranque REAL,
            presion_agua_cruda REAL,
            presion_pre_filtracion REAL,
            presion_post_filtracion REAL,
            presion_pre_membranas REAL,
            presion_post_membranas REAL,
            presion_bombas REAL,
            
            rotametro_productos REAL,
            rotametro_rechazo REAL,
            
            sensor_ph REAL,
            sensor_std REAL,
            
            amperimetro REAL,
            horometro REAL,
            
            filtro_arena TEXT,
            filtro_carbon TEXT,
            suavizador_num INTEGER,
            entrada_suavizador TEXT,
            salida_suavizador TEXT,
            
            sdt_vaso1 REAL,
            sdt_vaso2 REAL,
            sdt_vaso3 REAL,
            sdt_vaso4 REAL,
            sdt_vaso5 REAL,
            sdt_final REAL,
            
            entrada_osmosis_sdt REAL,
            entrada_osmosis_dt REAL,
            
            observaciones TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # 1. Tabla Control de Calidad Monitoreo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_calidad_monitoreo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            planta TEXT,
            hora_monitoreo TEXT,
            nave TEXT,
            
            c1_cloro REAL,
            c1_ph REAL,
            c2_cloro REAL,
            c2_ph REAL,
            aduana_cloro REAL,
            
            pf_ph REAL,
            pf_std REAL,
            pf_conductividad REAL,
            pf_dureza REAL,
            pf_ozono REAL,
            pf_cloro REAL,
            
            lamp1_encendido TEXT,  -- 'Si' / 'No'
            lamp1_hora TEXT,
            lamp2_encendido TEXT,
            lamp2_hora TEXT,
            
            observaciones TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # 1.5. Tabla Calidad Lavado
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_calidad_lavado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            planta TEXT,
            hora_monitoreo TEXT,
            nave TEXT,
            
            tanque_ph REAL,
            tanque_std REAL,
            tanque_conductividad REAL,
            tanque_dureza REAL,
            tanque_ozono REAL,
            tanque_cloro REAL,
            
            alcalino_ph REAL,
            alcalino_g3 REAL,
            alcalino_temperatura REAL,
            acido_ph REAL,
            acido_pl REAL,
            enjuague_ph REAL,
            enjuague_ozono REAL,
            enjuague_cloro REAL,
            carbon_cloro_inicial REAL,
            carbon_cloro_pt REAL,
            tapas_cloro REAL,
            
            observaciones TEXT,
            created_at TIMESTAMP
        )
    ''')

    # 2. Tabla Suavizador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_suavizador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            numero_suavizador INTEGER,
            hora_monitoreo TEXT,
            
            gotas REAL,
            inicio REAL,
            final REAL,
            tiempo_total REAL,
            
            created_at TIMESTAMP
        )
    ''')

    # 3. Tabla Calidad Pozos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_calidad_pozos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            pozo INTEGER,
            hora_monitoreo TEXT,
            
            conductividad REAL,
            std REAL,
            ph REAL,
            cloro REAL,
            
            planta TEXT DEFAULT 'Planta_A',
            created_at TIMESTAMP
        )
    ''')

    # 4. Tabla Checklist Filtros y Nave
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_filtros_nave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            
            limpieza_general_cumple INTEGER,
            limpieza_general_obs TEXT,
            
            limpieza_profunda_cumple INTEGER,
            limpieza_profunda_obs TEXT,
            
            limpieza_otros_cumple INTEGER,
            limpieza_otros_obs TEXT,
            
            material_prueba_cumple INTEGER,
            material_prueba_obs TEXT,
            
            infraestructura_pintado_cumple INTEGER,
            infraestructura_pintado_obs TEXT,
            
            infraestructura_tuberias_cumple INTEGER,
            infraestructura_tuberias_obs TEXT,
            
            mantenimiento_calcas_area_cumple INTEGER,
            mantenimiento_calcas_area_obs TEXT,
            
            mantenimiento_calcas_lavadora_cumple INTEGER,
            mantenimiento_calcas_lavadora_obs TEXT,
            
            documentacion_archivos_cumple INTEGER,
            documentacion_archivos_obs TEXT,
            
            documentacion_firmas_cumple INTEGER,
            documentacion_firmas_obs TEXT,
            
            firma_ejecuta TEXT,
            firma_responsable TEXT,
            
            created_at TIMESTAMP
        )
    ''')

    # 5. Tabla Ciclos de Suavizador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_ciclos_suavizador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            numero_suavizador INTEGER,
            planta TEXT,
            estado TEXT,
            inicio_retrolavado TEXT,
            fin_retrolavado TEXT,
            inicio_regenerado TEXT,
            fin_regenerado TEXT,
            inicio_enjuage_lento TEXT,
            fin_enjuage_lento TEXT,
            inicio_enjuage_rapido TEXT,
            fin_enjuage_rapido TEXT,
            tiempo_total TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # 6. Tabla Ósmosis Vasos (Parte 2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_osmosis_vasos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            turno TEXT,
            planta TEXT,
            
            sdt_vaso1 REAL, efi_vaso1 REAL, rango_vaso1 TEXT,
            sdt_vaso2 REAL, efi_vaso2 REAL, rango_vaso2 TEXT,
            sdt_vaso3 REAL, efi_vaso3 REAL, rango_vaso3 TEXT,
            sdt_vaso4 REAL, efi_vaso4 REAL, rango_vaso4 TEXT,
            sdt_vaso5 REAL, efi_vaso5 REAL, rango_vaso5 TEXT,
            sdt_final REAL, efi_final REAL, rango_final TEXT,
            
            sdt_rechazo12 REAL, efi_rechazo12 REAL, rango_rechazo12 TEXT,
            sdt_rechazo3 REAL, efi_rechazo3 REAL, rango_rechazo3 TEXT,
            sdt_rechazo4 REAL, efi_rechazo4 REAL, rango_rechazo4 TEXT,
            sdt_rechazo5 REAL, efi_rechazo5 REAL, rango_rechazo5 TEXT,
            
            entrada_sdt REAL,
            entrada_dt REAL,
            
            observaciones TEXT,
            firma_jefe_turno_1 TEXT,
            firma_jefe_turno_2 TEXT,
            firma_subjefe_calidad TEXT,
            firma_jefe_calidad TEXT,
            
            created_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Base de datos y tablas inicializadas correctamente.")

if __name__ == '__main__':
    init_db()
