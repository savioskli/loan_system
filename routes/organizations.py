from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from models.organization import Organization
from forms.organization_forms import OrganizationForm
from extensions import db
from utils.decorators import admin_required

organizations_bp = Blueprint('organizations', __name__)

@organizations_bp.route('/')
@login_required
@admin_required
def index():
    try:
        organizations = Organization.query.order_by(Organization.name).all()
        return render_template('admin/organizations/index.html', organizations=organizations)
    except Exception as e:
        current_app.logger.error(f"Error in organizations index: {str(e)}")
        flash('Error loading organizations', 'error')
        return redirect(url_for('admin.dashboard'))

@organizations_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = OrganizationForm()
    
    if form.validate_on_submit():
        try:
            organization = Organization(
                name=form.name.data,
                code=form.code.data,
                description=form.description.data,
                is_active=form.is_active.data
            )
            db.session.add(organization)
            db.session.commit()
            flash('Organization created successfully.', 'success')
            return redirect(url_for('organizations.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating organization: {str(e)}', 'error')
    
    return render_template('admin/organizations/form.html', form=form, title='Create Organization')

@organizations_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    organization = Organization.query.get_or_404(id)
    form = OrganizationForm(obj=organization)
    
    if form.validate_on_submit():
        try:
            # Don't update code if it's already in use by another organization
            if organization.code != form.code.data:
                existing_org = Organization.query.filter_by(code=form.code.data).first()
                if existing_org:
                    flash('This organization code is already in use.', 'error')
                    return render_template('admin/organizations/form.html', form=form, title='Edit Organization')
            
            organization.name = form.name.data
            organization.code = form.code.data
            organization.description = form.description.data
            organization.is_active = form.is_active.data
            
            db.session.commit()
            flash('Organization updated successfully.', 'success')
            return redirect(url_for('organizations.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating organization: {str(e)}', 'error')
    
    return render_template('admin/organizations/form.html', form=form, title='Edit Organization')

@organizations_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    try:
        organization = Organization.query.get_or_404(id)
        
        # Check if organization has any associated data
        if organization.modules or organization.staff:
            flash('Cannot delete organization with associated modules or staff.', 'error')
            return redirect(url_for('organizations.index'))
        
        db.session.delete(organization)
        db.session.commit()
        flash('Organization deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting organization: {str(e)}', 'error')
    
    return redirect(url_for('organizations.index'))
