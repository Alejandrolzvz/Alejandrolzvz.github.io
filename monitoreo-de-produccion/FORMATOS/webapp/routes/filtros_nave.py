import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from utils.db import get_db_connection
from utils.decorators import admin_or_super_required

def init_filtros_nave_routes(app):
    @app.route('/filtros_nave')
    @login_required
    def filtros_nave_index():
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_filtros_nave ORDER BY fecha DESC, id DESC LIMIT 20').fetchall()
        conn.close()
        return render_template('filtros_nave_index.html', registros=registros)

    @app.route('/nuevo_filtros_nave', methods=('GET', 'POST'))
    @login_required
    def nuevo_filtros_nave():
        if request.method == 'POST':
            fecha = request.form.get('fecha', '')
            planta = request.form.get('planta', '')
            
            limpieza_general_cumple = request.form.get('limpieza_general_cumple', '0')
            limpieza_general_obs = request.form.get('limpieza_general_obs', '')
            
            limpieza_profunda_cumple = request.form.get('limpieza_profunda_cumple', '0')
            limpieza_profunda_obs = request.form.get('limpieza_profunda_obs', '')
            
            limpieza_otros_cumple = request.form.get('limpieza_otros_cumple', '0')
            limpieza_otros_obs = request.form.get('limpieza_otros_obs', '')
            
            material_prueba_cumple = request.form.get('material_prueba_cumple', '0')
            material_prueba_obs = request.form.get('material_prueba_obs', '')
            
            infraestructura_pintado_cumple = request.form.get('infraestructura_pintado_cumple', '0')
            infraestructura_pintado_obs = request.form.get('infraestructura_pintado_obs', '')
            
            infraestructura_tuberias_cumple = request.form.get('infraestructura_tuberias_cumple', '0')
            infraestructura_tuberias_obs = request.form.get('infraestructura_tuberias_obs', '')
            
            mantenimiento_calcas_area_cumple = request.form.get('mantenimiento_calcas_area_cumple', '0')
            mantenimiento_calcas_area_obs = request.form.get('mantenimiento_calcas_area_obs', '')
            
            mantenimiento_calcas_lavadora_cumple = request.form.get('mantenimiento_calcas_lavadora_cumple', '0')
            mantenimiento_calcas_lavadora_obs = request.form.get('mantenimiento_calcas_lavadora_obs', '')
            
            documentacion_archivos_cumple = request.form.get('documentacion_archivos_cumple', '0')
            documentacion_archivos_obs = request.form.get('documentacion_archivos_obs', '')
            
            documentacion_firmas_cumple = request.form.get('documentacion_firmas_cumple', '0')
            documentacion_firmas_obs = request.form.get('documentacion_firmas_obs', '')
            
            firma_ejecuta = request.form.get('firma_ejecuta', '')
            firma_responsable = request.form.get('firma_responsable', '')

            if not fecha or not planta:
                flash('La fecha y planta son obligatorias.', 'danger')
            else:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO registro_filtros_nave (
                        fecha, planta,
                        limpieza_general_cumple, limpieza_general_obs,
                        limpieza_profunda_cumple, limpieza_profunda_obs,
                        limpieza_otros_cumple, limpieza_otros_obs,
                        material_prueba_cumple, material_prueba_obs,
                        infraestructura_pintado_cumple, infraestructura_pintado_obs,
                        infraestructura_tuberias_cumple, infraestructura_tuberias_obs,
                        mantenimiento_calcas_area_cumple, mantenimiento_calcas_area_obs,
                        mantenimiento_calcas_lavadora_cumple, mantenimiento_calcas_lavadora_obs,
                        documentacion_archivos_cumple, documentacion_archivos_obs,
                        documentacion_firmas_cumple, documentacion_firmas_obs,
                        firma_ejecuta, firma_responsable,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fecha, planta,
                    int(limpieza_general_cumple), limpieza_general_obs,
                    int(limpieza_profunda_cumple), limpieza_profunda_obs,
                    int(limpieza_otros_cumple), limpieza_otros_obs,
                    int(material_prueba_cumple), material_prueba_obs,
                    int(infraestructura_pintado_cumple), infraestructura_pintado_obs,
                    int(infraestructura_tuberias_cumple), infraestructura_tuberias_obs,
                    int(mantenimiento_calcas_area_cumple), mantenimiento_calcas_area_obs,
                    int(mantenimiento_calcas_lavadora_cumple), mantenimiento_calcas_lavadora_obs,
                    int(documentacion_archivos_cumple), documentacion_archivos_obs,
                    int(documentacion_firmas_cumple), documentacion_firmas_obs,
                    firma_ejecuta, firma_responsable,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
                conn.close()
                flash('Registro guardado exitosamente.', 'success')
                return redirect(url_for('filtros_nave_index'))

        hoy = datetime.now().strftime('%Y-%m-%d')
        return render_template('formulario_filtros_nave.html', hoy=hoy)

    @app.route('/registro_filtros_nave/<int:id>')
    @login_required
    def detalle_filtros_nave(id):
        conn = get_db_connection()
        registro = conn.execute('SELECT * FROM registro_filtros_nave WHERE id = ?', (id,)).fetchone()
        conn.close()
        
        if registro is None:
            flash('Registro no encontrado.', 'danger')
            return redirect(url_for('filtros_nave_index'))
            
        return render_template('detalle_filtros_nave.html', registro=registro)

    @app.route('/exportar_filtros_nave', methods=['POST'])
    @login_required
    @admin_or_super_required
    def exportar_filtros_nave():
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            flash('Ambas fechas son obligatorias.', 'warning')
            return redirect(url_for('filtros_nave_index'))
            
        conn = get_db_connection()
        query = 'SELECT * FROM registro_filtros_nave WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC, id ASC'
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        
        if df.empty:
            flash(f'No se encontraron registros.', 'info')
            return redirect(url_for('filtros_nave_index'))
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtros_Nave')
        output.seek(0)
        
        filename = f"Filtros_Nave_{fecha_inicio}_a_{fecha_fin}.xlsx"
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @app.route('/resumen_filtros_nave')
    @login_required
    @admin_or_super_required
    def resumen_filtros_nave():
        fecha_consulta = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registro_filtros_nave WHERE fecha = ? ORDER BY id ASC', (fecha_consulta,)).fetchall()
        conn.close()
        return render_template('resumen_filtros_nave.html', registros=registros, fecha_seleccionada=fecha_consulta)
