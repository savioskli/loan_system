from functools import wraps
from flask import flash, redirect, url_for, abort, request
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_active:
            flash('Your account is inactive. Please contact an administrator.', 'error')
            return redirect(url_for('auth.login'))
        if current_user.role.lower() != 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
