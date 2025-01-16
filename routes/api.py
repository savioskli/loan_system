from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
import mysql.connector
from config import db_config
from models.correspondence import Correspondence
from models.staff import Staff
from models.loan import Loan
from models.collection_schedule import CollectionSchedule
from datetime import datetime
from extensions import db, csrf

api_bp = Blueprint('api', __name__, url_prefix='/api')
csrf.exempt(api_bp)  # Remove CSRF protection from API routes since we handle it manually

@api_bp.route('/customers/search')
@login_required
def search_customers():
    """Search customers/clients from core banking database."""
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        if not query:
            current_app.logger.info('No query provided, returning empty result')
            return jsonify({
                'items': [],
                'has_more': False
            })

        # Connect to core banking database
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database='sacco_db',
            auth_plugin=db_config['auth_plugin']
        )
        cursor = conn.cursor(dictionary=True)

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Search query with LIKE for FullName and include loan and guarantor information
        search_term = f"%{query}%"
        sql = """
            SELECT 
                m.MemberID,
                m.FullName,
                GROUP_CONCAT(DISTINCT CONCAT_WS(':', 
                    l.LoanAppID, 
                    l.LoanNo,
                    l.LoanAmount,
                    COALESCE(lle.OutstandingBalance, 0)
                )) AS LoanInfo,
                GROUP_CONCAT(DISTINCT CONCAT_WS(':', 
                    g.GuarantorID,
                    gm.MemberID,
                    gm.FullName,
                    g.GuaranteedAmount,
                    g.Status
                )) AS GuarantorInfo
            FROM Members m
            LEFT JOIN LoanApplications l ON m.MemberID = l.MemberID
            LEFT JOIN (
                SELECT LoanID, OutstandingBalance
                FROM LoanLedgerEntries
                WHERE LedgerID IN (
                    SELECT MAX(LedgerID)
                    FROM LoanLedgerEntries
                    GROUP BY LoanID
                )
            ) lle ON l.LoanAppID = lle.LoanID
            LEFT JOIN Guarantors g ON l.LoanAppID = g.LoanAppID
            LEFT JOIN Members gm ON g.GuarantorMemberID = gm.MemberID
            WHERE 
                m.FullName LIKE %s
                AND m.Status = 'Active'
            GROUP BY m.MemberID
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (search_term, per_page, offset))
        members = cursor.fetchall()

        # Get total count for pagination
        count_sql = """
            SELECT COUNT(DISTINCT m.MemberID) as count
            FROM Members m
            WHERE 
                m.FullName LIKE %s
                AND m.Status = 'Active'
        """
        cursor.execute(count_sql, (search_term,))
        total_count = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        # Transform the results to match Select2 format
        items = []
        for member in members:
            loans = []
            guarantors = []
            
            # Process loan information
            if member['LoanInfo']:
                loan_info_list = member['LoanInfo'].split(',')
                for loan_info in loan_info_list:
                    loan_id, loan_no, loan_amount, outstanding = loan_info.split(':')
                    if loan_id and loan_no:  # Only add if we have valid loan info
                        loans.append({
                            'LoanAppID': loan_id,
                            'LoanNo': loan_no,
                            'LoanAmount': float(loan_amount) if loan_amount else 0,
                            'OutstandingBalance': float(outstanding) if outstanding else 0
                        })
            
            # Process guarantor information
            if member['GuarantorInfo']:
                guarantor_info_list = member['GuarantorInfo'].split(',')
                for guarantor_info in guarantor_info_list:
                    try:
                        guarantor_id, member_id, guarantor_name, guaranteed_amount, status = guarantor_info.split(':')
                        if guarantor_id and member_id and status == 'Active':  # Only add active guarantors
                            guarantors.append({
                                'GuarantorID': guarantor_id,
                                'MemberID': member_id,
                                'GuarantorName': guarantor_name,
                                'GuaranteedAmount': float(guaranteed_amount) if guaranteed_amount else 0,
                                'Status': status
                            })
                    except ValueError:
                        continue  # Skip malformed guarantor info

            items.append({
                'id': str(member['MemberID']),
                'text': member['FullName'],
                'loans': loans,
                'guarantors': guarantors
            })

        return jsonify({
            'items': items,
            'has_more': total_count > (page * per_page)
        })

    except Exception as e:
        current_app.logger.error(f'Error in customer search: {str(e)}')
        return jsonify({
            'items': [],
            'has_more': False,
            'error': 'An error occurred while searching'
        }), 500

@api_bp.route('/users/search', methods=['GET'])
@login_required
def search_users():
    """Search users from the database."""
    try:
        # Extract query parameters
        search_query = request.args.get('query', '').strip()

        if not search_query:
            current_app.logger.info('No query provided, returning empty result')
            return jsonify({'staff': []})

        # Connect to the database
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database='sacco_db',  # Use the appropriate database
            auth_plugin=db_config['auth_plugin']
        )
        cursor = conn.cursor(dictionary=True)

        # Search query with LIKE for multiple fields
        search_term = f"%{search_query}%"
        sql = """
            SELECT 
                UserID,
                FullName,
                BranchID
            FROM Users 
            WHERE 
                FullName LIKE %s
            AND status = 'Active'
        """
        cursor.execute(sql, (search_term,))  # Corrected to include a comma

        staff_members = cursor.fetchall()

        cursor.close()
        conn.close()

        # Transform the results to match the expected format
        staff_list = [{'UserID': staff['UserID'], 'FullName': staff['FullName'], 'BranchID': staff['BranchID']} for staff in staff_members]

        current_app.logger.info('Returning search results')
        # Return the data as a JSON response
        return jsonify({'staff': staff_list})

    except Exception as e:
        current_app.logger.error(f'Error in user search: {str(e)}')
        current_app.logger.info('Returning error response')
        return jsonify({'staff': [], 'error': 'An error occurred while searching'}), 500

@api_bp.route('/communications', methods=['POST'])
@login_required
def create_communication():
    """Create a new communication record"""
    try:
        data = request.json
        current_app.logger.info(f"Received data: {data}")
        
        # Get current staff member
        staff = Staff.query.filter_by(username=current_user.username).first()
        if not staff:
            current_app.logger.error('Staff record not found')
            current_app.logger.info('Returning error response')
            return jsonify({
                'status': 'error',
                'message': 'Staff record not found'
            }), 404
            
        # Create new communication
        try:
            new_comm = Correspondence(
                account_no=data['account_no'],
                client_name=data['client_name'],
                type=data['type'],
                message=data['message'],
                status=data.get('status', 'pending'),
                sent_by=current_user.username,
                staff_id=staff.id,
                recipient=data.get('recipient') or None,
                delivery_status=data.get('delivery_status') or None,
                delivery_time=datetime.strptime(data['delivery_time'], '%Y-%m-%dT%H:%M') if data.get('delivery_time') else None,
                call_duration=int(data['call_duration']) if data.get('call_duration') else None,
                call_outcome=data.get('call_outcome') or None,
                location=data.get('location') or None,
                visit_purpose=data.get('visit_purpose') or None,
                visit_outcome=data.get('visit_outcome') or None
            )
        except KeyError as e:
            current_app.logger.error(f"Missing required field: {e}")
            current_app.logger.info('Returning error response')
            return jsonify({
                'status': 'error',
                'message': f'Missing required field: {str(e)}'
            }), 400
        
        db.session.add(new_comm)
        db.session.commit()
        
        current_app.logger.info('Communication created successfully')
        current_app.logger.info('Returning success response')
        return jsonify({
            'status': 'success',
            'message': 'Communication created successfully',
            'data': new_comm.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating communication: {str(e)}")
        current_app.logger.info('Returning error response')
        return jsonify({
            'status': 'error',
            'message': 'Failed to create communication'
        }), 500

@api_bp.route('/new-collection-schedules', methods=['POST'])
@login_required
def create_collection_schedule():
    """Create a new collection schedule"""
    try:
        data = request.json
        current_app.logger.info(f"Received data: {data}")
        
        # Get current staff member
        staff = Staff.query.filter_by(username=current_user.username).first()
        if not staff:
            current_app.logger.error('Staff record not found')
            return jsonify({
                'status': 'error',
                'message': 'Staff record not found'
            }), 404

        # Create new collection schedule
        try:
            new_schedule = CollectionSchedule(
                staff_id=staff.id,
                client_id=data['client_id'],  # Keep this line for client_id
                loan_id=data['loan_id'],
                follow_up_deadline=data['follow_up_deadline'],
                collection_priority=data['collection_priority'],
                follow_up_frequency=data['follow_up_frequency'],
                next_follow_up_date=datetime.strptime(data['next_follow_up_date'], '%Y-%m-%dT%H:%M'),
                promised_payment_date=datetime.strptime(data['promised_payment_date'], '%Y-%m-%d'),
                attempts_allowed=data['attempts'],  # Change this line to attempts_allowed
                preferred_collection_method=data['preferred_collection_method'],
                task_description=data['task_description'],
                special_instructions=data.get('special_instructions', None),
                assigned_branch=data['branch_id']
            )
            
            db.session.add(new_schedule)
            db.session.commit()

            current_app.logger.info('Collection schedule created successfully')
            return jsonify({
                'status': 'success',
                'message': 'Collection schedule created successfully',
                'data': new_schedule.to_dict()  # Assuming to_dict() method exists in the model
            }), 201

        except KeyError as e:
            current_app.logger.error(f"Missing required field: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Missing required field: {str(e)}'
            }), 400

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating collection schedule: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while creating the collection schedule'
        }), 500
