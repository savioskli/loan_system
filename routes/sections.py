from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from utils.decorators import admin_required
from utils.db import get_db_connection

sections_bp = Blueprint('sections', __name__, url_prefix='/sections')

@sections_bp.route('/')
@login_required
@admin_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all form sections with their module names
    cursor.execute("""
        SELECT fs.*, m.name as module_name 
        FROM form_sections fs
        LEFT JOIN modules m ON fs.module_id = m.id 
        ORDER BY fs.name
    """)
    sections = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/sections/index.html', sections=sections)

@sections_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            name = request.form['name']
            module_id = request.form['module']
            description = request.form.get('description', '')
            is_active = 'is_active' in request.form
            
            cursor.execute(
                "INSERT INTO form_sections (name, module_id, description, is_active) VALUES (%s, %s, %s, %s)",
                (name, module_id, description, is_active)
            )
            
            conn.commit()
            flash('Form section created successfully!', 'success')
            return redirect(url_for('sections.index'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error creating form section: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    # Get available modules for the dropdown
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, name, parent_id 
        FROM modules 
        WHERE is_active = 1 
        ORDER BY name
    """)
    modules = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin/sections/form.html', section=None, modules=modules)

@sections_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            module_id = request.form['module']
            description = request.form.get('description', '')
            is_active = 'is_active' in request.form
            
            cursor.execute(
                "UPDATE form_sections SET name=%s, module_id=%s, description=%s, is_active=%s WHERE id=%s",
                (name, module_id, description, is_active, id)
            )
            
            conn.commit()
            flash('Form section updated successfully!', 'success')
            return redirect(url_for('sections.index'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error updating form section: {str(e)}', 'error')
    
    # Get the current section data
    cursor.execute("""
        SELECT fs.*, m.name as module_name 
        FROM form_sections fs
        LEFT JOIN modules m ON fs.module_id = m.id 
        WHERE fs.id = %s
    """, (id,))
    section = cursor.fetchone()
    
    if not section:
        cursor.close()
        conn.close()
        flash('Form section not found', 'error')
        return redirect(url_for('sections.index'))
    
    # Get available modules for the dropdown
    cursor.execute("""
        SELECT id, name, parent_id 
        FROM modules 
        WHERE is_active = 1 
        ORDER BY name
    """)
    modules = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/sections/form.html', section=section, modules=modules)

@sections_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the section exists
        cursor.execute("SELECT id FROM form_sections WHERE id = %s", (id,))
        if not cursor.fetchone():
            flash('Form section not found', 'error')
            return redirect(url_for('sections.index'))
        
        # Delete the section
        cursor.execute("DELETE FROM form_sections WHERE id = %s", (id,))
        conn.commit()
        flash('Form section deleted successfully!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting form section: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('sections.index'))
