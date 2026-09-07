import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from utils.db import get_db_connection
from utils.decorators import admin_or_super_required

def calcular_duracion(inicio, fin):
    if not inicio or not fin:
        return ""
    try:
        t1 = datetime.strptime(inicio, '%H:%M')
        t2 = datetime.strptime(fin, '%H:%M')
        diff = (t2 - t1).total_seconds() / 60
        if diff < 0:
            diff += 24 * 60
        return f"{int(diff)} min"
    except (ValueError, TypeError):
        return ""

def init_ciclos_suavizador_routes(app):
    
    @app.route('/ciclos_suavizador')
    @login_required
    def ciclos_index():
        conn = get_db_connection()
        registros_raw = conn.execute('SELECT * FROM registro_ciclos_suavizador ORDER BY id DESC LIMIT 20').fetchall()
        conn.close()
        
        registros = []
        for r in registros_raw:
            reg = dict(r)
            reg['duracion_retrolavado'] = calcular_duracion(reg.get('inicio_retrolavado'), reg.get('fin_retrolavado'))
            reg['duracion_regenerado'] = calcular_duracion(reg.get('inicio_regenerado'), reg.get('fin_regenerado'))
            reg['duracion_enjuage_lento'] = calcular_duracion(reg.get('inicio_enjuage_lento'), reg.get('fin_enjuage_lento'))
            reg['duracion_enjuage_rapido'] = calcular_duracion(reg.get('inicio_enjuage_rapido'), reg.get('fin_enjuage_rapido'))
            registros.append(reg)
            
        return render_template('ciclos_index.html', registros=registros)

    @app.route('/continuar_ciclo', methods=['GET', 'POST'])
    @login_required
    def continuar_ciclo():
        # Cuando abrimos el formulario
        if request.method == 'GET':
            suavizador_id = request.args.get('numero_suavizador')
            planta = request.args.get('planta')
            fecha_str = datetime.now().strftime('%Y-%m-%d')
            
            # Si no ha seleccionado suavizador o planta, lo mandamos al selector
            if not suavizador_id or not planta:
                return render_template('ciclos_selector.html', hoy=fecha_str)

            conn = get_db_connection()
            # Buscar el ciclo activo (pendiente) sin importar la fecha en la que inició
            ciclo = conn.execute(
                "SELECT * FROM registro_ciclos_suavizador WHERE numero_suavizador = ? AND planta = ? AND estado = 'En progreso'",
                (suavizador_id, planta)
            ).fetchone()
            conn.close()
            
            return render_template('formulario_ciclos.html', hoy=fecha_str, suavizador_id=suavizador_id, planta=planta, ciclo=ciclo)

        # POST
        fecha = request.form.get('fecha')
        suavizador_id = request.form.get('numero_suavizador')
        planta = request.form.get('planta')
        
        inicio_retrolavado = request.form.get('inicio_retrolavado')
        fin_retrolavado = request.form.get('fin_retrolavado')
        
        inicio_regenerado = request.form.get('inicio_regenerado')
        fin_regenerado = request.form.get('fin_regenerado')
        
        inicio_enjuage_lento = request.form.get('inicio_enjuage_lento')
        fin_enjuage_lento = request.form.get('fin_enjuage_lento')
        
        inicio_enjuage_rapido = request.form.get('inicio_enjuage_rapido')
        fin_enjuage_rapido = request.form.get('fin_enjuage_rapido')
        
        tiempo_total = request.form.get('tiempo_total', '')

        estado = "En progreso"
        if fin_enjuage_rapido and tiempo_total:
            estado = "Completado"

        conn = get_db_connection()
        ciclo = conn.execute(
            "SELECT id FROM registro_ciclos_suavizador WHERE numero_suavizador = ? AND planta = ? AND estado = 'En progreso'",
            (suavizador_id, planta)
        ).fetchone()

        if ciclo:
            # Update existente
            conn.execute('''
                UPDATE registro_ciclos_suavizador SET
                inicio_retrolavado = ?, fin_retrolavado = ?,
                inicio_regenerado = ?, fin_regenerado = ?,
                inicio_enjuage_lento = ?, fin_enjuage_lento = ?,
                inicio_enjuage_rapido = ?, fin_enjuage_rapido = ?,
                tiempo_total = ?, estado = ?
                WHERE id = ?
            ''', (
                inicio_retrolavado, fin_retrolavado,
                inicio_regenerado, fin_regenerado,
                inicio_enjuage_lento, fin_enjuage_lento,
                inicio_enjuage_rapido, fin_enjuage_rapido,
                tiempo_total, estado,
                ciclo['id']
            ))
            mensaje = "Avance del ciclo guardado en progreso."
            if estado == "Completado":
                mensaje = "¡Ciclo completado exitosamente!"
            flash(mensaje, 'success')
        else:
            # Crear nuevo si no existía activo
            conn.execute('''
                INSERT INTO registro_ciclos_suavizador (
                    fecha, numero_suavizador, planta, estado,
                    inicio_retrolavado, fin_retrolavado,
                    inicio_regenerado, fin_regenerado,
                    inicio_enjuage_lento, fin_enjuage_lento,
                    inicio_enjuage_rapido, fin_enjuage_rapido,
                    tiempo_total, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fecha, suavizador_id, planta, estado,
                inicio_retrolavado, fin_retrolavado,
                inicio_regenerado, fin_regenerado,
                inicio_enjuage_lento, fin_enjuage_lento,
                inicio_enjuage_rapido, fin_enjuage_rapido,
                tiempo_total, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            flash('Nuevo ciclo de suavizador iniciado.', 'success')
            
        conn.commit()
        conn.close()
        return redirect(url_for('ciclos_index'))

    @app.route('/detalle_ciclo/<int:id>')
    @login_required
    def detalle_ciclos(id):
        conn = get_db_connection()
        registro = conn.execute('SELECT * FROM registro_ciclos_suavizador WHERE id = ?', (id,)).fetchone()
        conn.close()
        if registro is None:
            flash('Ciclo no encontrado.', 'danger')
            return redirect(url_for('ciclos_index'))
        return render_template('detalle_ciclos.html', registro=registro)

    @app.route('/exportar_ciclos', methods=['POST'])
    @login_required
    @admin_or_super_required
    def exportar_ciclos():
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        if not fecha_inicio or not fecha_fin:
            flash('Ambas fechas son obligatorias.', 'warning')
            return redirect(url_for('ciclos_index'))
            
        conn = get_db_connection()
        query = 'SELECT * FROM registro_ciclos_suavizador WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC'
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        
        if df.empty:
            flash('No se encontraron ciclos para este rango de fechas.', 'info')
            return redirect(url_for('ciclos_index'))
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Ciclos')
        output.seek(0)
        
        filename = f"Ciclos_Suavizador_{fecha_inicio}_a_{fecha_fin}.xlsx"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @app.route('/resumen_ciclos')
    @login_required
    @admin_or_super_required
    def resumen_ciclos():
        fecha_consulta = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        planta_consulta = request.args.get('planta', '')
        
        conn = get_db_connection()
        if planta_consulta:
            registros = conn.execute('SELECT * FROM registro_ciclos_suavizador WHERE fecha = ? AND planta = ? ORDER BY numero_suavizador ASC, id ASC', (fecha_consulta, planta_consulta)).fetchall()
        else:
            registros = conn.execute('SELECT * FROM registro_ciclos_suavizador WHERE fecha = ? ORDER BY numero_suavizador ASC, id ASC', (fecha_consulta,)).fetchall()
        conn.close()
        
        return render_template('resumen_ciclos.html', registros=registros, fecha_seleccionada=fecha_consulta, planta_seleccionada=planta_consulta)

    @app.route('/dashboard_ciclos')
    @login_required
    @admin_or_super_required
    def dashboard_ciclos():
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = request.args.get('fecha_inicio', hoy)
        fecha_fin = request.args.get('fecha_fin', hoy)

        conn = get_db_connection()
        registros_raw = conn.execute(
            'SELECT * FROM registro_ciclos_suavizador WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC',
            (fecha_inicio, fecha_fin)
        ).fetchall()
        conn.close()

        ciclos_completados = [r for r in registros_raw if r['estado'] == 'Completado']

        t_retrolavado = []
        t_regenerado = []
        t_enjuage_lento = []
        t_enjuage_rapido = []
        t_total = []

        labels_ciclos = []
        chart_retrolavado = []
        chart_regenerado = []
        chart_enjuage_lento = []
        chart_enjuage_rapido = []
        chart_total = []

        def get_mins(inicio, fin):
            if not inicio or not fin:
                return 0
            try:
                t1 = datetime.strptime(inicio, '%H:%M')
                t2 = datetime.strptime(fin, '%H:%M')
                diff = (t2 - t1).total_seconds() / 60
                if diff < 0:
                    diff += 24 * 60
                return int(diff)
            except (ValueError, TypeError):
                return 0

        for r in ciclos_completados:
            planta_val = r['planta'] if 'planta' in r.keys() and r['planta'] else ""
            planta_str = f" ({planta_val})" if planta_val else ""
            labels_ciclos.append(f"{r['fecha']} S{r['numero_suavizador']}{planta_str}")

            m_retro = get_mins(r['inicio_retrolavado'], r['fin_retrolavado'])
            m_regen = get_mins(r['inicio_regenerado'], r['fin_regenerado'])
            m_lento = get_mins(r['inicio_enjuage_lento'], r['fin_enjuage_lento'])
            m_rapido = get_mins(r['inicio_enjuage_rapido'], r['fin_enjuage_rapido'])
            m_total = m_retro + m_regen + m_lento + m_rapido
            
            t_retrolavado.append(m_retro)
            t_regenerado.append(m_regen)
            t_enjuage_lento.append(m_lento)
            t_enjuage_rapido.append(m_rapido)
            t_total.append(m_total)

            chart_retrolavado.append(m_retro)
            chart_regenerado.append(m_regen)
            chart_enjuage_lento.append(m_lento)
            chart_enjuage_rapido.append(m_rapido)
            chart_total.append(m_total)

        avg_retro = round(sum(t_retrolavado) / len(t_retrolavado), 1) if t_retrolavado else 0.0
        avg_regen = round(sum(t_regenerado) / len(t_regenerado), 1) if t_regenerado else 0.0
        avg_total = round(sum(t_total) / len(t_total), 1) if t_total else 0.0

        context = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'kpi_ciclos': len(ciclos_completados),
            'kpi_avg_total': avg_total,
            'kpi_avg_retro': avg_retro,
            'kpi_avg_regen': avg_regen,
            'chart_labels': json.dumps(labels_ciclos),
            'chart_retro': json.dumps(chart_retrolavado),
            'chart_regen': json.dumps(chart_regenerado),
            'chart_lento': json.dumps(chart_enjuage_lento),
            'chart_rapido': json.dumps(chart_enjuage_rapido),
            'chart_total': json.dumps(chart_total)
        }

        return render_template('dashboard_ciclos.html', **context)
