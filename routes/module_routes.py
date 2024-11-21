from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from services.module_service import ModuleService
from flask_login import login_required
from decorators import admin_required

module_bp = Blueprint('modules', __name__)

@module_bp.route('/admin/modules', methods=['GET'])
@login_required
@admin_required
def list_modules():
    client_modules = ModuleService.get_modules_by_type('client')
    loan_modules = ModuleService.get_modules_by_type('loan')
    return render_template(
        'admin/modules/list.html',
        client_modules=client_modules,
        loan_modules=loan_modules
    )

@module_bp.route('/admin/modules/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_module():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        module_type = request.form.get('module_type')
        parent_id = request.form.get('parent_id')
        
        if parent_id:
            parent_id = int(parent_id)
        
        module = ModuleService.create_module(
            name=name,
            description=description,
            module_type=module_type,
            parent_id=parent_id
        )
        
        if module:
            flash('Module created successfully!', 'success')
            return redirect(url_for('modules.list_modules'))
        flash('Failed to create module.', 'error')
    
    # For GET request, show the create form
    parent_modules = ModuleService.get_root_modules()
    return render_template(
        'admin/modules/create.html',
        parent_modules=parent_modules
    )

@module_bp.route('/admin/modules/<int:module_id>/fields', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_fields(module_id):
    module = ModuleService.get_module_by_id(module_id)
    if not module:
        flash('Module not found.', 'error')
        return redirect(url_for('modules.list_modules'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        label = request.form.get('label')
        field_type = request.form.get('field_type')
        required = request.form.get('required') == 'on'
        options = request.form.get('options')  # Assuming JSON string for select options
        validation_rules = request.form.get('validation_rules')  # Assuming JSON string
        
        field = ModuleService.add_field_to_module(
            module_id=module_id,
            name=name,
            label=label,
            field_type=field_type,
            required=required,
            options=options,
            validation_rules=validation_rules
        )
        
        if field:
            flash('Field added successfully!', 'success')
        else:
            flash('Failed to add field.', 'error')
    
    return render_template(
        'admin/modules/fields.html',
        module=module
    )

@module_bp.route('/admin/modules/<int:module_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_module(module_id):
    success = ModuleService.delete_module(module_id)
    return jsonify({'success': success})
