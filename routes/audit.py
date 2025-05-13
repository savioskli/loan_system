from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.audit import AuditLog
from models.post_disbursement_modules import PostDisbursementModule
from flask_login import login_required, current_user
from utils.decorators import admin_required
from extensions import db
import logging
from datetime import datetime, timedelta
from sqlalchemy import desc

# Set up logging
logger = logging.getLogger(__name__)

# Define the blueprint
audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/admin/audit', methods=['GET'])
@login_required
@admin_required
def audit_dashboard():
    """Render the audit dashboard page"""
    logger.info("Accessing audit dashboard")
    try:
        # Get filter parameters
        action_type = request.args.get('action_type')
        entity_type = request.args.get('entity_type')
        user_id = request.args.get('user_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query
        query = AuditLog.query
        
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.created_at >= date_from)
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the entire end date
            date_to = date_to + timedelta(days=1)
            query = query.filter(AuditLog.created_at < date_to)
            
        # Get the latest audit logs, ordered by creation date (newest first)
        audit_logs = query.order_by(desc(AuditLog.created_at)).limit(100).all()
        
        # Get distinct action types and entity types for filter dropdowns
        action_types = db.session.query(AuditLog.action_type).distinct().all()
        entity_types = db.session.query(AuditLog.entity_type).distinct().all()
        
        # Get statistics
        total_logs = AuditLog.query.count()
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        logs_today = AuditLog.query.filter(AuditLog.created_at.between(today_start, today_end)).count()
        
        # Get activity by action type
        action_stats = db.session.query(
            AuditLog.action_type, 
            db.func.count(AuditLog.id)
        ).group_by(AuditLog.action_type).all()
        
        # Get activity by entity type
        entity_stats = db.session.query(
            AuditLog.entity_type, 
            db.func.count(AuditLog.id)
        ).group_by(AuditLog.entity_type).all()
        
        return render_template(
            'admin/audit/dashboard.html', 
            audit_logs=audit_logs,
            action_types=[t[0] for t in action_types],
            entity_types=[t[0] for t in entity_types],
            total_logs=total_logs,
            logs_today=logs_today,
            action_stats=action_stats,
            entity_stats=entity_stats,
            selected_action_type=action_type,
            selected_entity_type=entity_type,
            selected_user_id=user_id,
            selected_date_from=date_from,
            selected_date_to=date_to
        )
    except Exception as e:
        logger.error(f"Error accessing audit dashboard: {str(e)}", exc_info=True)
        flash('An error occurred while loading the audit dashboard.', 'error')
        return redirect(url_for('admin.dashboard'))

@audit_bp.route('/admin/audit/logs', methods=['GET'])
@login_required
@admin_required
def audit_logs():
    """Render the audit logs page with filtering options"""
    logger.info("Accessing audit logs")
    try:
        # Get filter parameters
        action_type = request.args.get('action_type')
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id')
        user_id = request.args.get('user_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Build query
        query = AuditLog.query
        
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.created_at >= date_from)
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the entire end date
            date_to = date_to + timedelta(days=1)
            query = query.filter(AuditLog.created_at < date_to)
            
        # Get the audit logs, ordered by creation date (newest first)
        pagination = query.order_by(desc(AuditLog.created_at)).paginate(page=page, per_page=per_page)
        
        # Get distinct action types and entity types for filter dropdowns
        action_types = db.session.query(AuditLog.action_type).distinct().all()
        entity_types = db.session.query(AuditLog.entity_type).distinct().all()
        
        return render_template(
            'admin/audit/logs.html', 
            pagination=pagination,
            action_types=[t[0] for t in action_types],
            entity_types=[t[0] for t in entity_types],
            selected_action_type=action_type,
            selected_entity_type=entity_type,
            selected_entity_id=entity_id,
            selected_user_id=user_id,
            selected_date_from=date_from,
            selected_date_to=date_to
        )
    except Exception as e:
        logger.error(f"Error accessing audit logs: {str(e)}", exc_info=True)
        flash('An error occurred while loading the audit logs.', 'error')
        return redirect(url_for('admin.dashboard'))

@audit_bp.route('/admin/audit/detail/<int:log_id>', methods=['GET'])
@login_required
@admin_required
def audit_detail(log_id):
    """Render the audit detail page for a specific log entry"""
    logger.info(f"Accessing audit detail for log ID: {log_id}")
    try:
        # Get the audit log entry
        audit_log = AuditLog.query.get_or_404(log_id)
        
        return render_template('admin/audit/detail.html', audit_log=audit_log)
    except Exception as e:
        logger.error(f"Error accessing audit detail: {str(e)}", exc_info=True)
        flash('An error occurred while loading the audit detail.', 'error')
        return redirect(url_for('audit.audit_logs'))

@audit_bp.route('/admin/audit/entity/<string:entity_type>/<int:entity_id>', methods=['GET'])
@login_required
@admin_required
def entity_audit_history(entity_type, entity_id):
    """Render the audit history for a specific entity"""
    logger.info(f"Accessing audit history for {entity_type} ID: {entity_id}")
    try:
        # Get the audit logs for the entity
        audit_logs = AuditLog.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(desc(AuditLog.created_at)).all()
        
        return render_template(
            'admin/audit/entity_history.html', 
            audit_logs=audit_logs,
            entity_type=entity_type,
            entity_id=entity_id
        )
    except Exception as e:
        logger.error(f"Error accessing entity audit history: {str(e)}", exc_info=True)
        flash('An error occurred while loading the entity audit history.', 'error')
        return redirect(url_for('audit.audit_logs'))

@audit_bp.route('/admin/audit/user/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def user_audit_history(user_id):
    """Render the audit history for a specific user"""
    logger.info(f"Accessing audit history for user ID: {user_id}")
    try:
        # Get the audit logs for the user
        audit_logs = AuditLog.query.filter_by(
            user_id=user_id
        ).order_by(desc(AuditLog.created_at)).all()
        
        return render_template(
            'admin/audit/user_history.html', 
            audit_logs=audit_logs,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error accessing user audit history: {str(e)}", exc_info=True)
        flash('An error occurred while loading the user audit history.', 'error')
        return redirect(url_for('audit.audit_logs'))
