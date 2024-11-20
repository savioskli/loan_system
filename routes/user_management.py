from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.user import User
from models.branch import Branch
from models.staff import Staff
from forms.user_management import UserApprovalForm, UserCreateForm
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash
import logging

bp = Blueprint('user_management', __name__)

# User Management
@bp.route('/', methods=['GET'])
@login_required
def list_users():
    status = request.args.get('status')
    query = User.query
    
    if status:
        query = query.filter(User.status == status)
    
    users = query.all()
    return render_template('admin/users/list.html', users=users, current_status=status)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    form = UserCreateForm()
    try:
        # Get active branches for the dropdown
        branches = Branch.query.filter_by(is_active=True).all()
        form.branch_id.choices = [(0, '-- Select Branch --')] + [(b.id, b.branch_name) for b in branches]
        
        if form.validate_on_submit():
            try:
                # Check if email already exists
                if Staff.query.filter_by(email=form.email.data.lower()).first():
                    flash('Email already exists.', 'error')
                    return render_template('admin/users/form.html', form=form, title='Create User')
                
                # Validate branch if selected
                branch_id = None
                if form.branch_id.data != 0:
                    branch = Branch.query.get(form.branch_id.data)
                    if not branch:
                        flash('Selected branch not found.', 'error')
                        return render_template('admin/users/form.html', form=form, title='Create User')
                    branch_id = branch.id
                
                # Create the user
                user = Staff(
                    email=form.email.data.lower(),
                    first_name=form.first_name.data.strip(),
                    last_name=form.last_name.data.strip(),
                    phone=form.phone.data.strip() if form.phone.data else None,
                    branch_id=branch_id,
                    is_active=form.is_active.data
                )
                user.set_password('temporary_password')
                
                # Log the user creation attempt
                current_app.logger.info(f'Creating new user with email: {user.email}')
                
                db.session.add(user)
                db.session.commit()
                
                flash('User created successfully. Default password is: temporary_password', 'success')
                return redirect(url_for('user_management.list_users'))
                
            except Exception as inner_e:
                db.session.rollback()
                current_app.logger.error(f'Error in user creation (inner): {str(inner_e)}')
                flash(f'Error creating user: {str(inner_e)}', 'error')
                return render_template('admin/users/form.html', form=form, title='Create User')
            
        return render_template('admin/users/form.html', form=form, title='Create User')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error in user creation (outer): {str(e)}')
        flash(f'Error creating user: {str(e)}', 'error')
        return render_template('admin/users/form.html', form=form, title='Create User')

@bp.route('/<int:id>/approve', methods=['GET', 'POST'])
@login_required
def approve_user(id):
    user = User.query.get_or_404(id)
    form = UserApprovalForm(obj=user)
    
    if form.validate_on_submit():
        user.status = form.status.data
        if form.status.data == 'approved':
            user.approve(current_user)
        elif form.status.data == 'rejected':
            user.reject(current_user)
        db.session.commit()
        flash('User status updated successfully.', 'success')
        return redirect(url_for('user_management.list_users'))
    
    return render_template('admin/users/approve.html', form=form, user=user)
