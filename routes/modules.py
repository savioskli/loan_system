from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models.module import Module, FormField
from forms.module_forms import ModuleForm, FormFieldForm, DynamicFormFieldForm
from extensions import db
from models.role import Role
import json

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
            module = Module(
                name=form.name.data,
                code=form.code.data,
                description=form.description.data,
                parent_id=form.parent_id.data if form.parent_id.data != 0 else None,
                is_active=form.is_active.data
            )
            print(f"Module created: {module}")
            db.session.add(module)
            db.session.commit()
            print("Module saved to database")
            flash('Module created successfully.', 'success')
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
            module.name = form.name.data
            module.code = form.code.data
            module.description = form.description.data
            module.parent_id = form.parent_id.data if form.parent_id.data != 0 else None
            module.is_active = form.is_active.data
            
            db.session.commit()
            flash('Module updated successfully.', 'success')
            return redirect(url_for('modules.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating module: {str(e)}', 'error')
            
    return render_template('admin/modules/form.html', form=form, title='Edit Module')

@modules_bp.route('/<int:id>/fields')
@login_required
def list_fields(id):
    if not current_user.role or current_user.role.name.lower() != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
        
    module = Module.query.get_or_404(id)
    fields = module.form_fields.order_by(FormField.field_order).all()
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
            form = FormFieldForm()
            return render_template('admin/modules/field_form.html', form=form, module=module)
        
        # For POST requests
        current_app.logger.debug(f"Form Data: {request.form}")
        
        # Get the field data
        field_data = {
            'field_name': request.form.get('field_name'),
            'field_label': request.form.get('field_label'),
            'field_placeholder': request.form.get('field_placeholder'),
            'field_type': field_type,
            'validation_text': request.form.get('validation_text'),
            'is_required': request.form.get('is_required') == 'y'
        }
        
        # Create the appropriate form based on field type
        if field_type in ['select', 'radio', 'checkbox']:
            form = DynamicFormFieldForm(data=field_data)
            
            # Get options from the form
            option_labels = request.form.getlist('options-label[]')
            option_values = request.form.getlist('options-value[]')
            
            # Clear any existing options and add new ones
            while len(form.options) > 0:
                form.options.pop_entry()
            
            for label, value in zip(option_labels, option_values):
                if label.strip() and value.strip():
                    form.options.append_entry({
                        'label': label.strip(),
                        'value': value.strip()
                    })
        else:
            form = FormFieldForm(data=field_data)
        
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
                field_order=max_order + 1
            )
            
            # Handle options for select, radio, checkbox fields
            if field.field_type in ['select', 'radio', 'checkbox'] and hasattr(form, 'options'):
                options = []
                for option in form.options.data:
                    if option['label'].strip() and option['value'].strip():
                        options.append({
                            'label': option['label'].strip(),
                            'value': option['value'].strip()
                        })
                
                if options:
                    field.options = options
                    current_app.logger.debug(f"Setting options: {options}")
                else:
                    current_app.logger.debug("No valid options found")
                    flash('Please add at least one option for this field type.', 'error')
                    return render_template('admin/modules/field_form.html', form=form, module=module)
            
            try:
                current_app.logger.debug("Attempting to add field to database")
                db.session.add(field)
                db.session.commit()
                flash('Field created successfully.', 'success')
                return redirect(url_for('modules.list_fields', id=module.id))
            except Exception as db_error:
                current_app.logger.error(f"Database error: {str(db_error)}")
                db.session.rollback()
                flash(f'Database error: {str(db_error)}', 'error')
        else:
            current_app.logger.debug(f"Form validation failed. Errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text if hasattr(form, field) and hasattr(getattr(form, field), "label") else field}: {error}', 'error')
        
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
            form_data = {
                'field_name': field.field_name,
                'field_label': field.field_label,
                'field_placeholder': field.field_placeholder,
                'field_type': field.field_type,
                'validation_text': field.validation_text,
                'is_required': field.is_required
            }
            
            if field.field_type in ['select', 'radio', 'checkbox']:
                form = DynamicFormFieldForm(data=form_data)
                # Add existing options
                if field.options:
                    current_app.logger.debug(f"Loading existing options: {field.options}")
                    for option in field.options:
                        form.options.append_entry(option)
            else:
                form = FormFieldForm(data=form_data)
                
            return render_template('admin/modules/field_form.html', form=form, module=field.parent_module, title='Edit Field', field_id=field_id)
        
        # For POST requests
        current_app.logger.debug(f"POST request - Form Data: {request.form}")
        field_type = request.form.get('field_type', '')
        
        # Get the field data
        field_data = {
            'field_name': request.form.get('field_name'),
            'field_label': request.form.get('field_label'),
            'field_placeholder': request.form.get('field_placeholder'),
            'field_type': field_type,
            'validation_text': request.form.get('validation_text'),
            'is_required': request.form.get('is_required') == 'y'
        }
        current_app.logger.debug(f"Field data to be updated: {field_data}")
        
        # Create the appropriate form based on field type
        if field_type in ['select', 'radio', 'checkbox']:
            form = DynamicFormFieldForm(data=field_data)
            
            # Get options from the form
            option_labels = request.form.getlist('options-label[]')
            option_values = request.form.getlist('options-value[]')
            current_app.logger.debug(f"Option data received - Labels: {option_labels}, Values: {option_values}")
            
            # Clear any existing options and add new ones
            while len(form.options) > 0:
                form.options.pop_entry()
            
            for label, value in zip(option_labels, option_values):
                if label.strip() and value.strip():
                    form.options.append_entry({
                        'label': label.strip(),
                        'value': value.strip()
                    })
        else:
            form = FormFieldForm(data=field_data)
        
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
            
            # Handle options for select, radio, checkbox fields
            if field.field_type in ['select', 'radio', 'checkbox'] and hasattr(form, 'options'):
                options = []
                for option in form.options.data:
                    if option['label'].strip() and option['value'].strip():
                        options.append({
                            'label': option['label'].strip(),
                            'value': option['value'].strip()
                        })
                
                if options:
                    field.options = options
                    current_app.logger.debug(f"Setting options: {options}")
                else:
                    current_app.logger.debug("No valid options found")
                    flash('Please add at least one option for this field type.', 'error')
                    return render_template('admin/modules/field_form.html', form=form, module=field.parent_module, title='Edit Field', field_id=field_id)
            else:
                field.options = None
            
            current_app.logger.debug(f"After update - Field data: {field.__dict__}")
            
            try:
                current_app.logger.debug("Attempting to update field in database")
                db.session.add(field)  # Explicitly add the field to the session
                db.session.flush()     # Flush changes to get any SQL errors before commit
                current_app.logger.debug(f"After flush - Field data: {field.__dict__}")
                db.session.commit()
                current_app.logger.debug("Database commit successful")
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
                    flash(f'{getattr(form, field_name).label.text if hasattr(form, field_name) and hasattr(getattr(form, field_name), "label") else field_name}: {error}', 'error')
        
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
        
        # Delete the field
        db.session.delete(field)
        db.session.commit()
        
        current_app.logger.info(f"Field {field_id} deleted successfully")
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
    print(f"Delete request received for module ID: {id}")  # Debug log
    
    if not current_user.has_role('admin'):
        print(f"Permission denied for user: {current_user}")  # Debug log
        return jsonify({
            'success': False,
            'message': 'You do not have permission to delete modules.'
        }), 403

    try:
        module = Module.query.get_or_404(id)
        print(f"Found module to delete: {module.name} (ID: {module.id})")  # Debug log
        
        # Delete all form fields first
        form_fields = FormField.query.filter_by(module_id=id).all()
        print(f"Found {len(form_fields)} form fields to delete")  # Debug log
        for field in form_fields:
            print(f"Deleting form field: {field.field_name}")  # Debug log
            db.session.delete(field)
        
        # Delete all child modules recursively
        children = Module.query.filter_by(parent_id=id).all()
        print(f"Found {len(children)} child modules to delete")  # Debug log
        for child in children:
            child_fields = FormField.query.filter_by(module_id=child.id).all()
            print(f"Deleting {len(child_fields)} form fields for child module: {child.name}")  # Debug log
            for field in child_fields:
                db.session.delete(field)
            print(f"Deleting child module: {child.name}")  # Debug log
            db.session.delete(child)
        
        # Finally delete the module itself
        print(f"Deleting main module: {module.name}")  # Debug log
        db.session.delete(module)
        db.session.commit()
        print("Successfully committed all deletions")  # Debug log
        
        return jsonify({
            'success': True,
            'message': f'Module {module.name} has been deleted successfully.'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting module: {str(e)}")  # Debug log
        print(f"Error type: {type(e)}")  # Debug log
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        return jsonify({
            'success': False,
            'message': f'An error occurred while deleting the module: {str(e)}'
        }), 500
