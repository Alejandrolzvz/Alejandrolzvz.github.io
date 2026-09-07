import os

app_path = r'C:\PROYECTOS\FORMATOS\webapp\app.py'
routes_dir = r'C:\PROYECTOS\FORMATOS\webapp\routes'
os.makedirs(routes_dir, exist_ok=True)
os.makedirs(r'C:\PROYECTOS\FORMATOS\webapp\scripts', exist_ok=True)

with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def build_module(name, start, end):
    module_lines = lines[start:end]
    indented = ["    " + line if line.strip() else line for line in module_lines]
        
    code = f"""import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from utils.db import get_db_connection
from utils.models import User
from utils.decorators import admin_required, admin_or_super_required

def init_{name}_routes(app):
"""
    code += "".join(indented)
    return code

with open(os.path.join(routes_dir, 'osmosis.py'), 'w', encoding='utf-8') as f:
    f.write(build_module("osmosis", 262, 522))

with open(os.path.join(routes_dir, 'calidad.py'), 'w', encoding='utf-8') as f:
    f.write(build_module("calidad", 522, 630))

with open(os.path.join(routes_dir, 'suavizador.py'), 'w', encoding='utf-8') as f:
    f.write(build_module("suavizador", 630, 716))

with open(os.path.join(routes_dir, 'pozos.py'), 'w', encoding='utf-8') as f:
    f.write(build_module("pozos", 716, 995))

print("Partición manual completada.")
