from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.staff import Staff
from models.activity_log import ActivityLog
from forms.auth_forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm
from extensions import db
from utils.logging_utils import log_activity
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role.lower() == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        staff = Staff.query.filter_by(email=form.email.data.lower()).first()
        if staff and staff.check_password(form.password.data):
            if not staff.is_active:
                flash('Your account is not active. Please contact an administrator.', 'warning')
                return render_template('auth/login.html', form=form)

            login_user(staff, remember=form.remember_me.data)
            staff.update_last_login()
            log_activity(staff.id, 'login', 'User logged in successfully')
            
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                if staff.role.lower() == 'admin':
                    next_page = url_for('main.admin_dashboard')
                else:
                    next_page = url_for('main.dashboard')
            return redirect(next_page)
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        staff = Staff(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=form.password.data,
            phone=form.phone.data,
            branch_id=form.branch_id.data
        )
        
        db.session.add(staff)
        try:
            db.session.commit()
            log_activity(staff.id, 'register', 'New user registration')
            flash('Registration successful! Please wait for admin approval.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'logout', 'User logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_activity(current_user.id, 'password_change', 'Password changed successfully')
            flash('Your password has been updated.', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Current password is incorrect.', 'error')
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        staff = Staff.query.filter_by(email=form.email.data.lower()).first()
        if staff:
            # Here we would send an email with reset instructions
            # For now, we'll just show a success message
            flash('Check your email for password reset instructions.', 'success')
            return redirect(url_for('auth.login'))
        flash('Email address not found.', 'error')
    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Here we would verify the reset token
    # For now, we'll just show the reset form
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Here we would update the user's password
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
