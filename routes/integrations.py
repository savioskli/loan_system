from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from utils.decorators import admin_required
import requests
from datetime import datetime
import json

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

@integrations_bp.route('/core-banking')
@login_required
@admin_required
def core_banking():
    return render_template('admin/integrations/core_banking.html')

# Core Banking API Integration
class CoreBankingAPI:
    def __init__(self, system_type, config):
        self.system_type = system_type
        self.config = config
        self.base_url = f"http://{config['server_url']}:{config['port']}"
        self.session = requests.Session()
        if system_type == 'navision':
            self._setup_navision()
        elif system_type == 'brnet':
            self._setup_brnet()

    def _setup_navision(self):
        """Setup authentication and headers for Navision"""
        self.session.auth = (self.config['username'], self.config['password'])
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _setup_brnet(self):
        """Setup authentication and headers for BR.NET"""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-Key': self.config['api_key']
        })

    def get_loan_details(self, loan_id):
        """Fetch loan details from core banking system"""
        try:
            if self.system_type == 'navision':
                endpoint = f"/api/v1/loans/{loan_id}"
            else:  # BR.NET
                endpoint = f"/api/loans/details/{loan_id}"

            response = self.session.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def get_payment_history(self, loan_id):
        """Fetch payment history for a loan"""
        try:
            if self.system_type == 'navision':
                endpoint = f"/api/v1/loans/{loan_id}/payments"
            else:  # BR.NET
                endpoint = f"/api/loans/{loan_id}/payments"

            response = self.session.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def get_customer_info(self, customer_id):
        """Fetch customer information"""
        try:
            if self.system_type == 'navision':
                endpoint = f"/api/v1/customers/{customer_id}"
            else:  # BR.NET
                endpoint = f"/api/customers/{customer_id}"

            response = self.session.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

# API Routes for Core Banking Integration
@integrations_bp.route('/api/core-banking/test-connection', methods=['POST'])
@login_required
@admin_required
def test_core_banking_connection():
    """Test connection to core banking system"""
    config = request.json
    api = CoreBankingAPI(config['system_type'], config)
    
    try:
        # Try to make a simple API call
        if config['system_type'] == 'navision':
            response = api.session.get(f"{api.base_url}/api/v1/health")
        else:  # BR.NET
            response = api.session.get(f"{api.base_url}/api/health")
        
        response.raise_for_status()
        return jsonify({'success': True, 'message': 'Connection successful'})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'Connection failed: {str(e)}'})

@integrations_bp.route('/api/core-banking/test-sync', methods=['POST'])
@login_required
@admin_required
def test_core_banking_sync():
    """Test data synchronization with core banking system"""
    config = request.json
    api = CoreBankingAPI(config['system_type'], config)
    
    try:
        # Test loan details fetch
        loan_result = api.get_loan_details('test_loan_id')
        if 'error' in loan_result:
            raise Exception(loan_result['error'])

        # Test payment history fetch
        payment_result = api.get_payment_history('test_loan_id')
        if 'error' in payment_result:
            raise Exception(payment_result['error'])

        # Test customer info fetch
        customer_result = api.get_customer_info('test_customer_id')
        if 'error' in customer_result:
            raise Exception(customer_result['error'])

        return jsonify({
            'success': True,
            'message': 'Data synchronization test successful',
            'details': {
                'loan_sync': 'Success',
                'payment_sync': 'Success',
                'customer_sync': 'Success'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Data synchronization test failed: {str(e)}'
        })
