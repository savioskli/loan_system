from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from utils.decorators import admin_required
import traceback
from forms.general_settings import GeneralSettingsForm
from services.settings_service import SettingsService
from extensions import db
from utils.dynamic_tables import create_or_update_module_table
import mysql.connector
from config import db_config
from models.staff import Staff
from models.branch import Branch
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint, CoreBankingLog
from services.config_manager import ConfigManager
from services.api_manager import APIManager
from services.core_banking_service import CoreBankingService
from database.db_manager import DatabaseManager

def get_db_connection():
    return mysql.connector.connect(**db_config)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get user statistics
    total_users = Staff.query.count()
    active_users = Staff.query.filter_by(is_active=True).count()
    
    # Get branch statistics
    total_branches = Branch.query.count()
    active_branches = Branch.query.filter_by(is_active=True).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_branches=total_branches,
                         active_branches=active_branches)

@admin_bp.route('/system-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    form = GeneralSettingsForm()
    current_logo = None
    settings = None
    
    try:
        # Get current settings
        settings = SettingsService.get_all_settings()
        if settings:
            current_logo = settings.get('site_logo')
        
        if form.validate_on_submit():
            # Update settings using service
            settings_data = {
                'site_name': form.site_name.data,
                'site_description': form.site_description.data,
                'theme_mode': form.theme_mode.data,
                'primary_color': form.primary_color.data,
                'secondary_color': form.secondary_color.data
            }
            
            # Update general settings
            SettingsService.update_settings(settings_data, current_user.id)
            
            # Handle logo upload if provided
            if form.site_logo.data:
                SettingsService.handle_logo_upload(form.site_logo.data, current_app, current_user.id)

            flash('Settings updated successfully!', 'success')
            return redirect(url_for('admin.system_settings'))

        # Pre-fill form with existing settings
        if request.method == 'GET' and settings:
            form.site_name.data = settings.get('site_name', '')
            form.site_description.data = settings.get('site_description', '')
            form.theme_mode.data = settings.get('theme_mode', 'light')
            form.primary_color.data = settings.get('primary_color', '#3B82F6')
            form.secondary_color.data = settings.get('secondary_color', '#1E40AF')
        
        return render_template('admin/general_settings/form.html', 
                             form=form,
                             current_logo=current_logo)
                             
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        traceback.print_exc()  # Print the full traceback for debugging
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/modules/fields/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_field():
    if request.method == 'POST':
        # Existing field creation code...
        
        try:
            db.session.add(new_field)
            db.session.commit()
            
            # Update the dynamic table for this module
            module = Module.query.get(module_id)
            if module:
                create_or_update_module_table(module.code)
            
            flash('Field added successfully!', 'success')
            return redirect(url_for('admin.list_fields', module_id=module_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding field: {str(e)}', 'error')
            return redirect(url_for('admin.list_fields', module_id=module_id))

@admin_bp.route('/form-sections')
@login_required
@admin_required
def form_sections():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT fs.*, m.name as module_name 
        FROM form_sections fs
        JOIN modules m ON fs.module_id = m.id
        ORDER BY fs.order, fs.name
    """)
    sections = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/sections/index.html', sections=sections)

@admin_bp.route('/form-sections/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_form_section():
    if request.method == 'POST':
        name = request.form['name']
        module_id = request.form['module']
        submodule_id = request.form.get('submodule')  # Optional submodule
        is_active = 'is_active' in request.form
        description = request.form.get('description')
        order = request.form.get('order', 0)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO form_sections (name, module_id, submodule_id, description, `order`, is_active) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, module_id, submodule_id if submodule_id else None, description, order, is_active)
            )
            conn.commit()
            flash('Form section created successfully!', 'success')
            return redirect(url_for('admin.form_sections'))
        except Exception as e:
            conn.rollback()
            flash(f'Error creating form section: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

    # Get parent modules
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT m.id, m.name, m.code, m.description
        FROM modules m
        WHERE m.is_active = 1 AND m.parent_id IS NULL
        ORDER BY m.name
    """)
    modules = cursor.fetchall()
    
    # Get submodules
    cursor.execute("""
        SELECT m.id, m.name, m.code, m.description, p.name as parent_name
        FROM modules m
        JOIN modules p ON m.parent_id = p.id
        WHERE m.is_active = 1 AND m.parent_id IS NOT NULL
        ORDER BY p.name, m.name
    """)
    submodules = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('admin/sections/form.html', 
                         section=None, 
                         modules=modules,
                         submodules=submodules)

@admin_bp.route('/form-sections/edit/<int:section_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_form_section(section_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        module_id = request.form['module']
        submodule_id = request.form.get('submodule')  # Optional submodule
        is_active = 'is_active' in request.form
        description = request.form.get('description')
        order = request.form.get('order', 0)

        try:
            cursor.execute(
                "UPDATE form_sections SET name=%s, module_id=%s, submodule_id=%s, description=%s, `order`=%s, is_active=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s",
                (name, module_id, submodule_id if submodule_id else None, description, order, is_active, section_id)
            )
            conn.commit()
            flash('Form section updated successfully!', 'success')
            return redirect(url_for('admin.form_sections'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating form section: {str(e)}', 'error')
            return redirect(url_for('admin.form_sections'))

    # Get the current section data
    cursor.execute("""
        SELECT fs.*, m.name as module_name, sm.id as submodule_id, sm.name as submodule_name 
        FROM form_sections fs
        JOIN modules m ON fs.module_id = m.id
        LEFT JOIN modules sm ON fs.submodule_id = sm.id
        WHERE fs.id = %s
    """, (section_id,))
    section = cursor.fetchone()

    if not section:
        cursor.close()
        conn.close()
        flash('Form section not found', 'error')
        return redirect(url_for('admin.form_sections'))

    # Get parent modules
    cursor.execute("""
        SELECT m.id, m.name, m.code, m.description
        FROM modules m
        WHERE m.is_active = 1 AND m.parent_id IS NULL
        ORDER BY m.name
    """)
    modules = cursor.fetchall()
    
    # Get submodules for the selected module
    cursor.execute("""
        SELECT m.id, m.name, m.code, m.description, p.name as parent_name
        FROM modules m
        JOIN modules p ON m.parent_id = p.id
        WHERE m.is_active = 1 AND m.parent_id IS NOT NULL
        ORDER BY p.name, m.name
    """)
    submodules = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/sections/form.html', 
                         section=section,
                         modules=modules,
                         submodules=submodules)

@admin_bp.route('/form-sections/delete/<int:section_id>', methods=['POST'])
@login_required
@admin_required
def delete_form_section(section_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # First check if the section exists
        cursor.execute("SELECT id FROM form_sections WHERE id = %s", (section_id,))
        section = cursor.fetchone()
        
        if not section:
            flash('Form section not found', 'error')
            return redirect(url_for('admin.form_sections'))

        cursor.execute("DELETE FROM form_sections WHERE id = %s", (section_id,))
        conn.commit()
        flash('Form section deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting form section: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin.form_sections'))

@admin_bp.route('/core-banking')
@login_required
@admin_required
def core_banking():
    """Core banking systems overview"""
    try:
        # Get all banking systems
        systems = DatabaseManager.get_all_systems()
        
        # Get statistics
        total_systems = len(systems)
        active_systems = len([s for s in systems if s.is_active])
        total_endpoints = CoreBankingEndpoint.query.count()
        active_endpoints = CoreBankingEndpoint.query.filter_by(is_active=True).count()

        return render_template('admin/core_banking/index.html',
                             systems=systems,
                             total_systems=total_systems,
                             active_systems=active_systems,
                             total_endpoints=total_endpoints,
                             active_endpoints=active_endpoints)
    except Exception as e:
        flash(f'Error loading core banking systems: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/core-banking/system/<int:system_id>')
@login_required
@admin_required
def view_system(system_id):
    """View core banking system details"""
    try:
        # Get system details
        system = DatabaseManager.get_system_by_id(system_id)
        if not system:
            flash('Banking system not found', 'error')
            return redirect(url_for('admin.core_banking'))

        # Get endpoints
        endpoints = DatabaseManager.get_system_endpoints(system_id)

        # Get system statistics
        stats = DatabaseManager.get_system_stats(system_id)

        # Get endpoint statistics
        endpoint_stats = {}
        for endpoint in endpoints:
            endpoint_stats[endpoint.id] = DatabaseManager.get_endpoint_stats(endpoint.id)

        # Get recent logs
        logs = DatabaseManager.get_logs(system_id=system_id, limit=50)

        # Prepare chart data
        from datetime import datetime, timedelta
        today = datetime.utcnow()
        dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        dates.reverse()

        success_data = []
        error_data = []
        for date in dates:
            day_logs = DatabaseManager.get_logs(
                system_id=system_id,
                start_date=f"{date} 00:00:00",
                end_date=f"{date} 23:59:59"
            )
            success_count = len([l for l in day_logs if l.response_status and l.response_status < 400])
            error_count = len([l for l in day_logs if not l.response_status or l.response_status >= 400])
            success_data.append(success_count)
            error_data.append(error_count)

        return render_template('admin/core_banking/view.html',
                             system=system,
                             endpoints=endpoints,
                             stats=stats,
                             endpoint_stats=endpoint_stats,
                             logs=logs,
                             chart_labels=dates,
                             chart_success_data=success_data,
                             chart_error_data=error_data)
    except Exception as e:
        flash(f'Error loading system details: {str(e)}', 'error')
        return redirect(url_for('admin.core_banking'))

@admin_bp.route('/core-banking/add-system', methods=['POST'])
@login_required
@admin_required
def add_system():
    """Add a new core banking system"""
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'message': 'No data provided'}, 400

        system = ConfigManager.create_banking_system(
            name=data.get('name'),
            base_url=data.get('base_url'),
            auth_type=data.get('auth_type'),
            auth_credentials=data.get('auth_credentials'),
            headers=data.get('headers'),
            description=data.get('description'),
            port=data.get('port')
        )
        return {'success': True, 'system': {
            'id': system.id,
            'name': system.name
        }}
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@admin_bp.route('/core-banking/system/<int:system_id>', methods=['GET'])
@login_required
@admin_required
def get_system(system_id):
    """Get core banking system details"""
    try:
        config = ConfigManager.get_system_config(system_id)
        return config
    except Exception as e:
        return {'error': str(e)}, 404

@admin_bp.route('/core-banking/system/<int:system_id>', methods=['POST'])
@login_required
@admin_required
def update_system(system_id):
    """Update a core banking system"""
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'message': 'No data provided'}, 400

        system = ConfigManager.update_banking_system(system_id, **data)
        return {'success': True, 'system': {
            'id': system.id,
            'name': system.name
        }}
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@admin_bp.route('/core-banking/system/<int:system_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_system(system_id):
    """Delete a core banking system"""
    try:
        ConfigManager.update_banking_system(system_id, is_active=False)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@admin_bp.route('/core-banking/system/<int:system_id>/endpoint', methods=['POST'])
@login_required
@admin_required
def add_endpoint(system_id):
    """Add a new endpoint to a banking system"""
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'message': 'No data provided'}, 400

        endpoint = ConfigManager.create_endpoint(
            system_id=system_id,
            name=data.get('name'),
            endpoint=data.get('endpoint'),
            method=data.get('method'),
            request_schema=data.get('request_schema'),
            response_schema=data.get('response_schema'),
            description=data.get('description')
        )
        return {'success': True, 'endpoint': {
            'id': endpoint.id,
            'name': endpoint.name
        }}
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@admin_bp.route('/core-banking/endpoint/<int:endpoint_id>', methods=['GET'])
@login_required
@admin_required
def get_endpoint(endpoint_id):
    """Get endpoint details"""
    try:
        config = ConfigManager.get_endpoint_config(endpoint_id)
        return config
    except Exception as e:
        return {'error': str(e)}, 404

@admin_bp.route('/core-banking/endpoint/<int:endpoint_id>', methods=['POST'])
@login_required
@admin_required
def update_endpoint(endpoint_id):
    """Update an endpoint"""
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'message': 'No data provided'}, 400

        endpoint = ConfigManager.update_endpoint(endpoint_id, **data)
        return {'success': True, 'endpoint': {
            'id': endpoint.id,
            'name': endpoint.name
        }}
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@admin_bp.route('/core-banking/endpoint/<int:endpoint_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_endpoint(endpoint_id):
    """Delete an endpoint"""
    try:
        ConfigManager.update_endpoint(endpoint_id, is_active=False)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@admin_bp.route('/core-banking/endpoint/<int:endpoint_id>/test', methods=['POST'])
@login_required
@admin_required
def test_endpoint(endpoint_id):
    """Test an endpoint"""
    try:
        endpoint = CoreBankingEndpoint.query.get(endpoint_id)
        if not endpoint:
            return {'success': False, 'message': 'Endpoint not found'}, 404

        api_manager = APIManager(endpoint.system_id)
        response = api_manager.make_request(endpoint_id)
        
        return {
            'success': True,
            'data': response
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@admin_bp.route('/core-banking/log/<int:log_id>', methods=['GET'])
@login_required
@admin_required
def get_log(log_id):
    """Get log details"""
    try:
        log = CoreBankingLog.query.get(log_id)
        if not log:
            return {'error': 'Log not found'}, 404

        return {
            'id': log.id,
            'request_method': log.request_method,
            'request_url': log.request_url,
            'request_headers': log.request_headers,
            'request_body': log.request_body,
            'response_status': log.response_status,
            'response_body': log.response_body,
            'error_message': log.error_message,
            'created_at': log.created_at.isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500
