from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_super_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['ADMIN', 'SUPER']:
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
