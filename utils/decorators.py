from functools import wraps
from flask import flash, redirect, url_for, request, abort
from flask_login import current_user
from flask_wtf.csrf import validate_csrf

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.role or current_user.role.name.lower() != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def csrf_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            csrf_token = request.form.get('csrf_token')
            if not csrf_token:
                csrf_token = request.headers.get('X-CSRF-Token')
            if not csrf_token:
                abort(400, description='CSRF token missing')
            try:
                validate_csrf(csrf_token)
            except:
                abort(400, description='CSRF validation failed')
        return f(*args, **kwargs)
    return decorated_function
