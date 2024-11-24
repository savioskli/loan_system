from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
import mysql.connector
from config import db_config
from functools import wraps

bp = Blueprint('is_admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add your admin check logic here
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    return mysql.connector.connect(**db_config)

@bp.route('/form-sections')
@login_required
@admin_required
def form_sections():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM form_sections ORDER BY name")
    sections = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/form_sections/index.html', sections=sections)

@bp.route('/form-sections/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_form_section():
    if request.method == 'POST':
        name = request.form['name']
        module = request.form['module']
        submodule = request.form['submodule']
        is_active = 'is_active' in request.form

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO form_sections (name, module, submodule, is_active) VALUES (%s, %s, %s, %s)",
                (name, module, submodule, is_active)
            )
            conn.commit()
            flash('Form section created successfully!', 'success')
            return redirect(url_for('is_admin.form_sections'))
        except Exception as e:
            conn.rollback()
            flash(f'Error creating form section: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

    # Get available modules and submodules
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT module FROM modules ORDER BY module")
    modules = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT submodule FROM modules ORDER BY submodule")
    submodules = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()

    return render_template('admin/form_sections/form.html', 
                         section=None, 
                         modules=modules,
                         submodules=submodules)

@bp.route('/form-sections/edit/<int:section_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_form_section(section_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        module = request.form['module']
        submodule = request.form['submodule']
        is_active = 'is_active' in request.form

        try:
            cursor.execute(
                "UPDATE form_sections SET name=%s, module=%s, submodule=%s, is_active=%s WHERE id=%s",
                (name, module, submodule, is_active, section_id)
            )
            conn.commit()
            flash('Form section updated successfully!', 'success')
            return redirect(url_for('is_admin.form_sections'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating form section: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

    # Get the current section data
    cursor.execute("SELECT * FROM form_sections WHERE id = %s", (section_id,))
    section = cursor.fetchone()

    if not section:
        cursor.close()
        conn.close()
        flash('Form section not found', 'error')
        return redirect(url_for('is_admin.form_sections'))

    # Get available modules and submodules
    cursor.execute("SELECT DISTINCT module FROM modules ORDER BY module")
    modules = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT submodule FROM modules ORDER BY submodule")
    submodules = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('admin/form_sections/form.html', 
                         section=section,
                         modules=modules,
                         submodules=submodules)

@bp.route('/form-sections/delete/<int:section_id>', methods=['POST'])
@login_required
@admin_required
def delete_form_section(section_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM form_sections WHERE id = %s", (section_id,))
        conn.commit()
        flash('Form section deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting form section: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('is_admin.form_sections'))
