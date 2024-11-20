from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.staff import Staff
from models.branch import Branch
from models.role import Role
from forms.user_management import UserCreateForm, UserApprovalForm
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash
import logging
from services.staff_service import StaffService

bp = Blueprint('user_management', __name__, url_prefix='/user-management')

# User Management
@bp.route('/users', methods=['GET'])
@login_required
def list_users():
    """List all users."""
    try:
        status = request.args.get('status')
        users = StaffService.get_all_staff()
        if status:
            users = [user for user in users if user.status == status]
        return render_template('admin/users/list.html', users=users, current_status=status)
    except Exception as e:
        current_app.logger.error(f"Error in list_users: {str(e)}")
        flash('An error occurred while loading users.', 'error')
        return render_template('admin/users/list.html', users=[], current_status=None)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create a new user."""
    form = UserCreateForm()
    
    try:
        # Get all roles and branches for the form
        roles = Role.query.all()
        if not roles:
            flash('No roles found in the system. Please create at least one role first.', 'error')
            return redirect(url_for('user_management.list_users'))
            
        branches = Branch.query.all()
        
        # Populate form choices
        form.role_id.choices = [(role.id, role.name) for role in roles]
        form.branch_id.choices = [(0, 'No Branch')] + [(branch.id, branch.branch_name) for branch in branches]
        
        if form.validate_on_submit():
            try:
                # Prepare staff data
                staff_data = {
                    'email': form.email.data.strip(),
                    'first_name': form.first_name.data.strip(),
                    'last_name': form.last_name.data.strip(),
                    'phone': form.phone.data.strip() if form.phone.data else None,
                    'password': form.password.data,
                    'role_id': form.role_id.data,
                    'branch_id': form.branch_id.data if form.branch_id.data != 0 else None,
                    'is_active': form.is_active.data
                }
                
                current_app.logger.info(f"Creating staff member with data: {staff_data}")
                
                # Create new staff member
                new_staff = StaffService.create_staff(staff_data)
                
                flash('User created successfully!', 'success')
                return redirect(url_for('user_management.list_users'))
                
            except ValueError as e:
                current_app.logger.error(f"Validation error in create_user: {str(e)}")
                flash(str(e), 'error')
                return render_template('admin/users/create.html', form=form)
            except Exception as e:
                current_app.logger.error(f"Unexpected error in create_user: {str(e)}")
                flash('An unexpected error occurred while creating the user.', 'error')
                return render_template('admin/users/create.html', form=form)
        
        # If form validation failed, check for errors
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
        
        return render_template('admin/users/create.html', form=form)
        
    except Exception as e:
        current_app.logger.error(f"Error setting up create_user form: {str(e)}")
        flash('An error occurred while setting up the form.', 'error')
        return render_template('admin/users/create.html', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    staff = StaffService.get_staff_by_id(id)
    if not staff:
        flash('User not found.', 'error')
        return redirect(url_for('user_management.list_users'))
    
    form = UserCreateForm(obj=staff)
    
    if request.method == 'GET':
        # Get active branches for the dropdown
        branches = Branch.query.filter_by(is_active=True).all()
        form.branch_id.choices = [(0, '-- Select Branch --')] + [(b.id, b.branch_name) for b in branches]
        form.branch_id.data = staff.branch_id if staff.branch_id else 0
        
        # Get active roles for the dropdown
        roles = Role.query.filter_by(is_active=True).all()
        form.role_id.choices = [(r.id, r.name) for r in roles]
        form.role_id.data = staff.role_id
        
        # Set is_active based on user status
        form.is_active.data = staff.status == 'active'
        
        # Don't show password
        form.password.data = ''
    
    if form.validate_on_submit():
        try:
            data = {
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'phone': form.phone.data,
                'branch_id': form.branch_id.data if form.branch_id.data != 0 else None,
                'role_id': form.role_id.data,
                'is_active': form.is_active.data
            }
            
            if form.password.data:
                data['password'] = form.password.data
            
            success, message = StaffService.update_staff(id, data)
            if success:
                flash('User updated successfully!', 'success')
                return redirect(url_for('user_management.list_users'))
            else:
                flash(message, 'error')
                
        except Exception as e:
            flash(str(e), 'error')
            logging.error(f"Error updating user: {str(e)}")
    
    return render_template('admin/users/form.html', form=form, title='Edit User', staff=staff)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    success, message = StaffService.delete_staff(id)
    if success:
        flash('User deleted successfully!', 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('user_management.list_users'))

@bp.route('/change-status/<int:id>', methods=['POST'])
@login_required
def change_status(id):
    status = request.form.get('status')
    if not status:
        flash('Status is required.', 'error')
        return redirect(url_for('user_management.list_users'))
    
    success, message = StaffService.change_staff_status(id, status)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('user_management.list_users'))

@bp.route('/<int:id>/approve', methods=['GET', 'POST'])
@login_required
def approve_user(id):
    staff = StaffService.get_staff_by_id(id)
    form = UserApprovalForm(obj=staff)
    
    if form.validate_on_submit():
        staff.status = form.status.data
        if form.status.data == 'approved':
            staff.approve(current_user)
        elif form.status.data == 'rejected':
            staff.reject(current_user)
        db.session.commit()
        flash('User status updated successfully.', 'success')
        return redirect(url_for('user_management.list_users'))
    
    return render_template('admin/users/approve.html', form=form, staff=staff)
