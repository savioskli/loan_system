from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models.module import Module, FormField
from models.client_type import ClientType
from forms.module_forms import ModuleForm, FormFieldForm, DynamicFormFieldForm
from extensions import db
from models.role import Role
from utils.module_utils import generate_module_code
from utils.dynamic_tables import create_or_update_module_table
import json
import traceback
from datetime import datetime

modules_bp = Blueprint('modules', __name__)

@modules_bp.route('/')
@login_required
def index():
    print(f"Current user: {current_user.username}")
    print(f"Current user role ID: {current_user.role_id}")
    print(f"Current user role: {current_user.role}")
    if current_user.role:
        print(f"Role name: {current_user.role.name}")
    
    # List all roles
    all_roles = Role.query.all()
    print("Available roles:")
    for role in all_roles:
        print(f"- {role.name} (ID: {role.id})")
    
    if not current_user.role or current_user.role.name.lower() != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    # Get all modules and organize them hierarchically
    def build_module_tree(modules, parent_id=None):
        tree = []
        for module in modules:
            if module.parent_id == parent_id:
                # Get all children for this module
                children = build_module_tree(modules, module.id)
                if children:
                    module.children = children
                tree.append(module)
        return tree

    all_modules = Module.query.order_by(Module.name).all()
    modules = build_module_tree(all_modules)
    return render_template('admin/modules/index.html', modules=modules)

@modules_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.role or current_user.role.name.lower() != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
        
    form = ModuleForm()
    print("Form created")
    
    if form.validate_on_submit():
        try:
            print("Form validated")
            # Generate the module code
            parent_id = form.parent_id.data if form.parent_id.data != 0 else None
            code = generate_module_code(form.name.data, parent_id)
            
            module = Module(
                name=form.name.data,
                code=code,
                description=form.description.data,
                parent_id=parent_id,
                is_active=form.is_active.data
            )
            print(f"Module created: {module}")
            db.session.add(module)
            db.session.commit()
            print("Module saved to database")
            
            # Create the dynamic form data table
            if create_or_update_module_table(code):
                print(f"Created dynamic form data table for module {code}")
                flash('Module and form data table created successfully.', 'success')
            else:
                print(f"Failed to create dynamic form data table for module {code}")
                flash('Module created but form data table creation failed.', 'error')
            
            return redirect(url_for('modules.index'))
        except Exception as e:
            print(f"Error creating module: {str(e)}")
            db.session.rollback()
            flash('Error creating module. Please try again.', 'error')
    elif form.errors:
        print(f"Form validation errors: {form.errors}")
    
    return render_template('admin/modules/form.html', form=form, title='Create Module')

