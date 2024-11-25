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

@modules_bp.route('/<int:id>/fields/create', methods=['GET', 'POST'])
@login_required
def create_field(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        module = Module.query.get_or_404(id)
        field_type = request.form.get('field_type', '')
        
        # Use basic form for GET requests
        if request.method == 'GET':
            form = FormFieldForm(module_id=id)
            current_app.logger.info("GET request - Creating new form")
            current_app.logger.info(f"Client type choices: {form.client_type_restrictions.choices}")
            return render_template('admin/modules/field_form.html', form=form, module=module)
        
        # For POST requests
        current_app.logger.debug(f"Form Data: {request.form}")
        current_app.logger.debug(f"Client Type Restrictions: {request.form.getlist('client_type_restrictions')}")
        
        # Get the field data
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
        
        # Get options from the form with the template's naming convention
        options = []
        
        # Collect all options from the form data
        i = 0
        while True:
            label_key = f'options-{i}-form-label'
            value_key = f'options-{i}-form-value'
            
            if label_key not in request.form and f'options-{i}-label' not in request.form:  # No more options
                break
                    
            label = request.form.get(label_key, '').strip() or request.form.get(f'options-{i}-label', '').strip()
            value = request.form.get(value_key, '').strip() or request.form.get(f'options-{i}-value', '').strip()
            
            current_app.logger.debug(f"Processing option {i} - Label: {label}, Value: {value}")
            
            if label and value:  # Only add if both label and value are non-empty
                options.append({
                    'label': label,
                    'value': value
                })
                current_app.logger.debug(f"Added option {i}")
            
            i += 1
        
        current_app.logger.debug(f"Final collected options: {options}")
        field_data['options'] = options  # Add options to field_data
        
        # Create the appropriate form based on field type
        if field_type in ['select', 'radio', 'checkbox']:
            form = DynamicFormFieldForm(data=field_data, module_id=id)
            
            # Debug logging for form data
            current_app.logger.debug("Form Data:")
            for key, value in request.form.items():
                current_app.logger.debug(f"{key}: {value}")
            
            # Validate that we have at least one option for select/radio/checkbox fields
            if not options and field_type in ['select', 'radio', 'checkbox']:
                flash('Please add at least one option for this field type.', 'error')
                return render_template('admin/modules/field_form.html', form=form, module=module)
        else:
            form = FormFieldForm(data=field_data, module_id=id)
        
        if form.validate_on_submit():
            current_app.logger.debug("Form validated successfully")
            
            # Get the highest current order
            max_order = db.session.query(db.func.max(FormField.field_order)).filter_by(module_id=id).scalar() or 0
            
            field = FormField(
                module_id=id,
                field_name=form.field_name.data,
                field_label=form.field_label.data,
                field_placeholder=form.field_placeholder.data or '',
                field_type=form.field_type.data,
                validation_text=form.validation_text.data or '',
                is_required=form.is_required.data,
                field_order=max_order + 1,
                client_type_restrictions=list(map(int, form.client_type_restrictions.data)) if form.client_type_restrictions.data else [],
                section_id=form.section_id.data if form.section_id.data != 0 else None
            )
            
            current_app.logger.debug(f"Creating field with data:")
            current_app.logger.debug(f"- Name: {field.field_name}")
            current_app.logger.debug(f"- Type: {field.field_type}")
            current_app.logger.debug(f"- Client Type Restrictions: {field.client_type_restrictions}")
            
            # Handle options for select, radio, checkbox fields
            if field.field_type in ['select', 'radio', 'checkbox'] and hasattr(form, 'options'):
                current_app.logger.debug(f"Processing options for field type: {field.field_type}")
                current_app.logger.debug(f"Form options data: {form.options.data}")
                
                options = []
                for option in form.options.data:
                    current_app.logger.debug(f"Processing option: {option}")
                    if isinstance(option, dict) and option.get('label', '').strip() and option.get('value', '').strip():
                        options.append({
                            'label': option['label'].strip(),
                            'value': option['value'].strip()
                        })
                        current_app.logger.debug(f"Added option: {options[-1]}")
                
                if options:
                    current_app.logger.debug(f"Setting field options to: {options}")
                    field.options = options
                else:
                    current_app.logger.debug("No valid options found")
                    flash('Please add at least one option for this field type.', 'error')
                    return render_template('admin/modules/field_form.html', form=form, module=module)
            else:
                field.options = None
            
            current_app.logger.debug(f"After update - Field data: {field.__dict__}")
            
            try:
                current_app.logger.debug("Attempting to add field to database")
                current_app.logger.debug(f"Field data: {field.__dict__}")
                db.session.add(field)
                db.session.flush()  # Flush changes to get any DB-generated values
                current_app.logger.debug(f"After flush - Field options: {field.options}")
                db.session.commit()
                current_app.logger.debug("Database commit successful")
                current_app.logger.debug(f"Final field options: {field.options}")
                
                # Update the module's table schema
                current_app.logger.info(f"Updating table schema for module {module.code}")
                if not create_or_update_module_table(module.code):
                    raise Exception("Failed to update table schema")
                current_app.logger.info("Table schema updated successfully")
                
                flash('Field created successfully.', 'success')
                return redirect(url_for('modules.list_fields', id=module.id))
            except Exception as db_error:
                current_app.logger.error(f"Database error: {str(db_error)}")
                current_app.logger.error(traceback.format_exc())
                db.session.rollback()
                flash(f'Database error: {str(db_error)}', 'error')
        else:
            current_app.logger.debug(f"Form validation failed. Errors: {form.errors}")
            for field_name, errors in form.errors.items():
                for error in errors:
                    field_label = field_name
                    if hasattr(form, field_name):
                        field = getattr(form, field_name)
                        if hasattr(field, 'label') and hasattr(field.label, 'text'):
                            field_label = field.label.text
                    flash(f'{field_label}: {error}', 'error')
        
        return render_template('admin/modules/field_form.html', form=form, module=module)
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_field: {str(e)}")
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('modules.list_fields', id=id))

