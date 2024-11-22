from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.module import Module, FormField
from extensions import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get statistics for the dashboard
    pending_clients = 0  # TODO: Implement client count logic
    pending_loans = 0    # TODO: Implement loan count logic
    approved_loans = 0   # TODO: Implement approved loans count
    rejected_loans = 0   # TODO: Implement rejected loans count
    portfolio_value = 0  # TODO: Implement portfolio value calculation
    
    return render_template('user/dashboard.html',
                         pending_clients=pending_clients,
                         pending_loans=pending_loans,
                         approved_loans=approved_loans,
                         rejected_loans=rejected_loans,
                         portfolio_value=portfolio_value)

@user_bp.route('/dynamic_form/<module_code>')
@login_required
def dynamic_form(module_code):
    # TODO: Implement dynamic form rendering based on module code
    return render_template('user/dynamic_form.html', module_code=module_code)

@user_bp.route('/reports')
@login_required
def reports():
    # TODO: Implement reports page
    return render_template('user/reports.html')
