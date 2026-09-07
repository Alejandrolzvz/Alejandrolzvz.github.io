from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from utils.db import get_db_connection
from utils.decorators import admin_or_super_required

def init_osmosis_vasos_routes(app):
    @app.route('/osmosis_vasos')
    @login_required
    def osmosis_vasos_index():
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_osmosis_vasos ORDER BY fecha DESC, id DESC LIMIT 20').fetchall()
        conn.close()
        return render_template('osmosis_vasos_index.html', registros=registros)

    @app.route('/nuevo_registro_osmosis_vasos', methods=('GET', 'POST'))
    @login_required
    def nuevo_registro_osmosis_vasos():
        if request.method == 'POST':
            fecha = request.form.get('fecha', '')
            turno = request.form.get('turno', '')
            planta = request.form.get('planta', '')
            
            sdt_vaso1 = request.form.get('sdt_vaso1', '')
            efi_vaso1 = request.form.get('efi_vaso1', '')
            rango_vaso1 = request.form.get('rango_vaso1', '100-90')
            
            sdt_vaso2 = request.form.get('sdt_vaso2', '')
            efi_vaso2 = request.form.get('efi_vaso2', '')
            rango_vaso2 = request.form.get('rango_vaso2', '100-90')
            
            sdt_vaso3 = request.form.get('sdt_vaso3', '')
            efi_vaso3 = request.form.get('efi_vaso3', '')
            rango_vaso3 = request.form.get('rango_vaso3', '100-90')
            
            sdt_vaso4 = request.form.get('sdt_vaso4', '')
            efi_vaso4 = request.form.get('efi_vaso4', '')
            rango_vaso4 = request.form.get('rango_vaso4', '100-90')
            
            sdt_vaso5 = request.form.get('sdt_vaso5', '')
            efi_vaso5 = request.form.get('efi_vaso5', '')
            rango_vaso5 = request.form.get('rango_vaso5', '100-90')
            
            sdt_final = request.form.get('sdt_final', '')
            efi_final = request.form.get('efi_final', '')
            rango_final = request.form.get('rango_final', '100-90')
            
            sdt_rechazo12 = request.form.get('sdt_rechazo12', '')
            sdt_rechazo3 = request.form.get('sdt_rechazo3', '')
            sdt_rechazo4 = request.form.get('sdt_rechazo4', '')
            sdt_rechazo5 = request.form.get('sdt_rechazo5', '')
            
            entrada_sdt = request.form.get('entrada_sdt', '')
            entrada_dt = request.form.get('entrada_dt', '')
            
            observaciones = request.form.get('observaciones', '')
            
            firma_jefe_turno_1 = request.form.get('firma_jefe_turno_1', '')
            firma_jefe_turno_2 = request.form.get('firma_jefe_turno_2', '')
            firma_subjefe_calidad = request.form.get('firma_subjefe_calidad', '')
            firma_jefe_calidad = request.form.get('firma_jefe_calidad', '')

            if not fecha or not turno or not planta:
                flash('La fecha, la planta y turno son obligatorios.', 'danger')
            else:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO registro_osmosis_vasos (
                        fecha, turno, planta,
                        sdt_vaso1, efi_vaso1, rango_vaso1,
                        sdt_vaso2, efi_vaso2, rango_vaso2,
                        sdt_vaso3, efi_vaso3, rango_vaso3,
                        sdt_vaso4, efi_vaso4, rango_vaso4,
                        sdt_vaso5, efi_vaso5, rango_vaso5,
                        sdt_final, efi_final, rango_final,
                        sdt_rechazo12, sdt_rechazo3, sdt_rechazo4, sdt_rechazo5,
                        entrada_sdt, entrada_dt,
                        observaciones, 
                        firma_jefe_turno_1, firma_jefe_turno_2, firma_subjefe_calidad, firma_jefe_calidad,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fecha, turno, planta,
                    sdt_vaso1, efi_vaso1, rango_vaso1,
                    sdt_vaso2, efi_vaso2, rango_vaso2,
                    sdt_vaso3, efi_vaso3, rango_vaso3,
                    sdt_vaso4, efi_vaso4, rango_vaso4,
                    sdt_vaso5, efi_vaso5, rango_vaso5,
                    sdt_final, efi_final, rango_final,
                    sdt_rechazo12, sdt_rechazo3, sdt_rechazo4, sdt_rechazo5,
                    entrada_sdt, entrada_dt,
                    observaciones,
                    firma_jefe_turno_1, firma_jefe_turno_2, firma_subjefe_calidad, firma_jefe_calidad,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
                conn.close()
                flash('Registro de Ósmosis Vasos guardado exitosamente.', 'success')
                return redirect(url_for('osmosis_vasos_index'))

        hoy = datetime.now().strftime('%Y-%m-%d')
        return render_template('formulario_osmosis_vasos.html', hoy=hoy)

    @app.route('/resumen_diario_osmosis_vasos')
    @login_required
    @admin_or_super_required
    def resumen_diario_osmosis_vasos():
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_consulta = request.args.get('fecha', hoy)
        planta_consulta = request.args.get('planta', 'Planta_A')
        
        conn = get_db_connection()
        registros_crudos = conn.execute(
            'SELECT * FROM registro_osmosis_vasos WHERE fecha = ? AND planta = ? ORDER BY id ASC',
            (fecha_consulta, planta_consulta)
        ).fetchall()
        conn.close()

        # Organize by turno to display correctly in the table template
        # The expected turnos: 1 ("6:00 A.M. a 10:00 A.M."), 2 ("11:00 A.M. a 3:00 P.M."), 3 ("4:00 P.M. a 8:00 P.M.")
        turnos = {
            "6:00 A.M. a 10:00 A.M.": None,
            "11:00 A.M. a 3:00 P.M.": None,
            "4:00 P.M. a 8:00 P.M.": None
        }
        
        # Grab the latest observations and signatures
        observaciones_global = ""
        firma1 = ""
        firma2 = ""
        firma3 = ""
        firma4 = ""
        
        for reg in registros_crudos:
            turno_val = reg['turno']
            if turno_val in turnos:
                turnos[turno_val] = reg
            
            if reg['observaciones']: observaciones_global = reg['observaciones']
            if reg['firma_jefe_turno_1']: firma1 = reg['firma_jefe_turno_1']
            if reg['firma_jefe_turno_2']: firma2 = reg['firma_jefe_turno_2']
            if reg['firma_subjefe_calidad']: firma3 = reg['firma_subjefe_calidad']
            if reg['firma_jefe_calidad']: firma4 = reg['firma_jefe_calidad']

        context = {
            'fecha_seleccionada': fecha_consulta,
            'planta_seleccionada': planta_consulta,
            't1': turnos["6:00 A.M. a 10:00 A.M."],
            't2': turnos["11:00 A.M. a 3:00 P.M."],
            't3': turnos["4:00 P.M. a 8:00 P.M."],
            'obs': observaciones_global,
            'firma1': firma1,
            'firma2': firma2,
            'firma3': firma3,
            'firma4': firma4
        }
        return render_template('resumen_osmosis_vasos.html', **context)

    @app.route('/detalle_osmosis_vasos/<int:id>')
    @login_required
    def ver_detalle_osmosis_vasos(id):
        conn = get_db_connection()
        registro = conn.execute('SELECT * FROM registro_osmosis_vasos WHERE id = ?', (id,)).fetchone()
        conn.close()
        
        if registro is None:
            flash('El registro no fue encontrado.', 'danger')
            return redirect(url_for('osmosis_vasos_index'))
            
        return render_template('detalle_osmosis_vasos.html', registro=registro)

    @app.route('/exportar_osmosis_vasos', methods=['POST'])
    @login_required
    @admin_or_super_required
    def exportar_osmosis_vasos():
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        planta = request.form.get('planta', 'Planta_A')
        
        if not fecha_inicio or not fecha_fin:
            flash('Ambas fechas son obligatorias.', 'warning')
            return redirect(url_for('osmosis_vasos_index'))
            
        import pandas as pd
        from io import BytesIO

        conn = get_db_connection()
        query = 'SELECT * FROM registro_osmosis_vasos WHERE fecha BETWEEN ? AND ? AND planta = ? ORDER BY fecha ASC, id ASC'
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin, planta))
        conn.close()
        
        if df.empty:
            flash(f'No se encontraron registros entre {fecha_inicio} y {fecha_fin}.', 'info')
            return redirect(url_for('osmosis_vasos_index'))
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Vasos')
        
        output.seek(0)
        
        filename = f"Registros_Vasos_{fecha_inicio}_a_{fecha_fin}.xlsx"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @app.route('/dashboard_osmosis_vasos')
    @login_required
    @admin_or_super_required
    def dashboard_osmosis_vasos():
        hoy = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = request.args.get('fecha_inicio', hoy)
        fecha_fin = request.args.get('fecha_fin', hoy)
        planta = request.args.get('planta', '')

        conn = get_db_connection()
        if planta:
            registros = conn.execute(
                'SELECT * FROM registro_osmosis_vasos WHERE fecha BETWEEN ? AND ? AND planta = ? ORDER BY fecha ASC, id ASC',
                (fecha_inicio, fecha_fin, planta)
            ).fetchall()
        else:
            registros = conn.execute(
                'SELECT * FROM registro_osmosis_vasos WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC',
                (fecha_inicio, fecha_fin)
            ).fetchall()
        conn.close()
        
        import json
        
        labels_turnos = []
        chart_sdt_final = []
        chart_efi_final = []

        for r in registros:
            labels_turnos.append(f"{r['fecha']} ({r['turno']})")
            
            try:
                sdt = float(r['sdt_final']) if r['sdt_final'] else 0.0
                chart_sdt_final.append(sdt)
            except (ValueError, TypeError):
                chart_sdt_final.append(None)
                
            try:
                efi = float(r['efi_final']) if r['efi_final'] else 0.0
                chart_efi_final.append(efi)
            except (ValueError, TypeError):
                chart_efi_final.append(None)

        context = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'planta_seleccionada': planta,
            'chart_labels': json.dumps(labels_turnos),
            'chart_sdt_final': json.dumps(chart_sdt_final),
            'chart_efi_final': json.dumps(chart_efi_final)
        }

        return render_template('dashboard_osmosis_vasos.html', **context)
