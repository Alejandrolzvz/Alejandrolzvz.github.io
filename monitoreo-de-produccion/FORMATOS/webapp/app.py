import os
from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
from flask_login import LoginManager, current_user, login_required
from utils.db import get_db_connection
from utils.models import User

# Imports modulares
from routes.auth import init_auth_routes
from routes.osmosis import init_osmosis_routes
from routes.calidad import init_calidad_routes
from routes.calidad_lavado import init_calidad_lavado_routes
from routes.suavizador import init_suavizador_routes
from routes.pozos import init_pozos_routes
from routes.filtros_nave import init_filtros_nave_routes
from routes.ciclos_suavizador import init_ciclos_suavizador_routes
from routes.osmosis_vasos import init_osmosis_vasos_routes

from init_db_all import init_db

load_dotenv()

# Garantizar que la base de datos y sus tablas estén creadas al iniciar
init_db()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_record = conn.execute('''
        SELECT u.*, r.name as role_name 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        WHERE u.id = ?
    ''', (user_id,)).fetchone()
    conn.close()
    if user_record:
        return User(id=user_record['id'], username=user_record['username'], 
                    role_id=user_record['role_id'], role_name=user_record['role_name'])
    return None

@app.route('/')
@login_required
def home():
    return render_template('home.html')

# Inicializar todos los departamentos de software
init_auth_routes(app)
init_osmosis_routes(app)
init_calidad_routes(app)
init_calidad_lavado_routes(app)
init_suavizador_routes(app)
init_pozos_routes(app)
init_filtros_nave_routes(app)
init_ciclos_suavizador_routes(app)
init_osmosis_vasos_routes(app)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(host='0.0.0.0', debug=debug_mode, port=5000)
