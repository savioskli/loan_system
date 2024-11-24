from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import select, func
from models.staff import Staff
from models.branch import Branch
from models.activity_log import ActivityLog
from models.system_settings import SystemSettings
from models.role import Role
from forms.admin_forms import SystemSettingsForm
from extensions import db
from utils.logging_utils import log_activity
from utils.decorators import admin_required
import logging
import traceback
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def log_activity(user_id, action, details=None):
    try:
        ip_address = request.remote_addr
        activity = ActivityLog(user_id=user_id, action=action, details=details, ip_address=ip_address)
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    try:
        if current_user.role.name.lower() == 'admin':
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
        if current_user.role.name.lower() == 'admin':
            return redirect(url_for('main.admin_dashboard'))
            
        # Regular staff dashboard
        activities = db.session.execute(select(ActivityLog).where(ActivityLog.user_id == current_user.id).order_by(ActivityLog.timestamp.desc())).scalars().limit(10).all()
        return render_template('dashboard.html', activities=activities)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    try:
        if not current_user.role.name.lower() == 'admin':
            flash('You do not have permission to access the admin dashboard.', 'error')
            return redirect(url_for('main.dashboard'))
        
        logger.info("Getting admin dashboard stats")
        
        # Admin dashboard stats using func.count()
        total_users = db.session.scalar(select(func.count()).select_from(Staff))
        active_users = db.session.scalar(select(func.count()).select_from(Staff).where(Staff.is_active == True))
        total_branches = db.session.scalar(select(func.count()).select_from(Branch))
        active_branches = db.session.scalar(select(func.count()).select_from(Branch).where(Branch.is_active == True))
        
        logger.info(f"Stats - Total Users: {total_users}, Active Users: {active_users}, "
                   f"Total Branches: {total_branches}, Active Branches: {active_branches}")
        
        # Get recent activities with proper error handling
        try:
            recent_activities = db.session.execute(
                select(ActivityLog)
                .order_by(ActivityLog.timestamp.desc())
                .limit(10)
            ).scalars().all()
            logger.info(f"Retrieved {len(recent_activities)} recent activities")
        except Exception as e:
            logger.error(f"Error fetching recent activities: {str(e)}")
            recent_activities = []
            flash("Unable to load recent activities", "warning")
        
        log_activity(current_user.id, 'view_admin_dashboard', 'Viewed admin dashboard')
        return render_template('admin/dashboard.html', 
                             total_users=total_users or 0,
                             active_users=active_users or 0,
                             total_branches=total_branches or 0,
                             active_branches=active_branches or 0,
                             recent_activities=recent_activities)
                             
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the admin dashboard.', 'error')
        return render_template('errors/500.html'), 500

# User Management Routes
@main_bp.route('/admin/users')
@login_required
def view_users():
    try:
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
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
        if not current_user.role.name.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return render_template('admin/client_reports.html')
    except Exception as e:
        logger.error(f"Error in client reports: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

# Activity Monitoring Routes
@main_bp.route('/admin/activity-monitoring/activities')
@login_required
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Get filter parameters
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # Build query
    query = ActivityLog.query

    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    if action:
        query = query.filter(ActivityLog.action == action)
    if date_from:
        query = query.filter(ActivityLog.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(ActivityLog.created_at <= datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))

    # Get unique actions for filter dropdown
    actions = db.session.query(ActivityLog.action).distinct().all()
    actions = [action[0] for action in actions]

    # Get users for filter dropdown
    users = Staff.query.all()

    # Paginate results
    activities = query.order_by(desc(ActivityLog.created_at)).paginate(page=page, per_page=per_page)

    return render_template('admin/activity_logs.html',
                         activities=activities,
                         users=users,
                         actions=actions)

@main_bp.route('/admin/activity-monitoring/audit')
@login_required
@admin_required
def audit_trail():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Get filter parameters
        user_id = request.args.get('user_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        flash('Audit trail feature is not yet fully implemented.', 'info')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        logger.error(f"Error in audit trail: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading audit trail', 'error')
        return render_template('admin/audit_trail.html',
                             logs=None,
                             users=[])

@main_bp.route('/admin/activity-monitoring/system-logs')
@login_required
def system_logs():
    try:
        if not current_user.role.name.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        # Read the application log file
        log_file = 'app.log'
        log_entries = []
        
        try:
            with open(log_file, 'r') as f:
                # Read all lines and reverse them to get newest first
                lines = f.readlines()
                total_lines = len(lines)
                
                # Calculate pagination
                start_idx = (page - 1) * per_page
                end_idx = min(start_idx + per_page, total_lines)
                
                # Process the lines for the current page
                for line in lines[start_idx:end_idx]:
                    # Parse log line (assuming standard logging format)
                    try:
                        parts = line.split(' - ', 2)
                        timestamp = parts[0]
                        level = parts[1]
                        message = parts[2] if len(parts) > 2 else 'No message'
                        
                        log_entries.append({
                            'timestamp': timestamp,
                            'level': level,
                            'message': message
                        })
                    except Exception as parse_error:
                        logger.error(f"Error parsing log line: {str(parse_error)}")
                        continue
                
                # Create a pagination object
                class Pagination:
                    def __init__(self, items, page, per_page, total):
                        self.items = items
                        self.page = page
                        self.per_page = per_page
                        self.total = total
                        self.pages = (total + per_page - 1) // per_page
                    
                    def iter_pages(self):
                        for i in range(1, self.pages + 1):
                            yield i
                
                pagination = Pagination(log_entries, page, per_page, total_lines)
                
        except FileNotFoundError:
            flash('System log file not found.', 'error')
            log_entries = []
            pagination = None
        
        return render_template('admin/system_logs.html',
                             logs=pagination)
    except Exception as e:
        logger.error(f"Error in system logs: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500

@main_bp.route('/admin/test-logging')
@login_required
def test_logging():
    try:
        if not current_user.role.name.lower() == 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Test activity logging
        log_activity(current_user.id, 'test_logging', 'Testing activity logging system')
        flash('Activity logging test completed. Check the activity logs.', 'success')
        return redirect(url_for('main.activity_logs'))
    except Exception as e:
        logger.error(f"Error in test logging: {str(e)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500