@modules_bp.route('/<int:id>/fields/<int:field_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_field(id, field_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get the field and verify it belongs to the module
        field = FormField.query.get_or_404(field_id)
        if field.module_id != id:
            flash('Invalid field ID.', 'error')
            return redirect(url_for('modules.list_fields', id=id))
        
        # For GET requests, initialize the form with field data
        if request.method == 'GET':
            current_app.logger.debug(f"GET request - Current field data: {field.__dict__}")
            current_app.logger.debug(f"Client type restrictions before conversion: {field.client_type_restrictions}")
            
            # Ensure client_type_restrictions is a list of integers
            client_type_restrictions = []
            if field.client_type_restrictions:
                if isinstance(field.client_type_restrictions, list):
                    client_type_restrictions = [int(x) for x in field.client_type_restrictions]
                elif isinstance(field.client_type_restrictions, str):
                    try:
                        import json
                        client_type_restrictions = [int(x) for x in json.loads(field.client_type_restrictions)]
                    except (json.JSONDecodeError, ValueError) as e:
                        current_app.logger.error(f"Error parsing client_type_restrictions: {e}")
            
            current_app.logger.debug(f"Client type restrictions after conversion: {client_type_restrictions}")
            
            form_data = {
                'field_name': field.field_name,
                'field_label': field.field_label,
                'field_placeholder': field.field_placeholder,
                'field_type': field.field_type,
                'validation_text': field.validation_text,
                'is_required': field.is_required,
                'client_type_restrictions': client_type_restrictions,
                'section_id': field.section_id if field.section_id is not None else 0
            }
            
            if field.field_type in ['select', 'radio', 'checkbox']:
                form = DynamicFormFieldForm(data=form_data, module_id=id)
                # Clear any existing options and add new ones
                while len(form.options) > 0:
                    form.options.pop_entry()
                
                # Debug logging for options
                current_app.logger.info(f"Field type: {field.field_type}")
                current_app.logger.info(f"Raw options data: {field.options}")
                current_app.logger.info(f"Options type: {type(field.options)}")
                
                # Add existing options
                if field.options:
                    try:
                        # Handle list of dicts (our standard format)
                        if isinstance(field.options, list) and all(isinstance(x, dict) for x in field.options):
                            current_app.logger.info("Processing list of dicts")
                            for option in field.options:
                                form.options.append_entry({
                                    'label': option.get('label', ''),
                                    'value': option.get('value', '')
                                })
                        # Handle string-keyed dict
                        elif isinstance(field.options, dict):
                            current_app.logger.info("Processing dict")
                            for value, label in field.options.items():
                                form.options.append_entry({
                                    'label': label if isinstance(label, str) else str(value),
                                    'value': str(value)
                                })
                        # Handle list of strings
                        elif isinstance(field.options, list):
                            current_app.logger.info("Processing list of strings")
                            for option in field.options:
                                if isinstance(option, str):
                                    form.options.append_entry({
                                        'label': option,
                                        'value': option
                                    })
                                elif isinstance(option, dict):
                                    form.options.append_entry({
                                        'label': option.get('label', ''),
                                        'value': option.get('value', '')
                                    })
                        
                        # Log the processed options
                        current_app.logger.info("Processed options:")
                        for option in form.options:
                            current_app.logger.info(f"Label: {option.label.data}, Value: {option.value.data}")
                            
                    except Exception as e:
                        current_app.logger.error(f"Error processing options: {str(e)}")
                        current_app.logger.debug(f"Options data: {field.options}")
            else:
                form = FormFieldForm(data=form_data, module_id=id)
            
            return render_template('admin/modules/field_form.html', form=form, module=field.parent_module, title='Edit Field', field_id=field_id)
        
        # For POST requests
        current_app.logger.debug(f"POST request - Form Data: {request.form}")
        field_type = request.form.get('field_type', '')
        
        # Get client type restrictions from form
        client_type_restrictions = request.form.getlist('client_type_restrictions')
        current_app.logger.debug(f"Received client type restrictions: {client_type_restrictions}")
        
        # Convert to integers and handle empty list
        if client_type_restrictions:
            client_type_restrictions = [int(x) for x in client_type_restrictions]
        else:
            client_type_restrictions = None
        
        # Get the field data
        field_data = {
            'field_name': request.form.get('field_name'),
            'field_label': request.form.get('field_label'),
            'field_placeholder': request.form.get('field_placeholder'),
            'field_type': field_type,
            'validation_text': request.form.get('validation_text'),
            'is_required': request.form.get('is_required') == 'y',
            'client_type_restrictions': client_type_restrictions,
            'section_id': request.form.get('section_id', type=int)
        }
        current_app.logger.debug(f"Field data to be updated: {field_data}")
        
        # Get options from the form with the template's naming convention
        options = []
        
        # Collect all options from the form data
        i = 0
        while True:
            label_key = f'options-{i}-form-label'
            value_key = f'options-{i}-form-value'
            
            if label_key not in request.form and f'options-{i}-label' not in request.form:  # No more options
                break
                    
            label = request.form.get(label_key, '').strip() or request.form.get(f'options-{i}-label', '').strip()
            value = request.form.get(value_key, '').strip() or request.form.get(f'options-{i}-value', '').strip()
            
            current_app.logger.debug(f"Processing option {i} - Label: {label}, Value: {value}")
            
            if label and value:  # Only add if both label and value are non-empty
                options.append({
                    'label': label,
                    'value': value
                })
                current_app.logger.debug(f"Added option {i}")
            
            i += 1
        
        current_app.logger.debug(f"Final collected options: {options}")
        field_data['options'] = options  # Add options to field_data
        
        # Create the appropriate form based on field type
        if field_type in ['select', 'radio', 'checkbox']:
            form = DynamicFormFieldForm(data=field_data, module_id=id)
            
            # Debug logging for form data
            current_app.logger.debug("Form Data:")
            for key, value in request.form.items():
                current_app.logger.debug(f"{key}: {value}")
            
            # Validate that we have at least one option for select/radio/checkbox fields
            if not options and field_type in ['select', 'radio', 'checkbox']:
                flash('Please add at least one option for this field type.', 'error')
                return render_template('admin/modules/field_form.html', form=form, module=field.parent_module, title='Edit Field', field_id=field_id)
        else:
            form = FormFieldForm(data=field_data, module_id=id)
        
        if form.validate_on_submit():
            current_app.logger.debug("Form validated successfully")
            current_app.logger.debug(f"Before update - Field data: {field.__dict__}")
            
            # Update field data
            field.field_name = form.field_name.data
            field.field_label = form.field_label.data
            field.field_placeholder = form.field_placeholder.data
            field.field_type = form.field_type.data
            field.validation_text = form.validation_text.data
            field.is_required = form.is_required.data
            field.client_type_restrictions = list(map(int, form.client_type_restrictions.data)) if form.client_type_restrictions.data else []
            field.section_id = form.section_id.data if form.section_id.data != 0 else None
            
            current_app.logger.debug(f"Updated client type restrictions: {field.client_type_restrictions}")
            
            # Handle options for select, radio, checkbox fields
            if field.field_type in ['select', 'radio', 'checkbox'] and hasattr(form, 'options'):
                current_app.logger.debug(f"Processing options for field type: {field.field_type}")
                current_app.logger.debug(f"Form options data: {form.options.data}")
                
                options = []
                for option in form.options.data:
                    current_app.logger.debug(f"Processing option: {option}")
                    if isinstance(option, dict) and option.get('label', '').strip() and option.get('value', '').strip():
                        options.append({
                            'label': option['label'].strip(),
                            'value': option['value'].strip()
                        })
                        current_app.logger.debug(f"Added option: {options[-1]}")
                
                if options:
                    current_app.logger.debug(f"Setting field options to: {options}")
                    field.options = options
                    current_app.logger.debug(f"Field options after setting: {field.options}")
                else:
                    current_app.logger.debug("No valid options found")
                    flash('Please add at least one option for this field type.', 'error')
                    return render_template('admin/modules/field_form.html', form=form, module=field.parent_module, title='Edit Field', field_id=field_id)
            else:
                field.options = None
            
            current_app.logger.debug(f"After update - Field data: {field.__dict__}")
            
            try:
                current_app.logger.debug("Attempting to update field in database")
                current_app.logger.debug(f"Field data: {field.__dict__}")
                
                # Force SQLAlchemy to recognize the options change
                field.updated_at = datetime.utcnow()
                
                db.session.add(field)  # Explicitly add the field to the session
                db.session.flush()  # Flush changes to get any DB-generated values
                current_app.logger.debug(f"After flush - Field options: {field.options}")
                db.session.commit()
                current_app.logger.debug("Database commit successful")
                current_app.logger.debug(f"Final field options: {field.options}")
                
                # Verify the save by reloading the field
                db.session.refresh(field)
                current_app.logger.debug(f"After refresh - Field options: {field.options}")
                
                # Update the module's table schema
                current_app.logger.info(f"Updating table schema for module {field.parent_module.code}")
                if not create_or_update_module_table(field.parent_module.code):
                    raise Exception("Failed to update table schema")
                current_app.logger.info("Table schema updated successfully")
                
                flash('Field updated successfully.', 'success')
                return redirect(url_for('modules.list_fields', id=id))
            except Exception as db_error:
                current_app.logger.error(f"Database error: {str(db_error)}")
                db.session.rollback()
                flash(f'Database error: {str(db_error)}', 'error')
        else:
            current_app.logger.debug(f"Form validation failed. Errors: {form.errors}")
            for field_name, errors in form.errors.items():
                for error in errors:
                    field_label = field_name
                    if hasattr(form, field_name):
                        field = getattr(form, field_name)
                        if hasattr(field, 'label') and hasattr(field.label, 'text'):
                            field_label = field.label.text
                    flash(f'{field_label}: {error}', 'error')
        
        return render_template('admin/modules/field_form.html', form=form, module=field.parent_module, title='Edit Field', field_id=field_id)
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in edit_field: {str(e)}")
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('modules.list_fields', id=id))

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
