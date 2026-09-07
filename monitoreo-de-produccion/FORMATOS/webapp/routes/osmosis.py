import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from utils.db import get_db_connection
from utils.decorators import admin_or_super_required

def init_osmosis_routes(app):
    @app.route('/osmosis')
    @login_required
    def osmosis_index():
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_osmosis ORDER BY fecha DESC, id DESC LIMIT 20').fetchall()
        conn.close()
        return render_template('osmosis_index.html', registros=registros)

    @app.route('/nuevo_registro', methods=('GET', 'POST'))
    @login_required
    def nuevo_registro():
        if request.method == 'POST':
            # Capturamos todos los datos del formulario
            fecha = request.form.get('fecha', '')
            planta = request.form.get('planta', '')
            hora_monitoreo = request.form.get('hora_monitoreo', '')
            
            estatus_equipo = request.form.get('estatus_equipo', '')
            
            presion_arranque = request.form.get('presion_arranque', '')
            presion_agua_cruda = request.form.get('presion_agua_cruda', '')
            presion_pre_filtracion = request.form.get('presion_pre_filtracion', '')
            presion_post_filtracion = request.form.get('presion_post_filtracion', '')
            presion_pre_membranas = request.form.get('presion_pre_membranas', '')
            presion_post_membranas = request.form.get('presion_post_membranas', '')
            presion_bombas = request.form.get('presion_bombas', '')
            
            rotametro_productos = request.form.get('rotametro_productos', '')
            rotametro_rechazo = request.form.get('rotametro_rechazo', '')
            
            sensor_ph = request.form.get('sensor_ph', '')
            sensor_std = request.form.get('sensor_std', '')
            
            amperimetro = request.form.get('amperimetro', '')
            horometro = request.form.get('horometro', '')
            
            filtro_arena = request.form.get('filtro_arena', '')
            filtro_carbon = request.form.get('filtro_carbon', '')
            suavizador_num = request.form.get('suavizador_num', '')
            entrada_suavizador = request.form.get('entrada_suavizador', '')
            salida_suavizador = request.form.get('salida_suavizador', '')
            observaciones = request.form.get('observaciones', '')

            if not fecha or not hora_monitoreo:
                flash('La fecha y hora de monitoreo son obligatorias.', 'danger')
            else:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO registro_osmosis (
                        fecha, planta, hora_monitoreo, estatus_equipo,
                        presion_arranque, presion_agua_cruda, presion_pre_filtracion, presion_post_filtracion,
                        presion_pre_membranas, presion_post_membranas, presion_bombas,
                        rotametro_productos, rotametro_rechazo,
                        sensor_ph, sensor_std,
                        amperimetro, horometro,
                        filtro_arena, filtro_carbon, suavizador_num, entrada_suavizador, salida_suavizador,
                        observaciones, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fecha, planta, hora_monitoreo, estatus_equipo,
                    presion_arranque, presion_agua_cruda, presion_pre_filtracion, presion_post_filtracion,
                    presion_pre_membranas, presion_post_membranas, presion_bombas,
                    rotametro_productos, rotametro_rechazo,
                    sensor_ph, sensor_std,
                    amperimetro, horometro,
                    filtro_arena, filtro_carbon, suavizador_num, entrada_suavizador, salida_suavizador,
                    observaciones, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
                conn.close()
                flash('Registro de Ósmosis guardado exitosamente.', 'success')
                return redirect(url_for('osmosis_index'))

        # Si es GET, prelenamos con la fecha de hoy
        hoy = datetime.now().strftime('%Y-%m-%d')
        return render_template('formulario.html', hoy=hoy)

    @app.route('/registro/<int:id>')
    @login_required
    def ver_detalle(id):
        conn = get_db_connection()
        registro = conn.execute('SELECT * FROM registro_osmosis WHERE id = ?', (id,)).fetchone()
        conn.close()
        
        if registro is None:
            flash('El registro no fue encontrado.', 'danger')
            return redirect(url_for('osmosis_index'))
            
        return render_template('detalle.html', registro=registro)

    @app.route('/resumen_diario')
    @login_required
    @admin_or_super_required
    def resumen_diario():
        # Obtener fecha de la URL (querystring) o usar la fecha actual
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_consulta = request.args.get('fecha', hoy)
        
        conn = get_db_connection()
        # Obtenemos todos los registros de la fecha dada, ordenados por hora
        registros = conn.execute(
            'SELECT * FROM registro_osmosis WHERE fecha = ? ORDER BY id ASC',
            (fecha_consulta,)
        ).fetchall()
        conn.close()
        
        return render_template('resumen.html', registros=registros, fecha_seleccionada=fecha_consulta)

    @app.route('/exportar_excel', methods=['POST'])
    @login_required
    @admin_or_super_required
    def exportar_excel():
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            flash('Ambas fechas son obligatorias.', 'warning')
            return redirect(url_for('osmosis_index'))
            
        conn = get_db_connection()
        # Leer a DataFrame
        query = 'SELECT * FROM registro_osmosis WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC'
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        
        if df.empty:
            flash(f'No se encontraron registros entre {fecha_inicio} y {fecha_fin}.', 'info')
            return redirect(url_for('osmosis_index'))
        
        # Limpiamos u ordenamos un poco las columnas si se desea, o lo arrojamos directo.
        # Por temas prácticos, arrojamos todas las columnas capturadas:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Registros')
        
        output.seek(0)
        
        filename = f"Registros_Osmosis_{fecha_inicio}_a_{fecha_fin}.xlsx"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @app.route('/dashboard')
    @login_required
    @admin_or_super_required
    def dashboard():
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = request.args.get('fecha_inicio', hoy)
        fecha_fin = request.args.get('fecha_fin', hoy)

        conn = get_db_connection()
        registros = conn.execute(
            'SELECT * FROM registro_osmosis WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC',
            (fecha_inicio, fecha_fin)
        ).fetchall()
        conn.close()

        lecturas_encendido = [r for r in registros if r['estatus_equipo'] == 'Encendido']

        rechazo_sales_promedio = 0.0
        recuperacion_promedio = 0.0
        delta_p_promedio = 0.0

        list_rechazos = []
        list_recup = []
        list_delta_p = []

        labels_horas = []
        chart_rechazo = []
        chart_recuperacion = []
        chart_flujo_prod = []
        chart_flujo_rechazo = []
        chart_delta_p = []

        for r in registros:
            labels_horas.append(f"{r['fecha']} {r['hora_monitoreo']}")

            if r['estatus_equipo'] == 'Encendido':
                try:
                    sdt_in = float(r['entrada_osmosis_sdt']) if r['entrada_osmosis_sdt'] else 0.0
                    sdt_out = float(r['sdt_final']) if r['sdt_final'] else 0.0
                    if sdt_in > 0:
                        rech = ((sdt_in - sdt_out) / sdt_in) * 100.0
                        list_rechazos.append(rech)
                        chart_rechazo.append(round(rech, 2))
                    else:
                        chart_rechazo.append(None)
                except (ValueError, TypeError):
                    chart_rechazo.append(None)

                try:
                    prod = float(r['rotametro_productos']) if r['rotametro_productos'] else 0.0
                    rechazo_flujo = float(r['rotametro_rechazo']) if r['rotametro_rechazo'] else 0.0
                    chart_flujo_prod.append(prod)
                    chart_flujo_rechazo.append(rechazo_flujo)
                    if (prod + rechazo_flujo) > 0:
                        rec = (prod / (prod + rechazo_flujo)) * 100.0
                        list_recup.append(rec)
                        chart_recuperacion.append(round(rec, 2))
                    else:
                        chart_recuperacion.append(None)
                except (ValueError, TypeError):
                    chart_flujo_prod.append(None)
                    chart_flujo_rechazo.append(None)
                    chart_recuperacion.append(None)

                try:
                    pre_m = float(r['presion_pre_membranas']) if r['presion_pre_membranas'] else 0.0
                    post_m = float(r['presion_post_membranas']) if r['presion_post_membranas'] else 0.0
                    if pre_m > 0 and post_m > 0:
                        dp = pre_m - post_m
                        list_delta_p.append(dp)
                        chart_delta_p.append(round(dp, 2))
                    else:
                        chart_delta_p.append(None)
                except (ValueError, TypeError):
                    chart_delta_p.append(None)
            else:
                chart_rechazo.append(None)
                chart_recuperacion.append(None)
                chart_flujo_prod.append(None)
                chart_flujo_rechazo.append(None)
                chart_delta_p.append(None)

        if list_rechazos:
            rechazo_sales_promedio = round(float(sum(list_rechazos) / len(list_rechazos)), 2)
        if list_recup:
            recuperacion_promedio = round(float(sum(list_recup) / len(list_recup)), 2)
        if list_delta_p:
            delta_p_promedio = round(float(sum(list_delta_p) / len(list_delta_p)), 2)

        context = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'kpi_horas': len(lecturas_encendido),
            'kpi_rechazo': rechazo_sales_promedio,
            'kpi_recuperacion': recuperacion_promedio,
            'kpi_deltap': delta_p_promedio,
            'chart_labels': json.dumps(labels_horas),
            'chart_rechazo': json.dumps(chart_rechazo),
            'chart_recuperacion': json.dumps(chart_recuperacion),
            'chart_flujo_prod': json.dumps(chart_flujo_prod),
            'chart_flujo_rechazo': json.dumps(chart_flujo_rechazo),
            'chart_delta_p': json.dumps(chart_delta_p)
        }

        return render_template('dashboard.html', **context)
