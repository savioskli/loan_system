from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.staff import Staff
from models.branch import Branch
from models.activity_log import ActivityLog
from models.system_settings import SystemSettings
from forms.admin_forms import SystemSettingsForm
from extensions import db
import logging
import traceback
from werkzeug.utils import secure_filename
import os

# Configure logging
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    try:
        if current_user.role.lower() == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the page.', 'error')
        return render_template('errors/500.html'), 500

@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        if current_user.role.lower() == 'admin':
            return redirect(url_for('main.admin_dashboard'))
            
        # Regular staff dashboard
        activities = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(10)
        return render_template('dashboard.html', activities=activities)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access the admin dashboard.', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Admin dashboard stats
        total_users = Staff.query.count()
        active_users = Staff.query.filter_by(is_active=True).count()
        total_branches = Branch.query.count()
        active_branches = Branch.query.filter_by(is_active=True).count()
        recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10)
        
        return render_template('admin/dashboard.html', 
                             total_users=total_users,
                             active_users=active_users,
                             total_branches=total_branches,
                             active_branches=active_branches,
                             recent_activities=recent_activities)
    except Exception as e:
        logger.error(f"Error in admin dashboard route: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the admin dashboard.', 'error')
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    try:
        form = SystemSettingsForm()

        if form.validate_on_submit():
            # Update system settings
            SystemSettings.set_setting('system_name', form.system_name.data, current_user.id)
            SystemSettings.set_setting('system_description', form.system_description.data, current_user.id)
            SystemSettings.set_setting('theme_mode', form.theme_mode.data, current_user.id)
            SystemSettings.set_setting('theme_primary_color', form.theme_primary_color.data, current_user.id)
            SystemSettings.set_setting('theme_secondary_color', form.theme_secondary_color.data, current_user.id)

            # Handle logo upload
            if form.system_logo.data:
                file = form.system_logo.data
                if file:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    SystemSettings.set_setting('system_logo', f'/static/uploads/{filename}', current_user.id)

            flash('Settings updated successfully!', 'success')
            return redirect(url_for('main.admin_settings'))

        # Pre-fill form with existing settings
        if request.method == 'GET':
            form.system_name.data = SystemSettings.get_setting('system_name', 'Loan System')
            form.system_description.data = SystemSettings.get_setting('system_description', '')
            form.theme_mode.data = SystemSettings.get_setting('theme_mode', 'light')
            form.theme_primary_color.data = SystemSettings.get_setting('theme_primary_color', '#3B82F6')
            form.theme_secondary_color.data = SystemSettings.get_setting('theme_secondary_color', '#1E40AF')

        return render_template('admin/settings.html', form=form)
    except Exception as e:
        logger.error(f"Error in admin settings: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while processing your request.', 'error')
        return render_template('errors/500.html'), 500

# User Management Routes
@main_bp.route('/admin/users')
@login_required
def view_users():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/users.html')
    except Exception as e:
        logger.error(f"Error in view users: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/users/pending')
@login_required
def pending_approvals():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/pending_approvals.html')
    except Exception as e:
        logger.error(f"Error in pending approvals: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/users/roles')
@login_required
def user_roles():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/user_roles.html')
    except Exception as e:
        logger.error(f"Error in user roles: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

# Loan Management Routes
@main_bp.route('/admin/loan-types')
@login_required
def loan_types():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/loan_types.html')
    except Exception as e:
        logger.error(f"Error in loan types: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/loan-settings')
@login_required
def loan_settings():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/loan_settings.html')
    except Exception as e:
        logger.error(f"Error in loan settings: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/loan-reports')
@login_required
def loan_reports():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/loan_reports.html')
    except Exception as e:
        logger.error(f"Error in loan reports: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

# System Settings Routes
@main_bp.route('/admin/settings/email')
@login_required
def email_settings():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/email_settings.html')
    except Exception as e:
        logger.error(f"Error in email settings: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/settings/backup')
@login_required
def backup_settings():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/backup_settings.html')
    except Exception as e:
        logger.error(f"Error in backup settings: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

# Client Management Routes
@main_bp.route('/admin/client-management/fields')
@login_required
def client_fields():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/client_fields.html')
    except Exception as e:
        logger.error(f"Error in client fields: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/client-management/reports')
@login_required
def client_reports():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/client_reports.html')
    except Exception as e:
        logger.error(f"Error in client reports: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

# Activity Monitoring Routes
@main_bp.route('/admin/activity-monitoring/activities')
@login_required
def activity_logs():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/activity_logs.html')
    except Exception as e:
        logger.error(f"Error in activity logs: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/activity-monitoring/audit')
@login_required
def audit_trail():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/audit_trail.html')
    except Exception as e:
        logger.error(f"Error in audit trail: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/activity-monitoring/system-logs')
@login_required
def system_logs():
    try:
        if not current_user.role.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/system_logs.html')
    except Exception as e:
        logger.error(f"Error in system logs: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500