@modules_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not current_user.role or current_user.role.name.lower() != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
        
    module = Module.query.get_or_404(id)
    form = ModuleForm(obj=module)
    
    if form.validate_on_submit():
        try:
            # Update basic info
            module.name = form.name.data
            module.description = form.description.data
            new_parent_id = form.parent_id.data if form.parent_id.data != 0 else None
            
            # If parent changed, regenerate code
            if new_parent_id != module.parent_id:
                module.code = generate_module_code(module.name, new_parent_id)
                module.parent_id = new_parent_id
            
            module.is_active = form.is_active.data
            
            db.session.commit()
            flash('Module updated successfully.', 'success')
            return redirect(url_for('modules.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating module: {str(e)}', 'error')
            
    return render_template('admin/modules/form.html', form=form, title='Edit Module')

@modules_bp.route('/<int:id>/fields', methods=['GET'])
@login_required
def list_fields(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    module = Module.query.get_or_404(id)
    fields = FormField.query.filter_by(module_id=id).order_by(FormField.field_order).all()
    
    # Get client type names for each field's restrictions
    for field in fields:
        if field.client_type_restrictions:
            client_types = ClientType.query.filter(ClientType.id.in_(field.client_type_restrictions)).all()
            field.client_type_names = [ct.client_name for ct in client_types]
        else:
            field.client_type_names = []
        current_app.logger.debug(f"Field {field.field_name} restrictions: {field.client_type_restrictions}, Names: {field.client_type_names}")
    
    return render_template('admin/modules/fields.html', module=module, fields=fields)

@modules_bp.route('/<int:id>/fields/get', methods=['GET'])
@login_required
def get_module_fields(id):
    """Get all fields for a module"""
    module = Module.query.get_or_404(id)
    fields = FormField.query.filter_by(module_id=id).all()
    return jsonify([{
        'id': field.id,
        'field_name': field.field_name,
        'field_type': field.field_type
    } for field in fields])

@modules_bp.route('/<int:id>/fields/create', methods=['GET', 'POST'])
@login_required
def create_field(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        module = Module.query.get_or_404(id)
        
        # Use basic form for GET requests
        if request.method == 'GET':
            form = FormFieldForm(module_id=id)
            current_app.logger.info("GET request - Creating new form")
            return render_template('admin/modules/field_form.html', form=form, module=module)
        
        # For POST requests
        current_app.logger.debug(f"Form Data: {request.form}")
        
        field_type = request.form.get('field_type', '')
        field_data = {
            'field_name': request.form.get('field_name'),
            'field_label': request.form.get('field_label'),
            'field_placeholder': request.form.get('field_placeholder'),
            'field_type': field_type,
            'validation_text': request.form.get('validation_text'),
            'is_required': request.form.get('is_required') == 'y',
            'client_type_restrictions': request.form.getlist('client_type_restrictions') if request.form.getlist('client_type_restrictions') else [],
            'section_id': request.form.get('section_id', type=int)
        }
        
        # Get options from the form
        options = []
        i = 0
        while True:
            label_key = f'options-{i}-form-label'
            value_key = f'options-{i}-form-value'
            
            if label_key not in request.form and f'options-{i}-label' not in request.form:
                break
                
            label = request.form.get(label_key, '').strip() or request.form.get(f'options-{i}-label', '').strip()
            value = request.form.get(value_key, '').strip() or request.form.get(f'options-{i}-value', '').strip()
            
            if label and value:
                options.append({
                    'label': label,
                    'value': value
                })
            
            i += 1
        
        if field_type in ['select', 'radio', 'checkbox'] and not options:
            flash('Please add at least one option for this field type.', 'error')
            form = FormFieldForm(data=field_data, module_id=id)
            return render_template('admin/modules/field_form.html', form=form, module=module)
        
        # Get the highest current order
        max_order = db.session.query(db.func.max(FormField.field_order)).filter_by(module_id=id).scalar() or 0
        
        # Create new field
        field = FormField(
            module_id=id,
            field_name=field_data['field_name'],
            field_label=field_data['field_label'],
            field_placeholder=field_data['field_placeholder'],
            field_type=field_data['field_type'],
            validation_text=field_data['validation_text'],
            is_required=field_data['is_required'],
            field_order=max_order + 1,
            client_type_restrictions=[int(x) for x in field_data['client_type_restrictions']],
            section_id=field_data['section_id'] if field_data['section_id'] != 0 else None
        )
        
        if field_type in ['select', 'radio', 'checkbox']:
            field.options = options
        
        current_app.logger.debug(f"Creating field with data:")
        current_app.logger.debug(f"- Name: {field.field_name}")
        current_app.logger.debug(f"- Type: {field.field_type}")
        current_app.logger.debug(f"- Client Type Restrictions: {field.client_type_restrictions}")
        
        db.session.add(field)
        db.session.commit()
        
        # Update the module's table schema
        current_app.logger.info(f"Updating table schema for module {module.code}")
        if not create_or_update_module_table(module.code):
            raise Exception("Failed to update table schema")
        current_app.logger.info("Table schema updated successfully")
        
        flash('Field created successfully!', 'success')
        return redirect(url_for('modules.list_fields', id=id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating field: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while creating the field', 'error')
        form = FormFieldForm(data=field_data, module_id=id) if 'field_data' in locals() else FormFieldForm(module_id=id)
        return render_template('admin/modules/field_form.html', form=form, module=module)

@modules_bp.route('/<int:id>/fields/<int:field_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_field(id, field_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        module = Module.query.get_or_404(id)
        field = FormField.query.get_or_404(field_id)
        
        if request.method == 'GET':
            form = FormFieldForm(obj=field, module_id=id)
            return render_template('admin/modules/field_form.html', form=form, module=module, field=field)
        
        # For POST requests
        form = FormFieldForm(module_id=id)
        field_type = request.form.get('field_type', '')
        field_data = {
            'field_name': request.form.get('field_name'),
            'field_label': request.form.get('field_label'),
            'field_placeholder': request.form.get('field_placeholder'),
            'field_type': field_type,
            'validation_text': request.form.get('validation_text'),
            'is_required': request.form.get('is_required') == 'y',
            'client_type_restrictions': request.form.getlist('client_type_restrictions') if request.form.getlist('client_type_restrictions') else [],
            'section_id': request.form.get('section_id', type=int)
        }
        
        # Get options from the form
        options = []
        i = 0
        while True:
            label_key = f'options-{i}-form-label'
            value_key = f'options-{i}-form-value'
            
            if label_key not in request.form and f'options-{i}-label' not in request.form:
                break
                
            label = request.form.get(label_key, '').strip() or request.form.get(f'options-{i}-label', '').strip()
            value = request.form.get(value_key, '').strip() or request.form.get(f'options-{i}-value', '').strip()
            
            if label and value:
                options.append({
                    'label': label,
                    'value': value
                })
            
            i += 1
        
        if field_type in ['select', 'radio', 'checkbox'] and not options:
            flash('Please add at least one option for this field type.', 'error')
            form = FormFieldForm(data=field_data, module_id=id)
            return render_template('admin/modules/field_form.html', form=form, module=module, field=field)
        
        # Update field
        field.field_name = field_data['field_name']
        field.field_label = field_data['field_label']
        field.field_placeholder = field_data['field_placeholder']
        field.field_type = field_data['field_type']
        field.validation_text = field_data['validation_text']
        field.is_required = field_data['is_required']
        field.section_id = field_data['section_id'] if field_data['section_id'] != 0 else None
        field.client_type_restrictions = [int(x) for x in field_data['client_type_restrictions']]
        
        if field_type in ['select', 'radio', 'checkbox']:
            field.options = options
        else:
            field.options = None
        
        db.session.commit()
        
        # Update the module's table schema
        current_app.logger.info(f"Updating table schema for module {module.code}")
        if not create_or_update_module_table(module.code):
            raise Exception("Failed to update table schema")
        current_app.logger.info("Table schema updated successfully")
        
        flash('Field updated successfully.', 'success')
        return redirect(url_for('modules.list_fields', id=module.id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating field: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while updating the field', 'error')
        return render_template('admin/modules/field_form.html', form=form, module=module, field=field)

@modules_bp.route('/<int:id>/fields/order', methods=['POST'])
@login_required
def update_field_order(id):
    if not current_user.role or current_user.role.name.lower() != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
        
    try:
        data = request.get_json()
        fields = data.get('fields', [])
        
        # Update each field's order
        for field_data in fields:
            field = FormField.query.get(field_data['id'])
            if field and field.module_id == id:  # Ensure field belongs to current module
                field.field_order = field_data['order']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@modules_bp.route('/<int:id>/fields/<int:field_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_field(id, field_id):
    current_app.logger.info(f"Delete field request received - Module ID: {id}, Field ID: {field_id}")
    
    if not current_user.is_admin:
        current_app.logger.warning(f"Non-admin user {current_user.id} attempted to delete field {field_id}")
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        current_app.logger.debug(f"Attempting to fetch field {field_id}")
        field = FormField.query.get_or_404(field_id)
        
        # Verify the field belongs to the module
        if field.module_id != id:
            current_app.logger.warning(f"Field {field_id} does not belong to module {id}")
            flash('Invalid field ID.', 'error')
            return redirect(url_for('modules.list_fields', id=id))
        
        current_app.logger.info(f"Deleting field {field_id} from module {id}")
        # Store module_id before deletion for redirect
        module_id = field.module_id
        
        # Get the module
        module = Module.query.get_or_404(id)
        
        # Store module code before deletion
        module_code = module.code
        
        # Delete the field
        db.session.delete(field)
        db.session.commit()
        
        current_app.logger.info(f"Field {field_id} deleted successfully")
        
        # Update the module's table schema to remove the column
        current_app.logger.info(f"Updating table schema for module {module_code}")
        if not create_or_update_module_table(module_code):
            raise Exception("Failed to update table schema")
        current_app.logger.info("Table schema updated successfully")
        
        flash('Field deleted successfully.', 'success')
        return redirect(url_for('modules.list_fields', id=module_id))
        
    except Exception as e:
        current_app.logger.error(f"Error deleting field {field_id}: {str(e)}", exc_info=True)
        db.session.rollback()
        flash(f'An error occurred while deleting the field.', 'error')
        return redirect(url_for('modules.list_fields', id=id))

@modules_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    print(f"\n=== Starting module deletion process ===")
    print(f"Delete request received for module ID: {id}")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    
    if not current_user.is_admin:
        print(f"Permission denied for user: {current_user}")
        return jsonify({
            'success': False,
            'message': 'You do not have permission to delete modules.'
        }), 403

    try:
        # Get the module first to check if it exists
        module = Module.query.get(id)
        if not module:
            print(f"Module not found: {id}")
            return jsonify({
                'success': False,
                'message': f'Module with ID {id} not found.'
            }), 404
            
        module_name = module.name
        print(f"\nModule found: {module_name} (ID: {id})")
        
        # Get counts for logging
        child_form_fields = db.session.query(FormField).join(Module, Module.id == FormField.module_id)\
            .filter(Module.parent_id == id).count()
        main_form_fields = db.session.query(FormField).filter(FormField.module_id == id).count()
        child_modules = db.session.query(Module).filter(Module.parent_id == id).count()
        
        print(f"Found {child_form_fields} child form fields, {main_form_fields} main form fields, {child_modules} child modules")
        
        # Delete form fields first
        print("1. Deleting form fields...")
        FormField.query.filter_by(module_id=id).delete(synchronize_session=False)
        
        # Delete child form fields
        print("2. Deleting child form fields...")
        child_modules_ids = [m.id for m in Module.query.filter_by(parent_id=id).all()]
        if child_modules_ids:
            FormField.query.filter(FormField.module_id.in_(child_modules_ids)).delete(synchronize_session=False)
        
        # Delete child modules
        print("3. Deleting child modules...")
        Module.query.filter_by(parent_id=id).delete(synchronize_session=False)
        
        # Finally delete the main module
        print("4. Deleting main module...")
        db.session.delete(module)
        
        # Commit the transaction
        db.session.commit()
        print("All deletions committed successfully")
        
        response_data = {
            'success': True,
            'message': f'Successfully deleted module "{module_name}" and all its dependencies ({child_modules} child modules, {child_form_fields + main_form_fields} form fields).'
        }
        print(f"Sending success response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print("\n=== Exception Details ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print("\nTraceback:")
        import traceback
        traceback.print_exc()
        
        # Ensure we have a clean session
        db.session.rollback()
        
        return jsonify({
            'success': False,
            'message': f"Failed to delete module: {str(e)}"
        }), 500
