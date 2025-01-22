from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
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
import json
from models.letter_template import LetterType, LetterTemplate
from forms.letter_template_forms import LetterTypeForm, LetterTemplateForm
from sqlalchemy.orm import joinedload
from models.credit_bureau import CreditBureau
from forms.credit_bureau_forms import CreditBureauForm

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
        print(f"Loading system details for ID: {system_id}")
        # Get system details
        system = DatabaseManager.get_system_by_id(system_id)
        if not system:
            print(f"System not found with ID: {system_id}")
            flash('Banking system not found', 'error')
            return redirect(url_for('admin.core_banking'))

        print(f"Found system: {system.name}")

        # Initialize empty data structures
        endpoints = []
        stats = {
            'total_requests': 0,
            'error_requests': 0,
            'success_rate': 0,
            'active_endpoints': 0
        }
        endpoint_stats = {}
        logs = []
        chart_labels = []
        chart_success_data = []
        chart_error_data = []

        try:
            # Get endpoints
            print("Fetching endpoints...")
            endpoints = DatabaseManager.get_system_endpoints(system_id)
            print(f"Found {len(endpoints)} endpoints")
            
            # Update active endpoints count
            stats['active_endpoints'] = len([e for e in endpoints if e.is_active])
        except Exception as e:
            print(f"Error getting endpoints: {str(e)}")
            import traceback
            print(traceback.format_exc())

        try:
            # Get system statistics
            print("Fetching system stats...")
            system_stats = DatabaseManager.get_system_stats(system_id)
            if system_stats:
                stats.update(system_stats)
        except Exception as e:
            print(f"Error getting system stats: {str(e)}")
            import traceback
            print(traceback.format_exc())

        try:
            # Get endpoint statistics
            print("Fetching endpoint stats...")
            for endpoint in endpoints:
                try:
                    endpoint_stats[endpoint.id] = DatabaseManager.get_endpoint_stats(endpoint.id)
                except Exception as e:
                    print(f"Error getting stats for endpoint {endpoint.id}: {str(e)}")
                    endpoint_stats[endpoint.id] = {
                        'total_requests': 0,
                        'error_requests': 0,
                        'success_rate': 0
                    }
        except Exception as e:
            print(f"Error getting endpoint stats: {str(e)}")
            import traceback
            print(traceback.format_exc())

        try:
            # Get recent logs
            print("Fetching recent logs...")
            logs = DatabaseManager.get_logs(system_id=system_id, limit=50)
            print(f"Found {len(logs)} logs")
        except Exception as e:
            print(f"Error getting logs: {str(e)}")
            import traceback
            print(traceback.format_exc())

        # Prepare chart data
        print("Preparing chart data...")
        from datetime import datetime, timedelta
        today = datetime.utcnow()
        dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        dates.reverse()
        chart_labels = dates

        for date in dates:
            try:
                day_logs = DatabaseManager.get_logs(
                    system_id=system_id,
                    start_date=f"{date} 00:00:00",
                    end_date=f"{date} 23:59:59"
                )
                success_count = len([l for l in day_logs if l.response_status and l.response_status < 400])
                error_count = len([l for l in day_logs if not l.response_status or l.response_status >= 400])
            except Exception as e:
                print(f"Error getting logs for date {date}: {str(e)}")
                success_count = 0
                error_count = 0
            
            chart_success_data.append(success_count)
            chart_error_data.append(error_count)

        print("Rendering template...")
        return render_template('admin/core_banking/view.html',
                             system=system,
                             endpoints=endpoints,
                             stats=stats,
                             endpoint_stats=endpoint_stats,
                             logs=logs,
                             chart_labels=chart_labels,
                             chart_success_data=chart_success_data,
                             chart_error_data=chart_error_data)
    except Exception as e:
        import traceback
        print(f"Error in view_system: {str(e)}")
        print(traceback.format_exc())
        flash(f'Error loading system details: {str(e)}', 'error')
        return redirect(url_for('admin.core_banking'))

