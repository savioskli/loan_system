from flask import Blueprint, jsonify, current_app
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint
from database.db_manager import db
import mysql.connector
import json

bp = Blueprint('post_disbursement', __name__)

def execute_endpoint_query(core_system, endpoint):
    """Execute a query for a specific endpoint"""
    try:
        parameters = json.loads(endpoint.parameters) if endpoint.parameters else {}
        
        # Connect to core banking database
        conn = mysql.connector.connect(
            host=core_system.base_url,
            port=core_system.port or 3306,
            user=core_system.auth_credentials.get('username'),
            password=core_system.auth_credentials.get('password'),
            database=core_system.database_name
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Build the query
        tables = parameters.get('tables', [])
        fields = parameters.get('fields', ['*'])
        joins = parameters.get('joins', [])
        filters = parameters.get('filters', {})
        group_by = parameters.get('group_by', [])
        
        # Construct the query
        query = f"SELECT {', '.join(fields)} FROM {tables[0]}"
        
        # Add joins
        for join in joins:
            query += f" JOIN {join['table']} ON {join['on']}"
            
        # Add group by if present
        if group_by:
            query += f" GROUP BY {', '.join(group_by)}"
            
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Convert decimal values to float for JSON serialization
        for row in result:
            for key, value in row.items():
                if isinstance(value, bytes):
                    row[key] = float(value)
        
        cursor.close()
        conn.close()
        
        return result[0] if result else {}  # Return first row since we're using aggregates
        
    except Exception as e:
        current_app.logger.error(f"Error executing endpoint query: {str(e)}")
        return {}

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

        # Get all required endpoints
        endpoints = {
            'loan_grading': CoreBankingEndpoint.query.filter_by(
                system_id=core_system.id,
                name='loan_grading',
                is_active=True
            ).first(),
            'total_loans': CoreBankingEndpoint.query.filter_by(
                system_id=core_system.id,
                name='total_loans',
                is_active=True
            ).first(),
            'outstanding_loans': CoreBankingEndpoint.query.filter_by(
                system_id=core_system.id,
                name='outstanding_loans',
                is_active=True
            ).first()
        }

        # Verify all required endpoints exist
        missing_endpoints = [name for name, endpoint in endpoints.items() if not endpoint]
        if missing_endpoints:
            return jsonify({
                'status': 'error',
                'message': f'Missing required endpoints: {", ".join(missing_endpoints)}'
            }), 400

        # Get loan grading data
        loan_grading_data = execute_endpoint_query(core_system, endpoints['loan_grading'])
        
        # Get total loans data
        total_loans_data = execute_endpoint_query(core_system, endpoints['total_loans'])
        
        # Get outstanding loans data
        outstanding_loans_data = execute_endpoint_query(core_system, endpoints['outstanding_loans'])

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

        return jsonify({
            'status': 'success',
            'data': {
                'loan_classifications': loan_classifications,
                'loan_grading': loan_grading_data,
                'total_loans': total_loans_data,
                'outstanding_loans': outstanding_loans_data
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error in post disbursement endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
