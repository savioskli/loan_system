from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from utils.decorators import admin_required
from utils.db import get_db_connection

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/general')
@login_required
@admin_required
def general():
    return redirect(url_for('admin.system_settings'))

@settings_bp.route('/sections')
@login_required
@admin_required
def sections():
    return redirect(url_for('admin.form_sections'))

@settings_bp.route('/email')
@login_required
@admin_required
def email():
    flash('Email settings are not yet implemented.', 'info')
    return redirect(url_for('admin.dashboard'))

@settings_bp.route('/notifications')
@login_required
@admin_required
def notifications():
    flash('Notification settings are not yet implemented.', 'info')
    return redirect(url_for('admin.dashboard'))
