from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from utils.db import get_db_connection
from utils.models import User
from utils.decorators import admin_required

def init_auth_routes(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            conn = get_db_connection()
            user_record = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user_record and check_password_hash(user_record['password_hash'], password):
                role_record = conn.execute('SELECT name FROM roles WHERE id = ?', (user_record['role_id'],)).fetchone()
                user = User(id=user_record['id'], username=user_record['username'], 
                            role_id=user_record['role_id'], role_name=role_record['name'])
                login_user(user)
                next_page = request.args.get('next')
                conn.close()
                return redirect(next_page or url_for('home'))
            else:
                conn.close()
                flash('Usuario o contraseña incorrectos.', 'danger')
                
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Has cerrado sesión exitosamente.', 'info')
        return redirect(url_for('login'))

    @app.route('/cambiar_password', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def cambiar_password():
        if request.method == 'POST':
            user_to_change = request.form.get('user_to_change')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not user_to_change or not new_password or not confirm_password:
                flash('Todos los campos son obligatorios.', 'danger')
            elif new_password != confirm_password:
                flash('Las contraseñas no coinciden.', 'danger')
            else:
                conn = get_db_connection()
                user_record = conn.execute('SELECT * FROM users WHERE username = ?', (user_to_change,)).fetchone()
                
                if user_record:
                    hashed_pw = generate_password_hash(new_password)
                    conn.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hashed_pw, user_to_change))
                    conn.commit()
                    flash(f'Contraseña actualizada exitosamente para {user_to_change}.', 'success')
                else:
                    flash(f'El usuario {user_to_change} no existe.', 'danger')
                    
                conn.close()
                return redirect(url_for('home'))
                
        conn = get_db_connection()
        users = conn.execute('SELECT username FROM users').fetchall()
        conn.close()
        return render_template('cambiar_password.html', users=users)

    @app.route('/usuarios')
    @login_required
    @admin_required
    def lista_usuarios():
        conn = get_db_connection()
        usuarios = conn.execute('''
            SELECT u.id, u.username, u.role_id, u.created_at, r.name as role_name 
            FROM users u 
            JOIN roles r ON u.role_id = r.id 
            ORDER BY u.username ASC
        ''').fetchall()
        conn.close()
        return render_template('usuarios.html', usuarios=usuarios)

    @app.route('/usuarios/nuevo', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def nuevo_usuario():
        conn = get_db_connection()
        roles = conn.execute('SELECT * FROM roles ORDER BY name ASC').fetchall()
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            role_id = request.form.get('role_id')
            
            if not username or not password or not role_id:
                flash('Todos los campos son obligatorios.', 'danger')
            else:
                existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
                if existing:
                    flash(f'El usuario {username} ya existe.', 'danger')
                else:
                    hashed_pw = generate_password_hash(password)
                    role_record = conn.execute('SELECT name FROM roles WHERE id = ?', (role_id,)).fetchone()
                    role_name = role_record['name'] if role_record else 'PRODUC'
                    conn.execute('INSERT INTO users (username, password_hash, role_id, role) VALUES (?, ?, ?, ?)',
                                (username, hashed_pw, role_id, role_name))
                    conn.commit()
                    flash(f'Usuario {username} creado exitosamente.', 'success')
                    conn.close()
                    return redirect(url_for('lista_usuarios'))
                
        conn.close()
        return render_template('formulario_usuario.html', usuario=None, roles=roles)

    @app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def editar_usuario(id):
        conn = get_db_connection()
        usuario = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
        roles = conn.execute('SELECT * FROM roles ORDER BY name ASC').fetchall()
        
        if not usuario:
            conn.close()
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('lista_usuarios'))

        if request.method == 'POST':
            username = request.form.get('username')
            role_id = request.form.get('role_id')
            password = request.form.get('password')
            
            if not username or not role_id:
                flash('Usuario y Rol son obligatorios.', 'danger')
            elif id == 1 and int(role_id) != 1:
                flash('No se puede cambiar el rol del administrador maestro.', 'danger')
            elif id == current_user.id and int(role_id) != current_user.role_id:
                flash('No puedes cambiar tu propio rol para evitar pérdida de acceso.', 'warning')
            else:
                if password:
                    hashed_pw = generate_password_hash(password)
                    conn.execute('UPDATE users SET username = ?, role_id = ?, password_hash = ? WHERE id = ?',
                                (username, role_id, hashed_pw, id))
                else:
                    conn.execute('UPDATE users SET username = ?, role_id = ? WHERE id = ?',
                                (username, role_id, id))
                conn.commit()
                flash(f'Usuario {username} actualizado exitosamente.', 'success')
                conn.close()
                return redirect(url_for('lista_usuarios'))
                
        conn.close()
        return render_template('formulario_usuario.html', usuario=usuario, roles=roles)

    @app.route('/usuarios/eliminar/<int:id>', methods=['POST'])
    @login_required
    @admin_required
    def eliminar_usuario(id):
        if id == 1:
            flash('No se puede eliminar al administrador maestro.', 'danger')
            return redirect(url_for('lista_usuarios'))
            
        if current_user.id == id:
            flash('No puedes eliminarte a ti mismo.', 'danger')
            return redirect(url_for('lista_usuarios'))
            
        conn = get_db_connection()
        user_to_delete = conn.execute('SELECT r.name as role_name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = ?', (id,)).fetchone()
        
        if user_to_delete and user_to_delete['role_name'] == 'ADMIN':
            admins = conn.execute('SELECT COUNT(*) FROM users u JOIN roles r ON u.role_id = r.id WHERE r.name = "ADMIN"').fetchone()[0]
            if admins <= 1:
                flash('No se puede eliminar al último administrador del sistema.', 'danger')
                conn.close()
                return redirect(url_for('lista_usuarios'))

        conn.execute('DELETE FROM users WHERE id = ?', (id,))
        conn.commit()
        flash('Usuario eliminado exitosamente.', 'success')
        conn.close()
        return redirect(url_for('lista_usuarios'))
