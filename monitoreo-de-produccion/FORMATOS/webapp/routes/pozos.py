import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from utils.db import get_db_connection
from utils.decorators import admin_or_super_required

def init_pozos_routes(app):
    @app.route('/pozos')
    @login_required
    def pozos_index():
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_calidad_pozos ORDER BY fecha DESC, id DESC LIMIT 30').fetchall()
        conn.close()
        return render_template('pozos_index.html', registros=registros)

    @app.route('/nuevo_pozos', methods=('GET', 'POST'))
    @login_required
    def nuevo_pozos():
        if request.method == 'POST':
            fecha = request.form.get('fecha', '')
            planta = request.form.get('planta', '')
            pozo = request.form.get('pozo', '')
            hora_monitoreo = request.form.get('hora_monitoreo', '')
            conductividad = request.form.get('conductividad', '')
            std = request.form.get('std', '')
            ph = request.form.get('ph', '')
            cloro = request.form.get('cloro', '')

            if not fecha or not pozo or not hora_monitoreo or not planta:
                flash('La fecha, planta, pozo y hora son campos obligatorios.', 'danger')
            else:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO registro_calidad_pozos (
                        fecha, planta, pozo, hora_monitoreo, 
                        conductividad, std, ph, cloro, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fecha, planta, pozo, hora_monitoreo,
                    conductividad, std, ph, cloro,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
                conn.close()
                flash('Lectura de Pozo guardada exitosamente.', 'success')
                return redirect(url_for('pozos_index'))

        hoy = datetime.now().strftime('%Y-%m-%d')
        return render_template('formulario_pozos.html', hoy=hoy)

    @app.route('/registro_pozos/<int:id>')
    @login_required
    def detalle_pozos(id):
        conn = get_db_connection()
        registro = conn.execute('SELECT * FROM registro_calidad_pozos WHERE id = ?', (id,)).fetchone()
        conn.close()
        
        if registro is None:
            flash('Registro no encontrado.', 'danger')
            return redirect(url_for('pozos_index'))
            
        return render_template('detalle_pozos.html', registro=registro)

    @app.route('/exportar_pozos', methods=['POST'])
    @login_required
    @admin_or_super_required
    def exportar_pozos():
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            flash('Ambas fechas son obligatorias.', 'warning')
            return redirect(url_for('pozos_index'))
            
        conn = get_db_connection()
        query = 'SELECT id, fecha, planta, pozo, hora_monitoreo, conductividad, std, ph, cloro, created_at FROM registro_calidad_pozos WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, pozo ASC, hora_monitoreo ASC'
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        
        if df.empty:
            flash(f'No se encontraron registros.', 'info')
            return redirect(url_for('pozos_index'))
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Calidad_Pozos')
        output.seek(0)
        
        filename = f"Calidad_Pozos_{fecha_inicio}_a_{fecha_fin}.xlsx"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @app.route('/resumen_pozos')
    @login_required
    @admin_or_super_required
    def resumen_pozos():
        fecha_consulta = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        planta_consulta = request.args.get('planta', '')
        
        conn = get_db_connection()
        if planta_consulta:
            registros = conn.execute('SELECT * FROM registro_calidad_pozos WHERE fecha = ? AND planta = ? ORDER BY hora_monitoreo ASC', (fecha_consulta, planta_consulta)).fetchall()
        else:
            registros = conn.execute('SELECT * FROM registro_calidad_pozos WHERE fecha = ? ORDER BY hora_monitoreo ASC', (fecha_consulta,)).fetchall()
        conn.close()
        
        return render_template('resumen_pozos.html', registros=registros, fecha_seleccionada=fecha_consulta, planta_seleccionada=planta_consulta)

    @app.route('/dashboard_pozos')
    @login_required
    @admin_or_super_required
    def dashboard_pozos():
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = request.args.get('fecha_inicio', hoy)
        fecha_fin = request.args.get('fecha_fin', hoy)
        conn = get_db_connection()
        registros = conn.execute(
            'SELECT * FROM registro_calidad_pozos WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, hora_monitoreo ASC',
            (fecha_inicio, fecha_fin)
        ).fetchall()
        conn.close()

        labels_horas = []
        chart_cond, chart_std, chart_ph, chart_cloro = [], [], [], []
        sum_cond, sum_std = 0.0, 0.0
        valid_cond, valid_std = 0, 0

        def safe_float(val):
            try:
                return float(val) if val else None
            except (ValueError, TypeError):
                return None

        for r in registros:
            labels_horas.append(f"{r['fecha']} {r['hora_monitoreo']} (P{r['pozo']})")
            cond = safe_float(r['conductividad'])
            std = safe_float(r['std'])
            ph = safe_float(r['ph'])
            clo = safe_float(r['cloro'])
            chart_cond.append(cond)
            chart_std.append(std)
            chart_ph.append(ph)
            chart_cloro.append(clo)
            if cond is not None:
                sum_cond += cond
                valid_cond += 1
            if std is not None:
                sum_std += std
                valid_std += 1

        context = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'kpi_monitoreos': len(registros),
            'kpi_cond': round(sum_cond / valid_cond, 2) if valid_cond > 0 else 0,
            'kpi_std': round(sum_std / valid_std, 2) if valid_std > 0 else 0,
            'chart_labels': json.dumps(labels_horas),
            'chart_cond': json.dumps(chart_cond),
            'chart_std': json.dumps(chart_std),
            'chart_ph': json.dumps(chart_ph),
            'chart_cloro': json.dumps(chart_cloro)
        }
        return render_template('dashboard_pozos.html', **context)
