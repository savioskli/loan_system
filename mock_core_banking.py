from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# Mock data for different core banking systems
MOCK_DATA = {
    'navision': {
        'tables': [
            {
                'name': 'Customer',
                'description': 'Contains customer/client information including personal details and contact information'
            },
            {
                'name': 'Loan',
                'description': 'Contains loan account information including amounts, terms, and status'
            },
            {
                'name': 'LoanApplication',
                'description': 'Contains loan application details and approval workflow'
            },
            {
                'name': 'Collateral',
                'description': 'Contains information about loan collaterals and their valuation'
            },
            {
                'name': 'Payment',
                'description': 'Contains loan payment history and schedules'
            }
        ]
    },
    'brnet': {
        'tables': [
            {
                'name': 'CIF',
                'description': 'Customer Information File with detailed client records'
            },
            {
                'name': 'LOAN_MASTER',
                'description': 'Master table for all loan accounts'
            },
            {
                'name': 'LOAN_APPLICATION',
                'description': 'Loan application processing and workflow'
            },
            {
                'name': 'COLLATERAL_REGISTER',
                'description': 'Registry of all loan securities and collaterals'
            },
            {
                'name': 'REPAYMENT_SCHEDULE',
                'description': 'Loan repayment schedules and history'
            }
        ]
    }
}

@app.route('/api/beta/companies/metadata', methods=['GET'])
def navision_tables():
    # Check basic auth
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != 'admin123':
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check database name
    database = request.headers.get('Database')
    if not database or database != 'navision_db':
        return jsonify({'error': 'Invalid or missing database name'}), 400
    
    # Simulate some processing time
    time.sleep(0.5)
    return jsonify({'value': MOCK_DATA['navision']['tables']})

@app.route('/api/v1/health', methods=['GET'])
def navision_health():
    # Check basic auth
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != 'admin123':
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({'status': 'healthy', 'message': 'Navision core banking system is running'})

@app.route('/api/schema/tables', methods=['GET'])
def brnet_tables():
    # Check for API key
    api_key = request.headers.get('Authorization')
    if not api_key or not api_key.startswith('Bearer '):
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    # Simulate some processing time
    time.sleep(0.5)
    return jsonify(MOCK_DATA['brnet']['tables'])

@app.route('/api/health', methods=['GET'])
def brnet_health():
    # Check for API key
    api_key = request.headers.get('Authorization')
    if not api_key or not api_key.startswith('Bearer '):
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    return jsonify({'status': 'healthy', 'message': 'BR.NET core banking system is running'})

if __name__ == '__main__':
    app.run(port=5003)