@admin_bp.route('/api/core-banking/system/<int:system_id>')
@login_required
@admin_required
def get_system_details(system_id):
    """Get core banking system details as JSON"""
    try:
        # Get system details
        system = DatabaseManager.get_system_by_id(system_id)
        if not system:
            return jsonify({
                'status': 'error',
                'message': 'Banking system not found'
            }), 404

        # Get endpoints
        endpoints = DatabaseManager.get_system_endpoints(system_id)
        
        # Get system statistics
        stats = DatabaseManager.get_system_stats(system_id)
        if not stats:
            stats = {
                'total_requests': 0,
                'error_requests': 0,
                'success_rate': 0,
                'active_endpoints': len([e for e in endpoints if e.is_active])
            }

        # Get endpoint statistics
        endpoint_stats = {}
        for endpoint in endpoints:
            try:
                endpoint_stats[endpoint.id] = DatabaseManager.get_endpoint_stats(endpoint.id)
            except Exception as e:
                print(f"Error getting stats for endpoint {endpoint.id}: {str(e)}")
                endpoint_stats[endpoint.id] = {
                    'total_requests': 0,
                    'error_requests': 0,
                    'success_rate': 0
                }

        # Get recent logs
        logs = DatabaseManager.get_logs(system_id=system_id, limit=50)

        # Prepare chart data
        print("Preparing chart data...")
        from datetime import datetime, timedelta
        today = datetime.utcnow()
        dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        dates.reverse()
        chart_labels = dates

        chart_success_data = []
        chart_error_data = []

        for date in dates:
            try:
                day_logs = DatabaseManager.get_logs(
                    system_id=system_id,
                    start_date=f"{date} 00:00:00",
                    end_date=f"{date} 23:59:59"
                )
                success_count = len([l for l in day_logs if l.response_status and l.response_status < 400])
                error_count = len([l for l in day_logs if not l.response_status or l.response_status >= 400])
            except Exception as e:
                print(f"Error getting logs for date {date}: {str(e)}")
                success_count = 0
                error_count = 0
            
            chart_success_data.append(success_count)
            chart_error_data.append(error_count)

        # Convert system object to dict for JSON serialization
        system_dict = {
            'id': system.id,
            'name': system.name,
            'base_url': system.base_url,
            'port': system.port,
            'description': system.description,
            'auth_type': system.auth_type,
            'is_active': system.is_active,
            'created_at': system.created_at.isoformat() if system.created_at else None,
            'updated_at': system.updated_at.isoformat() if system.updated_at else None
        }

        # Convert logs to dict for JSON serialization
        logs_list = [{
            'id': log.id,
            'endpoint_id': log.endpoint_id,
            'request_method': log.request_method,
            'request_url': log.request_url,
            'response_status': log.response_status,
            'error_message': log.error_message,
            'created_at': log.created_at.isoformat() if log.created_at else None
        } for log in logs]

        # Convert endpoints to dict for JSON serialization
        endpoints_list = [{
            'id': e.id,
            'name': e.name,
            'path': e.path,
            'method': e.method,
            'description': e.description,
            'parameters': json.loads(e.parameters) if e.parameters else {},
            'headers': json.loads(e.headers) if e.headers else {},
            'is_active': e.is_active,
            'created_at': e.created_at.isoformat() if e.created_at else None,
            'updated_at': e.updated_at.isoformat() if e.updated_at else None
        } for e in endpoints]

        return jsonify({
            'status': 'success',
            'data': {
                'system': system_dict,
                'endpoints': endpoints_list,
                'stats': stats,
                'endpoint_stats': endpoint_stats,
                'logs': logs_list,
                'chart_data': {
                    'labels': chart_labels,
                    'success_data': chart_success_data,
                    'error_data': chart_error_data
                }
            }
        })
    except Exception as e:
        print(f"Error in get_system_details: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

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

@admin_bp.route('/core-banking/system/<int:system_id>')
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

@admin_bp.route('/letter-types', methods=['GET', 'POST'])
@login_required
@admin_required
def list_types():
    """
    List and create letter types
    """
    form = LetterTypeForm()
    
    if form.validate_on_submit():
        try:
            # Create new letter type
            new_letter_type = LetterType(
                name=form.name.data,
                description=form.description.data,
                is_active=form.is_active.data
            )
            db.session.add(new_letter_type)
            db.session.commit()
            flash('Letter type created successfully!', 'success')
            return redirect(url_for('admin.list_types'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating letter type: {str(e)}', 'danger')
    
    # Fetch existing letter types
    letter_types = LetterType.query.all()
    
    return render_template('admin/letter_types.html', 
                           form=form, 
                           letter_types=letter_types)

@admin_bp.route('/letter-types/edit/<int:type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_type(type_id):
    """
    Edit an existing letter type
    """
    letter_type = LetterType.query.get_or_404(type_id)
    form = LetterTypeForm(obj=letter_type)
    
    if form.validate_on_submit():
        try:
            # Update letter type
            form.populate_obj(letter_type)
            db.session.commit()
            flash('Letter type updated successfully!', 'success')
            return redirect(url_for('admin.list_types'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating letter type: {str(e)}', 'danger')
    
    return render_template('admin/edit_letter_type.html', 
                           form=form, 
                           letter_type=letter_type)

@admin_bp.route('/letter-templates', methods=['GET', 'POST'])
@login_required
@admin_required
def list_templates():
    """
    List and create letter templates
    """
    form = LetterTemplateForm()
    
    # Get optional letter_type_id from query parameter
    letter_type_id = request.args.get('letter_type_id', type=int)
    
    # Populate letter type choices dynamically
    letter_types = LetterType.query.filter_by(is_active=True).all()
    form.letter_type_id.choices = [(type.id, type.name) for type in letter_types]
    
    # If letter_type_id is provided, pre-select it in the form
    if letter_type_id and any(type.id == letter_type_id for type in letter_types):
        form.letter_type_id.data = letter_type_id
    
    if form.validate_on_submit():
        try:
            # Create new letter template
            new_template = LetterTemplate(
                letter_type_id=form.letter_type_id.data,
                name=form.name.data,
                template_content=form.template_content.data,
                is_active=form.is_active.data
            )
            db.session.add(new_template)
            db.session.commit()
            flash('Letter template created successfully!', 'success')
            return redirect(url_for('admin.list_templates'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating letter template: {str(e)}', 'danger')
    
    # Fetch existing letter templates with their associated letter types
    letter_templates = LetterTemplate.query.options(joinedload(LetterTemplate.letter_type)).all()
    
    return render_template('admin/letter_templates.html', 
                           form=form, 
                           letter_templates=letter_templates)

@admin_bp.route('/letter-templates/edit/<int:template_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_template(template_id):
    """
    Edit an existing letter template
    """
    letter_template = LetterTemplate.query.get_or_404(template_id)
    form = LetterTemplateForm(obj=letter_template)
    
    # Populate letter type choices dynamically
    form.letter_type_id.choices = [(type.id, type.name) for type in LetterType.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        try:
            # Update letter template
            form.populate_obj(letter_template)
            db.session.commit()
            flash('Letter template updated successfully!', 'success')
            return redirect(url_for('admin.list_templates'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating letter template: {str(e)}', 'danger')
    
    return render_template('admin/edit_letter_template.html', 
                           form=form, 
                           letter_template=letter_template)

@admin_bp.route('/letter-templates/by-type/<int:letter_type_id>')
@login_required
def get_templates_by_type(letter_type_id):
    """
    Get letter templates for a specific letter type
    """
    templates = LetterTemplate.query.filter_by(
        letter_type_id=letter_type_id, 
        is_active=True
    ).all()
    
    return jsonify([
        {
            'id': template.id, 
            'name': template.name
        } for template in templates
    ])

# Credit Bureau Configuration Routes
@admin_bp.route('/credit-bureau')
@login_required
@admin_required
def credit_bureau():
    """Render the credit bureau configuration page"""
    form = CreditBureauForm()
    configurations = CreditBureau.query.all()
    return render_template('admin/credit_bureau.html', form=form, configurations=configurations)

@admin_bp.route('/credit-bureau/add', methods=['POST'])
@login_required
@admin_required
def add_credit_bureau():
    """Add a new credit bureau configuration"""
    form = CreditBureauForm()
    
    if form.validate_on_submit():
        try:
            config = CreditBureau(
                name=form.name.data,
                provider=form.provider.data,
                base_url=form.base_url.data,
                api_key=form.api_key.data,
                username=form.username.data,
                password=form.password.data,
                is_active=form.is_active.data
            )
            db.session.add(config)
            db.session.commit()
            
            flash('Configuration added successfully!', 'success')
            return redirect(url_for('admin.credit_bureau'))
            
        except Exception as e:
            current_app.logger.error(f"Error adding configuration: {str(e)}")
            db.session.rollback()
            flash('Failed to add configuration. Please try again.', 'error')
    
    return render_template('admin/credit_bureau.html', form=form)

@admin_bp.route('/credit-bureau/<int:config_id>')
@login_required
@admin_required
def get_credit_bureau(config_id):
    """Get a specific credit bureau configuration"""
    config = CreditBureau.query.get_or_404(config_id)
    return jsonify({
        'id': config.id,
        'name': config.name,
        'provider': config.provider,
        'base_url': config.base_url,
        'api_key': config.api_key,
        'username': config.username,
        'is_active': config.is_active
    })

@admin_bp.route('/credit-bureau/<int:config_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_credit_bureau(config_id):
    """Edit a credit bureau configuration"""
    config = CreditBureau.query.get_or_404(config_id)
    form = CreditBureauForm()
    
    if form.validate_on_submit():
        try:
            config.name = form.name.data
            config.provider = form.provider.data
            config.base_url = form.base_url.data
            config.api_key = form.api_key.data
            config.username = form.username.data
            if form.password.data:  # Only update password if provided
                config.password = form.password.data
            config.is_active = form.is_active.data
            
            db.session.commit()
            flash('Configuration updated successfully!', 'success')
            return redirect(url_for('admin.credit_bureau'))
            
        except Exception as e:
            current_app.logger.error(f"Error updating configuration: {str(e)}")
            db.session.rollback()
            flash('Failed to update configuration. Please try again.', 'error')
    
    return render_template('admin/credit_bureau.html', form=form)

@admin_bp.route('/credit-bureau/<int:config_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_credit_bureau(config_id):
    """Toggle a configuration's active status"""
    try:
        config = CreditBureau.query.get_or_404(config_id)
        config.is_active = not config.is_active
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Configuration {"activated" if config.is_active else "deactivated"} successfully'
        })
    except Exception as e:
        current_app.logger.error(f"Error toggling configuration: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update configuration status'
        }), 500

@admin_bp.route('/credit-bureau/active')
@login_required
@admin_required
def get_active_credit_bureau():
    """Get the currently active credit bureau configuration"""
    config = CreditBureau.query.filter_by(is_active=True).first()
    if not config:
        return jsonify({'error': 'No active configuration found'}), 404
        
    return jsonify({
        'id': config.id,
        'name': config.name,
        'provider': config.provider,
        'base_url': config.base_url,
        'api_key': config.api_key,
        'username': config.username
    })
