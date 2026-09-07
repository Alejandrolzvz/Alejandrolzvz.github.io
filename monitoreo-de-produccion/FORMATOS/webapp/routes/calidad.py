import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from utils.db import get_db_connection
from utils.decorators import admin_or_super_required

def init_calidad_routes(app):
    @app.route('/calidad')
    @login_required
    def calidad_index():
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_calidad_monitoreo ORDER BY fecha DESC, id DESC LIMIT 20').fetchall()
        conn.close()
        return render_template('calidad_index.html', registros=registros)

    @app.route('/nuevo_calidad', methods=('GET', 'POST'))
    @login_required
    def nuevo_calidad():
        if request.method == 'POST':
            fecha = request.form.get('fecha', '')
            planta = request.form.get('planta', '')
            hora_monitoreo = request.form.get('hora_monitoreo', '')
            nave = request.form.get('nave', '')
            c1_cloro = request.form.get('c1_cloro', '')
            c1_ph = request.form.get('c1_ph', '')
            c2_cloro = request.form.get('c2_cloro', '')
            c2_ph = request.form.get('c2_ph', '')
            aduana_cloro = request.form.get('aduana_cloro', '')
            pf_ph = request.form.get('pf_ph', '')
            pf_std = request.form.get('pf_std', '')
            pf_conductividad = request.form.get('pf_conductividad', '')
            pf_dureza = request.form.get('pf_dureza', '')
            pf_ozono = request.form.get('pf_ozono', '')
            pf_cloro = request.form.get('pf_cloro', '')
            lamp1_encendido = request.form.get('lamp1_encendido', '')
            lamp1_hora = request.form.get('lamp1_hora', '')
            lamp2_encendido = request.form.get('lamp2_encendido', '')
            lamp2_hora = request.form.get('lamp2_hora', '')
            observaciones = request.form.get('observaciones', '')

            if not fecha or not hora_monitoreo:
                flash('La fecha y hora son obligatorias.', 'danger')
            else:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO registro_calidad_monitoreo (
                        fecha, planta, hora_monitoreo, nave,
                        c1_cloro, c1_ph, c2_cloro, c2_ph, aduana_cloro,
                        pf_ph, pf_std, pf_conductividad, pf_dureza, pf_ozono, pf_cloro,
                        lamp1_encendido, lamp1_hora, lamp2_encendido, lamp2_hora,
                        observaciones, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fecha, planta, hora_monitoreo, nave,
                    c1_cloro, c1_ph, c2_cloro, c2_ph, aduana_cloro,
                    pf_ph, pf_std, pf_conductividad, pf_dureza, pf_ozono, pf_cloro,
                    lamp1_encendido, lamp1_hora, lamp2_encendido, lamp2_hora,
                    observaciones, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
                conn.close()
                flash('Registro de Calidad guardado exitosamente.', 'success')
                return redirect(url_for('calidad_index'))

        hoy = datetime.now().strftime('%Y-%m-%d')
        return render_template('formulario_calidad.html', hoy=hoy)

    @app.route('/registro_calidad/<int:id>')
    @login_required
    def detalle_calidad(id):
        conn = get_db_connection()
        registro = conn.execute('SELECT * FROM registro_calidad_monitoreo WHERE id = ?', (id,)).fetchone()
        conn.close()
        
        if registro is None:
            flash('Registro no encontrado.', 'danger')
            return redirect(url_for('calidad_index'))
            
        return render_template('detalle_calidad.html', registro=registro)

    @app.route('/exportar_calidad', methods=['POST'])
    @login_required
    @admin_or_super_required
    def exportar_calidad():
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            flash('Ambas fechas son obligatorias.', 'warning')
            return redirect(url_for('calidad_index'))
            
        conn = get_db_connection()
        query = 'SELECT * FROM registro_calidad_monitoreo WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC'
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        
        if df.empty:
            flash(f'No se encontraron registros.', 'info')
            return redirect(url_for('calidad_index'))
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Calidad')
        output.seek(0)
        
        filename = f"Calidad_Monitoreo_{fecha_inicio}_a_{fecha_fin}.xlsx"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @app.route('/resumen_calidad')
    @login_required
    @admin_or_super_required
    def resumen_calidad():
        fecha_consulta = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_calidad_monitoreo WHERE fecha = ? ORDER BY hora_monitoreo ASC', (fecha_consulta,)).fetchall()
        conn.close()
        return render_template('resumen_calidad.html', registros=registros, fecha_seleccionada=fecha_consulta)

    @app.route('/dashboard_calidad')
    @login_required
    @admin_or_super_required
    def dashboard_calidad():
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = request.args.get('fecha_inicio', hoy)
        fecha_fin = request.args.get('fecha_fin', hoy)
        conn = get_db_connection()
        registros = conn.execute(
            'SELECT * FROM registro_calidad_monitoreo WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, hora_monitoreo ASC',
            (fecha_inicio, fecha_fin)
        ).fetchall()
        conn.close()

        labels_horas = []
        chart_pf_ph, chart_pf_conductividad, chart_pf_dureza, chart_pf_cloro = [], [], [], []
        sum_ph, sum_dureza, sum_cloro = 0.0, 0.0, 0.0
        valid_ph, valid_dureza, valid_cloro = 0, 0, 0

        def safe_float(val):
            try:
                return float(val) if val else None
            except (ValueError, TypeError):
                return None

        for r in registros:
            labels_horas.append(f"{r['fecha']} {r['hora_monitoreo']}")
            ph = safe_float(r['pf_ph'])
            cond = safe_float(r['pf_conductividad'])
            dur = safe_float(r['pf_dureza'])
            clo = safe_float(r['pf_cloro'])
            chart_pf_ph.append(ph)
            chart_pf_conductividad.append(cond)
            chart_pf_dureza.append(dur)
            chart_pf_cloro.append(clo)
            if ph is not None:
                sum_ph += ph
                valid_ph += 1
            if dur is not None:
                sum_dureza += dur
                valid_dureza += 1
            if clo is not None:
                sum_cloro += clo
                valid_cloro += 1

        context = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'kpi_monitoreos': len(registros),
            'kpi_ph': round(sum_ph / valid_ph, 2) if valid_ph > 0 else 0,
            'kpi_dureza': round(sum_dureza / valid_dureza, 2) if valid_dureza > 0 else 0,
            'kpi_cloro': round(sum_cloro / valid_cloro, 2) if valid_cloro > 0 else 0,
            'chart_labels': json.dumps(labels_horas),
            'chart_ph': json.dumps(chart_pf_ph),
            'chart_conductividad': json.dumps(chart_pf_conductividad),
            'chart_dureza': json.dumps(chart_pf_dureza),
            'chart_cloro': json.dumps(chart_pf_cloro)
        }
        return render_template('dashboard_calidad.html', **context)
