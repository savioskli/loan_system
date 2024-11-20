from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from services.role_service import RoleService
from forms.user_management import RoleForm
from flask import abort

bp = Blueprint('roles', __name__, url_prefix='/roles')

@bp.route('/', methods=['GET'])
@login_required
def list_roles():
    """List all roles"""
    roles, error = RoleService.list_roles()
    if error:
        current_app.logger.error(f'Error loading roles: {error}')
        flash(error, 'error')
    return render_template('admin/user_roles/list.html', roles=roles or [])

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_role():
    """Create a new role"""
    form = RoleForm()
    
    if request.method == 'POST':
        print("Form Data:", request.form)  # Debug print
        print("Form Validation:", form.validate())  # Debug print
        if form.errors:
            print("Form Errors:", form.errors)  # Debug print
    
    if form.validate_on_submit():
        try:
            # Get the current user's ID
            created_by = current_user.id if not current_user.is_anonymous else None
            
            # Convert form data to appropriate types
            name = form.name.data.strip()
            description = form.description.data.strip() if form.description.data else None
            is_active = bool(form.is_active.data)
            
            print(f"Creating role with: name={name}, description={description}, is_active={is_active}, created_by={created_by}")  # Debug print
            
            # Create role
            role, error = RoleService.create_role(
                name=name,
                description=description,
                is_active=is_active,
                created_by=created_by
            )
            
            if error:
                print(f"Error creating role: {error}")  # Debug print
                flash(error, 'error')
                return render_template('admin/user_roles/form.html', form=form, title='Create Role')
            
            print(f"Role created successfully: {role.name}")  # Debug print
            flash('Role created successfully.', 'success')
            return redirect(url_for('roles.list_roles'))
            
        except Exception as e:
            import traceback
            print("Exception:", str(e))  # Debug print
            print("Traceback:", traceback.format_exc())  # Debug print
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('admin/user_roles/form.html', form=form, title='Create Role')
    
    return render_template('admin/user_roles/form.html', form=form, title='Create Role')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    """Edit an existing role"""
    role, error = RoleService.get_role(id)
    if error:
        flash('Role not found.', 'error')
        return redirect(url_for('roles.list_roles'))

    form = RoleForm(obj=role)
    
    if request.method == 'POST':
        print(f"Form data received: name='{form.name.data}', description='{form.description.data}', is_active={form.is_active.data}")  # Debug print
    
    if form.validate_on_submit():
        print(f"Form validated, updating role {id}")  # Debug print
        updated_role, error = RoleService.update_role(
            role_id=id,
            name=form.name.data,
            description=form.description.data,
            is_active=form.is_active.data,
            updated_by=current_user.id
        )
        if error:
            print(f"Error updating role: {error}")  # Debug print
            flash(error, 'error')
        else:
            flash('Role updated successfully.', 'success')
            return redirect(url_for('roles.list_roles'))
    elif request.method == 'POST':
        print(f"Form validation failed: {form.errors}")  # Debug print
    
    return render_template('admin/user_roles/form.html', form=form, role=role, title='Edit Role')

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_role(id):
    """Delete a role"""
    error = RoleService.delete_role(id)
    if error:
        flash(error, 'error')
    else:
        flash('Role deleted successfully.', 'success')
    return redirect(url_for('roles.list_roles'))
