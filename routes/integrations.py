from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from utils.decorators import admin_required

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/credit-bureau')
@login_required
@admin_required
def credit_bureau():
    return render_template('admin/integrations/credit_bureau.html')

@integrations_bp.route('/payment-gateway')
@login_required
@admin_required
def payment_gateway():
    return render_template('admin/integrations/payment_gateway.html')

@integrations_bp.route('/sms-gateway')
@login_required
@admin_required
def sms_gateway():
    return render_template('admin/integrations/sms_gateway.html')
