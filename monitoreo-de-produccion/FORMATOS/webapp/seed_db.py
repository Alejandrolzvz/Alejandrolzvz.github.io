import random
import math
from utils.db import get_db_connection
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from init_db_all import init_db

def seed_database():
    # Asegurar que las tablas estén inicializadas
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Limpiando datos previos de prueba...")
    tables = [
        'registro_osmosis', 'registro_calidad_monitoreo', 'registro_calidad_lavado',
        'registro_suavizador', 'registro_calidad_pozos', 'registro_filtros_nave',
        'registro_ciclos_suavizador', 'registro_osmosis_vasos'
    ]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    print("Generando datos con alta variedad y tendencias para los últimos 15 días...")
    
    # 1. Usuarios de prueba
    users_to_add = [
        ('admin_prueba', 'admin123', 'ADMIN', 1),
        ('operador_prueba', 'operador123', 'PRODUC', 2)
    ]
    
    for username, pwd, role, role_id in users_to_add:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            hashed = generate_password_hash(pwd)
            cursor.execute("INSERT INTO users (username, password_hash, role, role_id) VALUES (?, ?, ?, ?)", (username, hashed, role, role_id))
            print(f"Usuario '{username}' listo.")
            
    hoy = datetime.now()
    horas = ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    
    # 2. Registros de Ósmosis Inversa (con variaciones sinusoidal + ruido)
    count_osmosis = 0
    for i in range(15, -1, -1):
        fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
        # Simulamos variación diaria y horaria
        base_trend = math.sin(i / 3.0) * 5.0
        for h_idx, hora in enumerate(horas):
            var = base_trend + random.uniform(-3.0, 3.0)
            entrada_sdt = round(250.0 + var * 2.0, 1)
            sdt_final = round(max(4.0, 10.0 + var * 0.5 + random.uniform(-1.0, 1.0)), 1)
            flujo_prod = round(50.0 + var + random.uniform(-2.0, 2.0), 1)
            flujo_rech = round(15.0 - var * 0.3 + random.uniform(-1.5, 1.5), 1)
            pre_membrana = round(120.0 + var * 1.5 + random.uniform(-3.0, 3.0), 1)
            post_membrana = round(100.0 + var * 0.8 + random.uniform(-2.0, 2.0), 1)
            
            cursor.execute('''
                INSERT INTO registro_osmosis (
                    fecha, planta, hora_monitoreo, estatus_equipo,
                    presion_arranque, presion_agua_cruda, presion_pre_filtracion, presion_post_filtracion,
                    presion_pre_membranas, presion_post_membranas, presion_bombas,
                    rotametro_productos, rotametro_rechazo,
                    sensor_ph, sensor_std,
                    amperimetro, horometro,
                    filtro_arena, filtro_carbon, suavizador_num, entrada_suavizador, salida_suavizador,
                    entrada_osmosis_sdt, sdt_final,
                    observaciones, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha_str, 'Planta_A', hora, 'Encendido' if random.random() > 0.1 else 'Apagado',
                round(100.0 + random.uniform(-2, 2), 1), round(95.0 + random.uniform(-3, 3), 1),
                round(90.0 + random.uniform(-2, 2), 1), round(88.0 + random.uniform(-2, 2), 1),
                pre_membrana, post_membrana, round(130.0 + random.uniform(-4, 4), 1),
                flujo_prod, flujo_rech,
                round(7.2 + random.uniform(-0.4, 0.4), 2), round(entrada_sdt * 0.3, 1),
                round(10.5 + random.uniform(-1.0, 1.0), 1), round(500.0 + count_osmosis * 2.5, 1),
                'OK', 'OK', (h_idx % 2) + 1, 'Limpia', 'Limpia',
                entrada_sdt, sdt_final,
                'Monitoreo rutinario' if random.random() > 0.2 else 'Ajuste de válvulas realizado',
                (hoy - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
            ))
            count_osmosis += 1

    # 3. Registros de Calidad Monitoreo (con variedad)
    count_calidad = 0
    for i in range(15, -1, -1):
        fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
        for hora in horas:
            c1_cloro = round(random.uniform(1.8, 2.4), 2)
            c1_ph = round(random.uniform(6.8, 7.5), 2)
            c2_cloro = round(random.uniform(0.1, 0.4), 2)
            c2_ph = round(random.uniform(6.9, 7.4), 2)
            aduana_cloro = round(random.uniform(1.2, 1.8), 2)
            pf_ph = round(random.uniform(7.0, 7.6), 2)
            pf_std = round(random.uniform(75.0, 95.0), 1)
            pf_conduct = round(pf_std * 2.0, 1)
            pf_dureza = round(random.uniform(4.0, 12.0), 1)
            pf_ozono = round(random.uniform(3.0, 4.5), 2)
            
            cursor.execute('''
                INSERT INTO registro_calidad_monitoreo (
                    fecha, planta, hora_monitoreo, nave,
                    c1_cloro, c1_ph, c2_cloro, c2_ph, aduana_cloro,
                    pf_ph, pf_std, pf_conductividad, pf_dureza, pf_ozono, pf_cloro,
                    lamp1_encendido, lamp1_hora, lamp2_encendido, lamp2_hora,
                    observaciones, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha_str, 'Planta_A', hora, f'Nave {(count_calidad % 2) + 1}',
                c1_cloro, c1_ph, c2_cloro, c2_ph, aduana_cloro,
                pf_ph, pf_std, pf_conduct, pf_dureza, pf_ozono, 0.0,
                'Si', '24 hrs', 'Si' if random.random() > 0.05 else 'No', '24 hrs',
                'Calidad dentro de rango',
                (hoy - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
            ))
            count_calidad += 1

    # 4. Registros de Calidad Lavado
    count_lavado = 0
    for i in range(15, -1, -1):
        fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
        for hora in ["08:30", "12:30", "16:30"]:
            cursor.execute('''
                INSERT INTO registro_calidad_lavado (
                    fecha, planta, hora_monitoreo, nave,
                    tanque_ph, tanque_std, tanque_conductividad, tanque_dureza, tanque_ozono, tanque_cloro,
                    alcalino_ph, alcalino_g3, alcalino_temperatura, acido_ph, acido_pl,
                    enjuague_ph, enjuague_ozono, enjuague_cloro, carbon_cloro_inicial, carbon_cloro_pt, tapas_cloro,
                    observaciones, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha_str, 'Planta_A', hora, 'Nave 1',
                round(random.uniform(7.1, 7.6), 2), round(random.uniform(78.0, 88.0), 1), round(random.uniform(155.0, 175.0), 1),
                round(random.uniform(5.0, 9.0), 1), round(random.uniform(2.8, 3.6), 2), 0.0,
                round(random.uniform(9.8, 10.6), 2), round(random.uniform(0.38, 0.52), 2), round(random.uniform(55.0, 65.0), 1),
                round(random.uniform(2.2, 2.8), 2), round(random.uniform(0.08, 0.15), 2),
                round(random.uniform(6.8, 7.3), 2), round(random.uniform(1.8, 2.4), 2), 0.0,
                round(random.uniform(1.8, 2.2), 2), 0.0, round(random.uniform(1.2, 1.8), 2),
                'Prueba de concentraciones correcta',
                (hoy - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
            ))
            count_lavado += 1

    # 5. Registros de Suavizador
    count_suavizador = 0
    for i in range(15, -1, -1):
        fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
        for suav_num in [1, 2]:
            gotas = round(random.uniform(8.0, 25.0), 1)
            cursor.execute('''
                INSERT INTO registro_suavizador (
                    fecha, numero_suavizador, hora_monitoreo,
                    gotas, inicio, final, tiempo_total, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha_str, suav_num, '10:00',
                gotas, round(random.uniform(0.0, 5.0), 1), round(random.uniform(40.0, 60.0), 1), round(random.uniform(40.0, 55.0), 1),
                (hoy - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
            ))
            count_suavizador += 1

    # 6. Registros de Calidad Pozos
    count_pozos = 0
    for i in range(15, -1, -1):
        fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
        for pozo_num in [1, 2, 3]:
            cond = round(random.uniform(400.0, 520.0), 1)
            cursor.execute('''
                INSERT INTO registro_calidad_pozos (
                    fecha, pozo, hora_monitoreo, conductividad, std, ph, cloro, planta, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha_str, pozo_num, '07:00',
                cond, round(cond * 0.5, 1), round(random.uniform(7.1, 7.7), 2), round(random.uniform(1.0, 1.8), 2), 'Planta_A',
                (hoy - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
            ))
            count_pozos += 1

    # 7. Registros Checklist Filtros y Nave
    count_filtros = 0
    for i in range(15, -1, -1):
        fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
        cursor.execute('''
            INSERT INTO registro_filtros_nave (
                fecha, limpieza_general_cumple, limpieza_general_obs,
                limpieza_profunda_cumple, limpieza_profunda_obs,
                limpieza_otros_cumple, limpieza_otros_obs,
                material_prueba_cumple, material_prueba_obs,
                infraestructura_pintado_cumple, infraestructura_pintado_obs,
                infraestructura_tuberias_cumple, infraestructura_tuberias_obs,
                mantenimiento_calcas_area_cumple, mantenimiento_calcas_area_obs,
                mantenimiento_calcas_lavadora_cumple, mantenimiento_calcas_lavadora_obs,
                documentacion_archivos_cumple, documentacion_archivos_obs,
                documentacion_firmas_cumple, documentacion_firmas_obs,
                firma_ejecuta, firma_responsable, created_at
            ) VALUES (?, 1, 'OK', 1, 'OK', 1, 'OK', 1, 'OK', 1, 'OK', 1, 'OK', 1, 'OK', 1, 'OK', 1, 'OK', 1, 'OK', 'Operador 1', 'Supervisor 1', ?)
        ''', (fecha_str, (hoy - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')))
        count_filtros += 1

    # 8. Registros Ciclos de Suavizador (FALTABA)
    count_ciclos = 0
    for i in range(15, -1, -1):
        fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
        for suav_num in [1, 2]:
            cursor.execute('''
                INSERT INTO registro_ciclos_suavizador (
                    fecha, numero_suavizador, estado,
                    inicio_retrolavado, fin_retrolavado,
                    inicio_regenerado, fin_regenerado,
                    inicio_enjuage_lento, fin_enjuage_lento,
                    inicio_enjuage_rapido, fin_enjuage_rapido,
                    tiempo_total, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha_str, suav_num, 'Completado',
                '08:00', '08:15',
                '08:15', '09:00',
                '09:00', '09:30',
                '09:30', '09:45',
                '1h 45m',
                (hoy - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
            ))
            count_ciclos += 1

    # 9. Registros Ósmosis Vasos - STD y Eficiencia (FALTABA)
    count_vasos = 0
    for i in range(15, -1, -1):
        fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
        for turno in ['Turno 1 (Matutino)', 'Turno 2 (Vespertino)']:
            ent_sdt = round(random.uniform(240.0, 260.0), 1)
            v1 = round(random.uniform(12.0, 18.0), 1)
            v2 = round(random.uniform(10.0, 16.0), 1)
            v3 = round(random.uniform(11.0, 17.0), 1)
            v4 = round(random.uniform(9.0, 15.0), 1)
            v5 = round(random.uniform(8.0, 13.0), 1)
            v_fin = round(random.uniform(7.0, 12.0), 1)
            
            efi1 = round(((ent_sdt - v1) / ent_sdt) * 100.0, 1)
            efi2 = round(((ent_sdt - v2) / ent_sdt) * 100.0, 1)
            efi3 = round(((ent_sdt - v3) / ent_sdt) * 100.0, 1)
            efi4 = round(((ent_sdt - v4) / ent_sdt) * 100.0, 1)
            efi5 = round(((ent_sdt - v5) / ent_sdt) * 100.0, 1)
            efi_fin = round(((ent_sdt - v_fin) / ent_sdt) * 100.0, 1)
            
            cursor.execute('''
                INSERT INTO registro_osmosis_vasos (
                    fecha, turno,
                    sdt_vaso1, efi_vaso1, rango_vaso1,
                    sdt_vaso2, efi_vaso2, rango_vaso2,
                    sdt_vaso3, efi_vaso3, rango_vaso3,
                    sdt_vaso4, efi_vaso4, rango_vaso4,
                    sdt_vaso5, efi_vaso5, rango_vaso5,
                    sdt_final, efi_final, rango_final,
                    sdt_rechazo12, efi_rechazo12, rango_rechazo12,
                    sdt_rechazo3, efi_rechazo3, rango_rechazo3,
                    sdt_rechazo4, efi_rechazo4, rango_rechazo4,
                    sdt_rechazo5, efi_rechazo5, rango_rechazo5,
                    entrada_sdt, entrada_dt, observaciones,
                    firma_jefe_turno_1, firma_jefe_turno_2, firma_subjefe_calidad, firma_jefe_calidad,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha_str, turno,
                v1, efi1, 'Optimo',
                v2, efi2, 'Optimo',
                v3, efi3, 'Optimo',
                v4, efi4, 'Optimo',
                v5, efi5, 'Optimo',
                v_fin, efi_fin, 'Optimo',
                350.0, 92.0, 'Normal',
                360.0, 91.5, 'Normal',
                370.0, 91.0, 'Normal',
                380.0, 90.5, 'Normal',
                ent_sdt, 20.0, 'Funcionamiento normal de vasos',
                'Op1', 'Op2', 'SubJefe', 'JefeCalidad',
                (hoy - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
            ))
            count_vasos += 1

    conn.commit()
    conn.close()
    
    print(f"✅ Éxito: Se generó variedad y dinámica amplia de datos para todas las bitácoras:")
    print(f" - Ósmosis Inversa: {count_osmosis} registros")
    print(f" - Calidad Monitoreo: {count_calidad} registros")
    print(f" - Calidad Lavado: {count_lavado} registros")
    print(f" - Suavizador: {count_suavizador} registros")
    print(f" - Pozos: {count_pozos} registros")
    print(f" - Checklist Filtros Nave: {count_filtros} registros")
    print(f" - Secuencia Ciclos Suavizador: {count_ciclos} registros")
    print(f" - Ósmosis Vasos (S.T.D y Eficiencia): {count_vasos} registros")

if __name__ == '__main__':
    seed_database()
