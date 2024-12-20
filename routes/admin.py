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
