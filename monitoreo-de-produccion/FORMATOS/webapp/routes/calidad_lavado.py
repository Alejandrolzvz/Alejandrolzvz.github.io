import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from utils.db import get_db_connection
from utils.decorators import admin_or_super_required

def init_calidad_lavado_routes(app):
    @app.route('/calidad_lavado')
    @login_required
    def calidad_lavado_index():
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_calidad_lavado ORDER BY fecha DESC, id DESC LIMIT 20').fetchall()
        conn.close()
        return render_template('calidad_lavado_index.html', registros=registros)

    @app.route('/nuevo_calidad_lavado', methods=('GET', 'POST'))
    @login_required
    def nuevo_calidad_lavado():
        if request.method == 'POST':
            fecha = request.form.get('fecha', '')
            planta = request.form.get('planta', '')
            hora_monitoreo = request.form.get('hora_monitoreo', '')
            nave = request.form.get('nave', '')
            
            tanque_ph = request.form.get('tanque_ph', '')
            tanque_std = request.form.get('tanque_std', '')
            tanque_conductividad = request.form.get('tanque_conductividad', '')
            tanque_dureza = request.form.get('tanque_dureza', '')
            tanque_ozono = request.form.get('tanque_ozono', '')
            tanque_cloro = request.form.get('tanque_cloro', '')
            
            alcalino_ph = request.form.get('alcalino_ph', '')
            alcalino_g3 = request.form.get('alcalino_g3', '')
            alcalino_temperatura = request.form.get('alcalino_temperatura', '')
            acido_ph = request.form.get('acido_ph', '')
            acido_pl = request.form.get('acido_pl', '')
            enjuague_ph = request.form.get('enjuague_ph', '')
            enjuague_ozono = request.form.get('enjuague_ozono', '')
            enjuague_cloro = request.form.get('enjuague_cloro', '')
            carbon_cloro_inicial = request.form.get('carbon_cloro_inicial', '')
            carbon_cloro_pt = request.form.get('carbon_cloro_pt', '')
            tapas_cloro = request.form.get('tapas_cloro', '')
            
            observaciones = request.form.get('observaciones', '')

            if not fecha or not hora_monitoreo:
                flash('La fecha y hora son obligatorias.', 'danger')
            else:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO registro_calidad_lavado (
                        fecha, planta, hora_monitoreo, nave,
                        tanque_ph, tanque_std, tanque_conductividad, tanque_dureza, tanque_ozono, tanque_cloro,
                        alcalino_ph, alcalino_g3, alcalino_temperatura, acido_ph, acido_pl, enjuague_ph, enjuague_ozono, enjuague_cloro,
                        carbon_cloro_inicial, carbon_cloro_pt, tapas_cloro, observaciones, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fecha, planta, hora_monitoreo, nave,
                    tanque_ph, tanque_std, tanque_conductividad, tanque_dureza, tanque_ozono, tanque_cloro,
                    alcalino_ph, alcalino_g3, alcalino_temperatura, acido_ph, acido_pl, enjuague_ph, enjuague_ozono, enjuague_cloro,
                    carbon_cloro_inicial, carbon_cloro_pt, tapas_cloro, observaciones, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
                conn.close()
                flash('Registro de Calidad (Tanque y Lavado) guardado exitosamente.', 'success')
                return redirect(url_for('calidad_lavado_index'))

        hoy = datetime.now().strftime('%Y-%m-%d')
        return render_template('formulario_calidad_lavado.html', hoy=hoy)

    @app.route('/registro_calidad_lavado/<int:id>')
    @login_required
    def detalle_calidad_lavado(id):
        conn = get_db_connection()
        registro = conn.execute('SELECT * FROM registro_calidad_lavado WHERE id = ?', (id,)).fetchone()
        conn.close()
        
        if registro is None:
            flash('Registro no encontrado.', 'danger')
            return redirect(url_for('calidad_lavado_index'))
            
        return render_template('detalle_calidad_lavado.html', registro=registro)

    @app.route('/exportar_calidad_lavado', methods=['POST'])
    @login_required
    @admin_or_super_required
    def exportar_calidad_lavado():
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            flash('Ambas fechas son obligatorias.', 'warning')
            return redirect(url_for('calidad_lavado_index'))
            
        conn = get_db_connection()
        query = 'SELECT * FROM registro_calidad_lavado WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC'
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        
        if df.empty:
            flash(f'No se encontraron registros.', 'info')
            return redirect(url_for('calidad_lavado_index'))
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Calidad Lavado')
        output.seek(0)
        
        filename = f"Calidad_Lavado_{fecha_inicio}_a_{fecha_fin}.xlsx"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @app.route('/resumen_calidad_lavado')
    @login_required
    @admin_or_super_required
    def resumen_calidad_lavado():
        fecha_consulta = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_calidad_lavado WHERE fecha = ? ORDER BY hora_monitoreo ASC', (fecha_consulta,)).fetchall()
        conn.close()
        return render_template('resumen_calidad_lavado.html', registros=registros, fecha_seleccionada=fecha_consulta)

    @app.route('/dashboard_calidad_lavado')
    @login_required
    @admin_or_super_required
    def dashboard_calidad_lavado():
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = request.args.get('fecha_inicio', hoy)
        fecha_fin = request.args.get('fecha_fin', hoy)
        conn = get_db_connection()
        registros = conn.execute(
            'SELECT * FROM registro_calidad_lavado WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, hora_monitoreo ASC',
            (fecha_inicio, fecha_fin)
        ).fetchall()
        conn.close()

        labels_horas = []
        chart_tanque_ph, chart_tanque_conductividad, chart_tanque_cloro = [], [], []
        sum_ph, sum_cond, sum_cloro = 0.0, 0.0, 0.0
        valid_ph, valid_cond, valid_cloro = 0, 0, 0

        def safe_float(val):
            try:
                return float(val) if val else None
            except (ValueError, TypeError):
                return None

        for r in registros:
            labels_horas.append(f"{r['fecha']} {r['hora_monitoreo']}")
            ph = safe_float(r['tanque_ph'])
            cond = safe_float(r['tanque_conductividad'])
            clo = safe_float(r['tanque_cloro'])
            
            chart_tanque_ph.append(ph)
            chart_tanque_conductividad.append(cond)
            chart_tanque_cloro.append(clo)
            
            if ph is not None:
                sum_ph += ph
                valid_ph += 1
            if cond is not None:
                sum_cond += cond
                valid_cond += 1
            if clo is not None:
                sum_cloro += clo
                valid_cloro += 1

        context = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'kpi_monitoreos': len(registros),
            'kpi_ph': round(sum_ph / valid_ph, 2) if valid_ph > 0 else 0,
            'kpi_cond': round(sum_cond / valid_cond, 2) if valid_cond > 0 else 0,
            'kpi_cloro': round(sum_cloro / valid_cloro, 2) if valid_cloro > 0 else 0,
            'chart_labels': json.dumps(labels_horas),
            'chart_ph': json.dumps(chart_tanque_ph),
            'chart_conductividad': json.dumps(chart_tanque_conductividad),
            'chart_cloro': json.dumps(chart_tanque_cloro)
        }
        return render_template('dashboard_calidad_lavado.html', **context)
