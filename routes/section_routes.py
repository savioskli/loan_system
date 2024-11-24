from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.form_section import FormSection
from models.module import Module
from models.client_type import ClientType
from models.product import Product
from forms.section_forms import FormSectionForm
from extensions import db
from utils.decorators import admin_required
import json

sections_bp = Blueprint('sections', __name__, url_prefix='/sections')

@sections_bp.route('/')
@login_required
@admin_required
def index():
    # Get parent modules with their children
    parent_modules = Module.query.filter_by(parent_id=None).order_by(Module.name).all()
    return render_template('admin/sections/index.html', parent_modules=parent_modules)

@sections_bp.route('/create/<int:module_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def create(module_id):
    module = Module.query.get_or_404(module_id)
    form = FormSectionForm()
    
    # Populate choices for client types and products
    form.client_type_restrictions.choices = [(ct.id, ct.client_name) for ct in ClientType.query.all()]
    form.product_restrictions.choices = [(p.id, p.name) for p in Product.query.all()]
    
    if form.validate_on_submit():
        try:
            # Convert lists to JSON for storage
            client_type_restrictions = json.dumps(form.client_type_restrictions.data) if form.client_type_restrictions.data else None
            product_restrictions = json.dumps(form.product_restrictions.data) if form.product_restrictions.data else None
            
            section = FormSection(
                module_id=module.id,
                name=form.name.data,
                description=form.description.data,
                order=form.order.data,
                is_active=form.is_active.data,
                client_type_restrictions=client_type_restrictions,
                product_restrictions=product_restrictions
            )
            db.session.add(section)
            db.session.commit()
            flash('Form section created successfully.', 'success')
            return redirect(url_for('sections.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating form section. Please try again.', 'error')
    
    return render_template('admin/sections/form.html', 
                         form=form, 
                         module=module,
                         title='Create Form Section')

@sections_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    section = FormSection.query.get_or_404(id)
    form = FormSectionForm(obj=section)
    
    # Populate choices for client types and products
    form.client_type_restrictions.choices = [(ct.id, ct.client_name) for ct in ClientType.query.all()]
    form.product_restrictions.choices = [(p.id, p.name) for p in Product.query.all()]
    
    if request.method == 'GET':
        # Set initial values for multi-select fields
        if section.client_type_restrictions:
            form.client_type_restrictions.data = json.loads(section.client_type_restrictions)
        if section.product_restrictions:
            form.product_restrictions.data = json.loads(section.product_restrictions)
    
    if form.validate_on_submit():
        try:
            section.name = form.name.data
            section.description = form.description.data
            section.order = form.order.data
            section.is_active = form.is_active.data
            
            # Convert lists to JSON for storage
            section.client_type_restrictions = json.dumps(form.client_type_restrictions.data) if form.client_type_restrictions.data else None
            section.product_restrictions = json.dumps(form.product_restrictions.data) if form.product_restrictions.data else None
            
            db.session.commit()
            flash('Form section updated successfully.', 'success')
            return redirect(url_for('sections.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating form section. Please try again.', 'error')
    
    return render_template('admin/sections/form.html', 
                         form=form, 
                         section=section,
                         module=section.module,
                         title='Edit Form Section')

@sections_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    section = FormSection.query.get_or_404(id)
    try:
        db.session.delete(section)
        db.session.commit()
        flash('Form section deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting form section. Please try again.', 'error')
    
    return redirect(url_for('sections.index'))

@sections_bp.route('/update-order', methods=['POST'])
@login_required
@admin_required
def update_order():
    try:
        sections_order = request.json.get('sections', [])
        for order_data in sections_order:
            section = FormSection.query.get(order_data['id'])
            if section:
                section.order = order_data['order']
        db.session.commit()
        return {'success': True, 'message': 'Section order updated successfully.'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500
