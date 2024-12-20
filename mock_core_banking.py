from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# Mock data for different core banking systems
MOCK_DATA = {
    'navision': {
        'tables': [
            {
                'name': 'Customer',
                'description': 'Contains customer/client information including personal details and contact information',
                'fields': [
                    {'name': 'No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Name', 'type': 'Text[100]', 'description': 'Customer name'},
                    {'name': 'Address', 'type': 'Text[100]', 'description': 'Customer address'},
                    {'name': 'Phone_No_', 'type': 'Text[30]', 'description': 'Phone number'},
                    {'name': 'E_Mail', 'type': 'Text[80]', 'description': 'Email address'}
                ]
            },
            {
                'name': 'Loan',
                'description': 'Contains loan account information including amounts, terms, and status',
                'fields': [
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Loan_Amount', 'type': 'Decimal', 'description': 'Original loan amount'},
                    {'name': 'Outstanding_Balance', 'type': 'Decimal', 'description': 'Current outstanding balance'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Loan status (Active/Closed/Default)'}
                ]
            },
            {
                'name': 'LoanApplication',
                'description': 'Contains loan application details and approval workflow',
                'fields': [
                    {'name': 'Application_No_', 'type': 'Code[20]', 'description': 'Application number'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Application_Date', 'type': 'Date', 'description': 'Application date'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Application status'}
                ]
            },
            {
                'name': 'Collateral',
                'description': 'Contains information about loan collaterals and their valuation',
                'fields': [
                    {'name': 'Collateral_No_', 'type': 'Code[20]', 'description': 'Collateral number'},
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Type', 'type': 'Option', 'description': 'Type of collateral'},
                    {'name': 'Value', 'type': 'Decimal', 'description': 'Collateral value'}
                ]
            },
            {
                'name': 'Payment',
                'description': 'Contains loan payment history and schedules',
                'fields': [
                    {'name': 'Entry_No_', 'type': 'Integer', 'description': 'Payment entry number'},
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Payment_Date', 'type': 'Date', 'description': 'Payment date'},
                    {'name': 'Amount', 'type': 'Decimal', 'description': 'Payment amount'}
                ]
            },
            {
                'name': 'Loan_Grading',
                'description': 'Contains loan classification and provisioning details as per CBK guidelines',
                'fields': [
                    {'name': 'Entry_No_', 'type': 'Integer', 'description': 'Entry number (Primary Key)'},
                    {'name': 'Loan_Account_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Customer_Name', 'type': 'Text[100]', 'description': 'Customer name'},
                    {'name': 'Loan_Amount', 'type': 'Decimal', 'description': 'Original loan amount'},
                    {'name': 'Outstanding_Balance', 'type': 'Decimal', 'description': 'Current outstanding balance'},
                    {'name': 'Days_In_Arrears', 'type': 'Integer', 'description': 'Number of days in arrears'},
                    {'name': 'Principal_In_Arrears', 'type': 'Decimal', 'description': 'Principal amount in arrears'},
                    {'name': 'Interest_In_Arrears', 'type': 'Decimal', 'description': 'Interest amount in arrears'},
                    {'name': 'Total_In_Arrears', 'type': 'Decimal', 'description': 'Total amount in arrears'},
                    {'name': 'Classification', 'type': 'Code[1]', 'description': 'Risk classification (A/B/C/D/E)'},
                    {'name': 'Classification_Date', 'type': 'Date', 'description': 'Date of classification'},
                    {'name': 'Provision_Rate', 'type': 'Decimal', 'description': 'Provision rate percentage'},
                    {'name': 'Provision_Amount', 'type': 'Decimal', 'description': 'Calculated provision amount'}
                ],
                'sample_data': [
                    {
                        'Entry_No_': 1,
                        'Loan_Account_No_': 'LN00000001',
                        'Customer_Name': 'John Kamau',
                        'Loan_Amount': 500000.00,
                        'Outstanding_Balance': 450000.00,
                        'Days_In_Arrears': 10,
                        'Principal_In_Arrears': 10000.00,
                        'Interest_In_Arrears': 6041.67,
                        'Total_In_Arrears': 16041.67,
                        'Classification': 'A',
                        'Classification_Date': '2023-12-10',
                        'Provision_Rate': 1.00,
                        'Provision_Amount': 4500.00
                    },
                    {
                        'Entry_No_': 2,
                        'Loan_Account_No_': 'LN00000002',
                        'Customer_Name': 'Mary Wanjiku',
                        'Loan_Amount': 750000.00,
                        'Outstanding_Balance': 675000.00,
                        'Days_In_Arrears': 15,
                        'Principal_In_Arrears': 15000.00,
                        'Interest_In_Arrears': 10000.00,
                        'Total_In_Arrears': 25000.00,
                        'Classification': 'A',
                        'Classification_Date': '2023-12-05',
                        'Provision_Rate': 1.00,
                        'Provision_Amount': 6750.00
                    },
                    {
                        'Entry_No_': 3,
                        'Loan_Account_No_': 'LN00000003',
                        'Customer_Name': 'Peter Ochieng',
                        'Loan_Amount': 1000000.00,
                        'Outstanding_Balance': 900000.00,
                        'Days_In_Arrears': 40,
                        'Principal_In_Arrears': 40000.00,
                        'Interest_In_Arrears': 25833.33,
                        'Total_In_Arrears': 65833.33,
                        'Classification': 'B',
                        'Classification_Date': '2023-11-10',
                        'Provision_Rate': 3.00,
                        'Provision_Amount': 27000.00
                    },
                    {
                        'Entry_No_': 4,
                        'Loan_Account_No_': 'LN00000004',
                        'Customer_Name': 'Sarah Muthoni',
                        'Loan_Amount': 450000.00,
                        'Outstanding_Balance': 405000.00,
                        'Days_In_Arrears': 45,
                        'Principal_In_Arrears': 18000.00,
                        'Interest_In_Arrears': 10500.00,
                        'Total_In_Arrears': 28500.00,
                        'Classification': 'B',
                        'Classification_Date': '2023-11-05',
                        'Provision_Rate': 3.00,
                        'Provision_Amount': 12150.00
                    },
                    {
                        'Entry_No_': 5,
                        'Loan_Account_No_': 'LN00000005',
                        'Customer_Name': 'James Kiprop',
                        'Loan_Amount': 800000.00,
                        'Outstanding_Balance': 720000.00,
                        'Days_In_Arrears': 70,
                        'Principal_In_Arrears': 48000.00,
                        'Interest_In_Arrears': 33000.00,
                        'Total_In_Arrears': 81000.00,
                        'Classification': 'C',
                        'Classification_Date': '2023-10-10',
                        'Provision_Rate': 20.00,
                        'Provision_Amount': 144000.00
                    },
                    {
                        'Entry_No_': 6,
                        'Loan_Account_No_': 'LN00000006',
                        'Customer_Name': 'Grace Akinyi',
                        'Loan_Amount': 1200000.00,
                        'Outstanding_Balance': 1080000.00,
                        'Days_In_Arrears': 75,
                        'Principal_In_Arrears': 72000.00,
                        'Interest_In_Arrears': 46500.00,
                        'Total_In_Arrears': 118500.00,
                        'Classification': 'C',
                        'Classification_Date': '2023-10-05',
                        'Provision_Rate': 20.00,
                        'Provision_Amount': 216000.00
                    },
                    {
                        'Entry_No_': 7,
                        'Loan_Account_No_': 'LN00000007',
                        'Customer_Name': 'David Njoroge',
                        'Loan_Amount': 2000000.00,
                        'Outstanding_Balance': 1800000.00,
                        'Days_In_Arrears': 100,
                        'Principal_In_Arrears': 160000.00,
                        'Interest_In_Arrears': 113333.33,
                        'Total_In_Arrears': 273333.33,
                        'Classification': 'D',
                        'Classification_Date': '2023-09-10',
                        'Provision_Rate': 50.00,
                        'Provision_Amount': 900000.00
                    },
                    {
                        'Entry_No_': 8,
                        'Loan_Account_No_': 'LN00000008',
                        'Customer_Name': 'Alice Wairimu',
                        'Loan_Amount': 1500000.00,
                        'Outstanding_Balance': 1350000.00,
                        'Days_In_Arrears': 105,
                        'Principal_In_Arrears': 120000.00,
                        'Interest_In_Arrears': 80000.00,
                        'Total_In_Arrears': 200000.00,
                        'Classification': 'D',
                        'Classification_Date': '2023-09-05',
                        'Provision_Rate': 50.00,
                        'Provision_Amount': 675000.00
                    },
                    {
                        'Entry_No_': 9,
                        'Loan_Account_No_': 'LN00000009',
                        'Customer_Name': 'Michael Otieno',
                        'Loan_Amount': 1800000.00,
                        'Outstanding_Balance': 1620000.00,
                        'Days_In_Arrears': 190,
                        'Principal_In_Arrears': 180000.00,
                        'Interest_In_Arrears': 131250.00,
                        'Total_In_Arrears': 311250.00,
                        'Classification': 'E',
                        'Classification_Date': '2023-06-10',
                        'Provision_Rate': 100.00,
                        'Provision_Amount': 1620000.00
                    }
                ]
            }
        ]
    },
    'brnet': {
        'tables': [
            {
                'name': 'CIF',
                'description': 'Customer Information File with detailed client records',
                'fields': [
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Name', 'type': 'Text[100]', 'description': 'Customer name'},
                    {'name': 'Address', 'type': 'Text[100]', 'description': 'Customer address'},
                    {'name': 'Phone_No_', 'type': 'Text[30]', 'description': 'Phone number'},
                    {'name': 'E_Mail', 'type': 'Text[80]', 'description': 'Email address'}
                ]
            },
            {
                'name': 'LOAN_MASTER',
                'description': 'Master table for all loan accounts',
                'fields': [
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Loan_Amount', 'type': 'Decimal', 'description': 'Original loan amount'},
                    {'name': 'Outstanding_Balance', 'type': 'Decimal', 'description': 'Current outstanding balance'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Loan status (Active/Closed/Default)'}
                ]
            },
            {
                'name': 'LOAN_APPLICATION',
                'description': 'Loan application processing and workflow',
                'fields': [
                    {'name': 'Application_No_', 'type': 'Code[20]', 'description': 'Application number'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Application_Date', 'type': 'Date', 'description': 'Application date'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Application status'}
                ]
            },
            {
                'name': 'COLLATERAL_REGISTER',
                'description': 'Registry of all loan securities and collaterals',
                'fields': [
                    {'name': 'Collateral_No_', 'type': 'Code[20]', 'description': 'Collateral number'},
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Type', 'type': 'Option', 'description': 'Type of collateral'},
                    {'name': 'Value', 'type': 'Decimal', 'description': 'Collateral value'}
                ]
            },
            {
                'name': 'REPAYMENT_SCHEDULE',
                'description': 'Loan repayment schedules and history',
                'fields': [
                    {'name': 'Entry_No_', 'type': 'Integer', 'description': 'Payment entry number'},
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Payment_Date', 'type': 'Date', 'description': 'Payment date'},
                    {'name': 'Amount', 'type': 'Decimal', 'description': 'Payment amount'}
                ]
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
    
    # Create simplified table metadata
    tables = [
        {'name': table['name'], 'description': table['description']} 
        for table in MOCK_DATA['navision']['tables']
    ]
    
    # Simulate some processing time
    time.sleep(0.5)
    return jsonify({'value': tables})

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

@app.route('/api/beta/companies/loan-grading', methods=['GET'])
def navision_loan_grading():
    # Check basic auth
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != 'admin123':
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check database name
    database = request.headers.get('Database')
    if not database or database != 'navision_db':
        return jsonify({'error': 'Invalid or missing database name'}), 400
    
    # Get classification filter if any
    classification = request.args.get('classification')
    
    # Filter data based on classification if provided
    loan_data = MOCK_DATA['navision']['tables'][5]['sample_data']
    if classification:
        loan_data = [loan for loan in loan_data if loan['Classification'] == classification.upper()]
    
    # Simulate some processing time
    time.sleep(0.5)
    return jsonify({'value': loan_data})

if __name__ == '__main__':
    app.run(port=5003)
