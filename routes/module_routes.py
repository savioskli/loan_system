from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from services.module_service import ModuleService
from forms.module_forms import ModuleForm, FormFieldForm, DynamicFormFieldForm
from models.form_section import FormSection
from flask_login import login_required
from decorators import admin_required
import json

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

@module_bp.route('/admin/modules/<int:id>/fields/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_field(id):
    module = ModuleService.get_module_by_id(id)
    if not module:
        flash('Module not found.', 'error')
        return redirect(url_for('modules.list_modules'))

    form = DynamicFormFieldForm(module_id=id)
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Process options if field type requires them
            options = None
            if form.field_type.data in ['select', 'radio', 'checkbox'] and form.options:
                options = [{'label': opt.label.data, 'value': opt.value.data} 
                          for opt in form.options if opt.label.data and opt.value.data]

            # Get client type restrictions
            client_type_restrictions = form.client_type_restrictions.data if form.client_type_restrictions.data else None

            # Get section ID (0 means no section)
            section_id = form.section_id.data if form.section_id.data and form.section_id.data != 0 else None

            field = ModuleService.add_field_to_module(
                module_id=id,
                name=form.field_name.data,
                label=form.field_label.data,
                field_type=form.field_type.data,
                required=form.is_required.data,
                options=options,
                validation_rules=json.loads(form.validation_rules.data) if form.validation_rules.data else None,
                section_id=section_id,
                client_type_restrictions=client_type_restrictions
            )
            
            if field:
                flash('Field created successfully!', 'success')
                return redirect(url_for('modules.list_fields', id=id))
            else:
                flash('Failed to create field.', 'error')
        except Exception as e:
            flash(f'Error creating field: {str(e)}', 'error')

    return render_template(
        'admin/modules/field_form.html',
        form=form,
        module=module,
        title='Create Form Field'
    )

@module_bp.route('/admin/modules/<int:id>/fields/<int:field_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_field(id, field_id):
    module = ModuleService.get_module_by_id(id)
    if not module:
        flash('Module not found.', 'error')
        return redirect(url_for('modules.list_modules'))

    field = ModuleService.get_field_by_id(field_id)
    if not field:
        flash('Field not found.', 'error')
        return redirect(url_for('modules.list_fields', id=id))

    form = DynamicFormFieldForm(module_id=id, obj=field)
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Process options if field type requires them
            options = None
            if form.field_type.data in ['select', 'radio', 'checkbox'] and form.options:
                options = [{'label': opt.label.data, 'value': opt.value.data} 
                          for opt in form.options if opt.label.data and opt.value.data]

            # Get client type restrictions
            client_type_restrictions = form.client_type_restrictions.data if form.client_type_restrictions.data else None

            # Get section ID (0 means no section)
            section_id = form.section_id.data if form.section_id.data and form.section_id.data != 0 else None

            # Update field data
            field_data = {
                'name': form.field_name.data,
                'label': form.field_label.data,
                'field_type': form.field_type.data,
                'required': form.is_required.data,
                'options': options,
                'validation_rules': json.loads(form.validation_rules.data) if form.validation_rules.data else None,
                'section_id': section_id,
                'client_type_restrictions': client_type_restrictions
            }

            updated_field = ModuleService.update_field(field_id, field_data)
            
            if updated_field:
                flash('Field updated successfully!', 'success')
                return redirect(url_for('modules.list_fields', id=id))
            else:
                flash('Failed to update field.', 'error')
        except Exception as e:
            flash(f'Error updating field: {str(e)}', 'error')

    return render_template(
        'admin/modules/field_form.html',
        form=form,
        module=module,
        field_id=field_id,
        title='Edit Form Field'
    )

@module_bp.route('/admin/modules/<int:id>/fields', methods=['GET'])
@login_required
@admin_required
def list_fields(id):
    module = ModuleService.get_module_by_id(id)
    if not module:
        flash('Module not found.', 'error')
        return redirect(url_for('modules.list_modules'))
    
    return render_template(
        'admin/modules/list_fields.html',
        module=module
    )

@module_bp.route('/admin/modules/<int:module_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_module(module_id):
    success = ModuleService.delete_module(module_id)
    return jsonify({'success': success})
