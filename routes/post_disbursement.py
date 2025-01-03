from flask import Blueprint, jsonify, current_app
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint
from database.db_manager import db
import mysql.connector
import json

bp = Blueprint('post_disbursement', __name__)

@bp.route('/user/post-disbursement', methods=['GET'])
def get_post_disbursement_data():
    """Get post disbursement data including loan classifications and loan data"""
    try:
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({
                'status': 'error',
                'message': 'No active core banking system configured'
            }), 400

        # Get the loan grading endpoint configuration
        loan_grading_endpoint = CoreBankingEndpoint.query.filter_by(
            system_id=core_system.id,
            name='loan_grading',
            is_active=True
        ).first()

        if not loan_grading_endpoint:
            return jsonify({
                'status': 'error',
                'message': 'Loan grading endpoint not configured'
            }), 400

        # Parse endpoint parameters
        parameters = json.loads(loan_grading_endpoint.parameters) if loan_grading_endpoint.parameters else {}
        table_name = parameters.get('table_name', 'loan_grading')
        fields = parameters.get('fields', '*')

        # Connect to core banking database
        conn = mysql.connector.connect(
            host=core_system.base_url,
            port=core_system.port or 3306,
            user=core_system.auth_credentials.get('username'),
            password=core_system.auth_credentials.get('password'),
            database=parameters.get('database', 'loan_system')
        )

        cursor = conn.cursor(dictionary=True)

        # Get loan data
        if fields == '*':
            query = f"SELECT * FROM {table_name}"
        else:
            query = f"SELECT {', '.join(fields)} FROM {table_name}"

        cursor.execute(query)
        loans = cursor.fetchall()

        # Get loan grading analysis
        analysis_query = """
        SELECT 
            classification as risk_grade,
            COUNT(*) as loan_count,
            SUM(outstanding_balance) as total_exposure,
            AVG(days_in_arrears) as avg_days_in_arrears,
            MIN(days_in_arrears) as min_days_in_arrears,
            MAX(days_in_arrears) as max_days_in_arrears
        FROM loan_grading
        GROUP BY classification
        """
        cursor.execute(analysis_query)
        analysis = cursor.fetchall()

        # Close database connection
        cursor.close()
        conn.close()

        # Define loan classifications based on the data model
        loan_classifications = [
            {
                'code': 'N',
                'name': 'Normal (Performing Loans)',
                'description': 'Payments are up to date or overdue by less than 30 days',
                'days_range': '0-30',
                'provision_rate': 1
            },
            {
                'code': 'W',
                'name': 'Watch (Special Mention)',
                'description': 'Payments are overdue by 31 to 90 days',
                'days_range': '31-90',
                'provision_rate': 3
            },
            {
                'code': 'S',
                'name': 'Substandard',
                'description': 'Payments are overdue by 91 to 180 days',
                'days_range': '91-180',
                'provision_rate': 20
            },
            {
                'code': 'D',
                'name': 'Doubtful',
                'description': 'Payments are overdue by 181 to 360 days',
                'days_range': '181-360',
                'provision_rate': 50
            },
            {
                'code': 'L',
                'name': 'Loss (Non-Performing)',
                'description': 'Payments are overdue by more than 360 days',
                'days_range': '>360',
                'provision_rate': 100
            }
        ]

        # Convert decimal values to float for JSON serialization
        for loan in loans:
            for key, value in loan.items():
                if isinstance(value, bytes):
                    loan[key] = float(value)

        for item in analysis:
            for key, value in item.items():
                if isinstance(value, bytes):
                    item[key] = float(value)

        return jsonify({
            'status': 'success',
            'data': {
                'loan_classifications': loan_classifications,
                'loans': loans,
                'analysis': analysis
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error in post disbursement endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
