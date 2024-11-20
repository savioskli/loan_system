from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.module import Module, FormField
from forms.module_forms import ModuleForm, FormFieldForm, DynamicFormFieldForm
from extensions import db
import json

modules_bp = Blueprint('modules', __name__)

@modules_bp.route('/')
@login_required
def index():
    if current_user.role != 'Admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    # Get only top-level modules (those without parents)
    modules = Module.query.filter_by(parent_id=None).all()
    return render_template('admin/modules/index.html', modules=modules)

@modules_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != 'Admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
        
    form = ModuleForm()
    
    if form.validate_on_submit():
        try:
            module = Module(
                name=form.name.data,
                code=form.code.data,
                description=form.description.data,
                parent_id=form.parent_id.data if form.parent_id.data != 0 else None,
                is_active=form.is_active.data
            )
            db.session.add(module)
            db.session.commit()
            flash('Module created successfully.', 'success')
            return redirect(url_for('modules.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating module: {str(e)}', 'error')
    
    return render_template('admin/modules/form.html', form=form, title='Create Module')

@modules_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    if current_user.role != 'Admin':
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
    if current_user.role != 'Admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
        
    module = Module.query.get_or_404(id)
    fields = module.form_fields.order_by(FormField.field_order).all()
    return render_template('admin/modules/fields.html', module=module, fields=fields)

@modules_bp.route('/<int:id>/fields/create', methods=['GET', 'POST'])
@login_required
def create_field(id):
    if current_user.role != 'Admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
        
    module = Module.query.get_or_404(id)
    form = FormFieldForm()
    
    if form.validate_on_submit():
        try:
            # Get the highest current order
            max_order = db.session.query(db.func.max(FormField.field_order)).filter_by(module_id=id).scalar() or 0
            
            field = FormField(
                module_id=id,
                field_name=form.field_name.data,
                field_label=form.field_label.data,
                field_placeholder=form.field_placeholder.data,
                field_type=form.field_type.data,
                validation_text=form.validation_text.data,
                is_required=form.is_required.data,
                field_order=max_order + 1
            )
            
            if isinstance(form, DynamicFormFieldForm):
                options = []
                for option in form.options.data:
                    if option['label'].strip() and option['value'].strip():
                        options.append({
                            'label': option['label'].strip(),
                            'value': option['value'].strip()
                        })
                field.options = options
                
                if form.validation_rules.data:
                    try:
                        field.validation_rules = json.loads(form.validation_rules.data)
                    except json.JSONDecodeError:
                        flash('Invalid validation rules JSON format', 'error')
                        return render_template('admin/modules/field_form.html', form=form, module=module)
            
            db.session.add(field)
            db.session.commit()
            flash('Form field created successfully.', 'success')
            return redirect(url_for('modules.list_fields', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating form field: {str(e)}', 'error')
    
    return render_template('admin/modules/field_form.html', form=form, module=module)

@modules_bp.route('/<int:id>/fields/<int:field_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_field(id, field_id):
    if current_user.role != 'Admin':
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
        
    field = FormField.query.get_or_404(field_id)
    if field.module_id != id:
        flash('Invalid field ID.', 'error')
        return redirect(url_for('modules.list_fields', id=id))
        
    form = FormFieldForm(obj=field)
    
    if form.validate_on_submit():
        field.field_name = form.field_name.data
        field.field_label = form.field_label.data
        field.field_placeholder = form.field_placeholder.data
        field.field_type = form.field_type.data
        field.validation_text = form.validation_text.data
        field.is_required = form.is_required.data
        
        if isinstance(form, DynamicFormFieldForm):
            options = []
            for option in form.options.data:
                if option['label'].strip() and option['value'].strip():
                    options.append({
                        'label': option['label'].strip(),
                        'value': option['value'].strip()
                    })
            field.options = options
            field.validation_rules = json.loads(form.validation_rules.data) if form.validation_rules.data else None
        
        try:
            db.session.commit()
            flash('Form field updated successfully.', 'success')
            return redirect(url_for('modules.list_fields', id=id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating form field. Please try again.', 'error')
    
    return render_template('admin/modules/field_form.html', form=form, module=field.parent_module, title='Edit Field')

@modules_bp.route('/<int:id>/fields/order', methods=['POST'])
@login_required
def update_field_order(id):
    if current_user.role != 'Admin':
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
