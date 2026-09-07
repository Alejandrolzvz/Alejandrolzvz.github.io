import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from utils.db import get_db_connection
from utils.decorators import admin_or_super_required

def init_suavizador_routes(app):
    @app.route('/suavizador')
    @login_required
    def suavizador_index():
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_suavizador ORDER BY fecha DESC, id DESC LIMIT 20').fetchall()
        conn.close()
        return render_template('suavizador_index.html', registros=registros)

    @app.route('/nuevo_suavizador', methods=('GET', 'POST'))
    @login_required
    def nuevo_suavizador():
        if request.method == 'POST':
            fecha = request.form.get('fecha', '')
            planta = request.form.get('planta', '')
            numero_suavizador = request.form.get('numero_suavizador', '')
            hora_monitoreo = request.form.get('hora_monitoreo', '')
            gotas = request.form.get('gotas', '')
            inicio = request.form.get('inicio', '')
            final = request.form.get('final', '')
            tiempo_total = request.form.get('tiempo_total', '')

            if not fecha or not hora_monitoreo or not planta:
                flash('La fecha, hora y planta son obligatorias.', 'danger')
            else:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO registro_suavizador (
                        fecha, planta, numero_suavizador, hora_monitoreo, 
                        gotas, inicio, final, tiempo_total, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fecha, planta, numero_suavizador, hora_monitoreo,
                    gotas, inicio, final, tiempo_total,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
                conn.close()
                flash('Registro del Suavizador guardado exitosamente.', 'success')
                return redirect(url_for('suavizador_index'))

        hoy = datetime.now().strftime('%Y-%m-%d')
        return render_template('formulario_suavizador.html', hoy=hoy)

    @app.route('/registro_suavizador/<int:id>')
    @login_required
    def detalle_suavizador(id):
        conn = get_db_connection()
        registro = conn.execute('SELECT * FROM registro_suavizador WHERE id = ?', (id,)).fetchone()
        conn.close()
        
        if registro is None:
            flash('Registro no encontrado.', 'danger')
            return redirect(url_for('suavizador_index'))
            
        return render_template('detalle_suavizador.html', registro=registro)

    @app.route('/exportar_suavizador', methods=['POST'])
    @login_required
    @admin_or_super_required
    def exportar_suavizador():
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            flash('Ambas fechas son obligatorias.', 'warning')
            return redirect(url_for('suavizador_index'))
            
        conn = get_db_connection()
        query = 'SELECT id, fecha, planta, numero_suavizador, hora_monitoreo, gotas, created_at FROM registro_suavizador WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC'
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        
        if df.empty:
            flash(f'No se encontraron registros.', 'info')
            return redirect(url_for('suavizador_index'))
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Suavizador')
        output.seek(0)
        
        filename = f"Suavizador_{fecha_inicio}_a_{fecha_fin}.xlsx"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @app.route('/resumen_suavizador')
    @login_required
    @admin_or_super_required
    def resumen_suavizador():
        fecha_consulta = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        planta_consulta = request.args.get('planta', '')
        
        conn = get_db_connection()
        if planta_consulta:
            registros = conn.execute('SELECT * FROM registro_suavizador WHERE fecha = ? AND planta = ? ORDER BY hora_monitoreo ASC', (fecha_consulta, planta_consulta)).fetchall()
        else:
            registros = conn.execute('SELECT * FROM registro_suavizador WHERE fecha = ? ORDER BY hora_monitoreo ASC', (fecha_consulta,)).fetchall()
        conn.close()
        return render_template('resumen_suavizador.html', registros=registros, fecha_seleccionada=fecha_consulta, planta_seleccionada=planta_consulta)

    @app.route('/dashboard_suavizador')
    @login_required
    @admin_or_super_required
    def dashboard_suavizador():
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = request.args.get('fecha_inicio', hoy)
        fecha_fin = request.args.get('fecha_fin', hoy)
        planta_consulta = request.args.get('planta', '')
        
        conn = get_db_connection()
        if planta_consulta:
            registros = conn.execute(
                'SELECT * FROM registro_suavizador WHERE (fecha BETWEEN ? AND ?) AND planta = ? ORDER BY fecha ASC, hora_monitoreo ASC',
                (fecha_inicio, fecha_fin, planta_consulta)
            ).fetchall()
        else:
            registros = conn.execute(
                'SELECT * FROM registro_suavizador WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, hora_monitoreo ASC',
                (fecha_inicio, fecha_fin)
            ).fetchall()
        conn.close()

        labels_horas = []
        chart_gotas = []
        sum_gotas = 0.0
        valid_gotas = 0

        for r in registros:
            labels_horas.append(f"{r['fecha']} {r['hora_monitoreo']} (S{r['numero_suavizador']})")
            try:
                val = float(r['gotas']) if r['gotas'] else None
            except (ValueError, TypeError):
                val = None
            chart_gotas.append(val)
            if val is not None:
                sum_gotas += val
                valid_gotas += 1

        context = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'planta_seleccionada': planta_consulta,
            'kpi_monitoreos': len(registros),
            'kpi_gotas': round(sum_gotas / valid_gotas, 1) if valid_gotas > 0 else 0,
            'chart_labels': json.dumps(labels_horas),
            'chart_gotas': json.dumps(chart_gotas)
        }
        return render_template('dashboard_suavizador.html', **context)
