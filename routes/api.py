from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
import mysql.connector
import json
from config import db_config
from models.correspondence import Correspondence
from models.staff import Staff
from models.loan import Loan
from models.collection_schedule import CollectionSchedule
from datetime import datetime
from extensions import db, csrf
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from models.letter_template import LetterTemplate  # Import LetterTemplate model
from models.core_banking import CoreBankingSystem  # Import CoreBankingSystem model
from models.post_disbursement_modules import ExpectedStructure, ActualStructure  # Import mapping models
from sqlalchemy import text, select  # Import text function for raw SQL queries

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
            
        # Statically define the module ID for customer search
        module_id = 8  # Module ID for customer search
            
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            current_app.logger.error('No active core banking system configured')
            return jsonify({
                'error': 'No active core banking system configured',
                'items': [],
                'has_more': False
            }), 500

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }
        current_app.logger.info(f"Connecting to database: {core_system.database_name}")

        try:
            conn = mysql.connector.connect(**core_banking_config)
        except mysql.connector.Error as e:
            current_app.logger.error(f"Error connecting to database: {str(e)}")
            return jsonify({
                'error': f'Error connecting to database: {str(e)}',
                'items': [],
                'has_more': False
            }), 500
        cursor = conn.cursor(dictionary=True)

        # Retrieve the mapping data for customer search module
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    # Retrieve expected and actual columns as lists
                    expected_columns = expected.columns  # e.g., ['MemberID', 'FullName', ...]
                    actual_columns = actual.columns     # e.g., ['member_id', 'full_name', ...]
                    
                    # Create a dictionary mapping expected to actual columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict  # Now a dictionary
                    }
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Mapping Data for customer search: {mapping}")
        except Exception as e:
            current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
            return jsonify({
                'error': f'Error retrieving mapping data: {str(e)}',
                'items': [],
                'has_more': False
            }), 500

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Build dynamic query based on mapping
        def build_dynamic_query(mapping, search_term, per_page, offset):
            try:
                # Access the mapping correctly using string keys
                members = mapping.get("Members", {})
                loan_apps = mapping.get("LoanApplications", {})
                loan_ledger = mapping.get("LoanLedgerEntries", {})
                guarantors = mapping.get("Guarantors", {})
                
                # Ensure that the necessary tables and columns are present in the mapping
                if not members or not "columns" in members:
                    raise KeyError("Missing Members table in mapping")
                
                # Get column mappings
                m_cols = members["columns"]
                l_cols = loan_apps.get("columns", {}) if loan_apps else {}
                lle_cols = loan_ledger.get("columns", {}) if loan_ledger else {}
                g_cols = guarantors.get("columns", {}) if guarantors else {}
                
                # Build the dynamic SQL query
                sql = f"""
                SELECT 
                    m.{m_cols.get('MemberID', 'MemberID')} AS MemberID,
                    m.{m_cols.get('FullName', 'FullName')} AS FullName"""
                
                # Add loan information if available
                if loan_apps and loan_ledger:
                    sql += f"""
                    ,GROUP_CONCAT(DISTINCT CONCAT_WS(':', 
                        l.{l_cols.get('LoanAppID', 'LoanAppID')}, 
                        l.{l_cols.get('LoanNo', 'LoanNo')},
                        COALESCE(l.{l_cols.get('LoanAmount', 'LoanAmount')}, 0),
                        COALESCE(lle.{lle_cols.get('OutstandingBalance', 'OutstandingBalance')}, 0),
                        COALESCE(l.{l_cols.get('RepaymentPeriod', 'RepaymentPeriod')}, 0)
                    )) AS LoanInfo"""
                
                # Add guarantor information if available
                if guarantors:
                    sql += f"""
                    ,GROUP_CONCAT(DISTINCT 
                        CASE 
                            WHEN g.{g_cols.get('GuarantorID', 'GuarantorID')} IS NOT NULL 
                            THEN CONCAT_WS(':', 
                                COALESCE(g.{g_cols.get('GuarantorID', 'GuarantorID')}, ''),
                                COALESCE(g.{g_cols.get('GuarantorMemberID', 'GuarantorMemberID')}, ''),
                                COALESCE(gm.{m_cols.get('FullName', 'FullName')}, ''),
                                COALESCE(g.{g_cols.get('GuaranteedAmount', 'GuaranteedAmount')}, 0),
                                COALESCE(g.{g_cols.get('Status', 'Status')}, ''),
                                COALESCE(l.{l_cols.get('LoanAppID', 'LoanAppID')}, '')
                            )
                        END
                    ) AS GuarantorInfo"""
                
                # FROM clause
                sql += f"""
                FROM {members["actual_table_name"]} m"""
                
                # JOINs
                if loan_apps:
                    sql += f"""
                    LEFT JOIN {loan_apps["actual_table_name"]} l ON m.{m_cols.get('MemberID', 'MemberID')} = l.{l_cols.get('MemberID', 'MemberID')}"""
                
                if loan_ledger:
                    sql += f"""
                    LEFT JOIN (
                        SELECT {lle_cols.get('LoanID', 'LoanID')} AS LoanID, {lle_cols.get('OutstandingBalance', 'OutstandingBalance')} AS OutstandingBalance
                        FROM {loan_ledger["actual_table_name"]}
                        WHERE {lle_cols.get('LedgerID', 'LedgerID')} IN (
                            SELECT MAX({lle_cols.get('LedgerID', 'LedgerID')})
                            FROM {loan_ledger["actual_table_name"]}
                            GROUP BY {lle_cols.get('LoanID', 'LoanID')}
                        )
                    ) lle ON l.{l_cols.get('LoanAppID', 'LoanAppID')} = lle.LoanID"""
                
                if guarantors:
                    sql += f"""
                    LEFT JOIN {guarantors["actual_table_name"]} g ON l.{l_cols.get('LoanAppID', 'LoanAppID')} = g.{g_cols.get('LoanAppID', 'LoanAppID')}
                    LEFT JOIN {members["actual_table_name"]} gm ON g.{g_cols.get('GuarantorMemberID', 'GuarantorMemberID')} = gm.{m_cols.get('MemberID', 'MemberID')}"""
                
                # WHERE clause
                sql += f"""
                WHERE 
                    m.{m_cols.get('FullName', 'FullName')} LIKE %s"""
                
                # Add status filter if available
                if 'Status' in m_cols:
                    sql += f"""
                    AND m.{m_cols.get('Status', 'Status')} = 'Active'"""
                
                # GROUP BY, LIMIT, OFFSET
                sql += f"""
                GROUP BY m.{m_cols.get('MemberID', 'MemberID')}
                LIMIT %s OFFSET %s
                """
                
                return sql
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise
        
        try:
            # Build the dynamic query
            search_term = f"%{query}%"
            sql = build_dynamic_query(mapping, search_term, per_page, offset)
            current_app.logger.info(f"Dynamic SQL query: {sql}")
            cursor.execute(sql, (search_term, per_page, offset))
        except Exception as e:
            current_app.logger.error(f"Error executing dynamic query: {str(e)}")
            return jsonify({
                'error': f'Error searching customers: {str(e)}',
                'items': [],
                'has_more': False
            }), 500
        members = cursor.fetchall()

        # Get total count for pagination
        try:
            # Build dynamic count query based on mapping
            members_table = mapping.get("Members", {})
            if not members_table or not "columns" in members_table:
                raise KeyError("Missing Members table in mapping")
                
            m_cols = members_table["columns"]
            
            count_sql = f"""
                SELECT COUNT(DISTINCT m.{m_cols.get('MemberID', 'MemberID')}) as count
                FROM {members_table["actual_table_name"]} m
                WHERE 
                    m.{m_cols.get('FullName', 'FullName')} LIKE %s
            """
            
            # Add status filter if available
            if 'Status' in m_cols:
                count_sql += f"""
                    AND m.{m_cols.get('Status', 'Status')} = 'Active'
                """
                
            count_sql += """
            """
            
            current_app.logger.info(f"Dynamic count SQL query: {count_sql}")
            cursor.execute(count_sql, (search_term,))
        except Exception as e:
            current_app.logger.error(f"Error executing count query: {str(e)}")
            return jsonify({
                'error': f'Error counting customers: {str(e)}',
                'items': [],
                'has_more': False
            }), 500
        total_count = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        # Transform the results to match Select2 format
        items = []
        for member in members:
            loans = []
            guarantors = []
            
            # Get the mapping data for field names
            loan_apps = mapping.get("LoanApplications", {})
            loan_ledger = mapping.get("LoanLedgerEntries", {})
            guarantors_mapping = mapping.get("Guarantors", {})
            
            # Process loan information
            if 'LoanInfo' in member and member['LoanInfo']:
                loan_info_list = member['LoanInfo'].split(',')
                for loan_info in loan_info_list:
                    try:
                        loan_id, loan_no, loan_amount, outstanding, repayment_period = loan_info.split(':')
                        if loan_id and loan_no:  # Only add if we have valid loan info
                            # Use the expected column names for the client-side
                            loans.append({
                                'LoanAppID': loan_id,
                                'LoanNo': loan_no,
                                'LoanAmount': float(loan_amount) if loan_amount else 0,
                                # Use OutstandingBalance as per the memory
                                'OutstandingBalance': float(outstanding) if outstanding else 0,
                                'RepaymentPeriod': int(repayment_period) if repayment_period else 0
                            })
                    except ValueError as e:
                        current_app.logger.error(f"Error parsing loan info: {loan_info}, Error: {str(e)}")
                        continue
            
            # Process guarantor information
            if 'GuarantorInfo' in member and member['GuarantorInfo'] and member['GuarantorInfo'] != 'NULL':
                current_app.logger.info(f"Raw GuarantorInfo: {member['GuarantorInfo']}")
                guarantor_info_list = [g for g in member['GuarantorInfo'].split(',') if g]  # Filter out empty strings
                for guarantor_info in guarantor_info_list:
                    try:
                        fields = guarantor_info.split(':')
                        if len(fields) == 6:  # Only process if we have all fields
                            guarantor_id, member_id, guarantor_name, guaranteed_amount, status, loan_app_id = fields
                            # Check if status is Active - use the expected value for client-side
                            if guarantor_id and member_id and status == 'Active':
                                guarantors.append({
                                    'GuarantorID': guarantor_id,
                                    'GuarantorMemberID': member_id,
                                    'GuarantorName': guarantor_name.strip() if guarantor_name else '',
                                    'GuaranteedAmount': float(guaranteed_amount) if guaranteed_amount else 0,
                                    'Status': status,
                                    'LoanAppID': loan_app_id
                                })
                    except ValueError as e:
                        current_app.logger.error(f"Error parsing guarantor info: {guarantor_info}, Error: {str(e)}")
                        continue

            result = {
                'id': str(member['MemberID']),
                'text': member['FullName'],
                'loans': loans,
                'guarantors': guarantors
            }
            current_app.logger.info(f"Processed member result: {result}")
            items.append(result)

        response = {
            'items': items,
            'has_more': total_count > (page * per_page)
        }
        current_app.logger.info(f"API Response: {response}")
        return jsonify(response)

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
    """Create a new communication record and send SMS/Email if applicable"""
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
                status='pending',  # Always start with pending
                sent_by=current_user.username,
                staff_id=staff.id,
                recipient=data.get('recipient') or None,
                delivery_status=None,  # Will be updated after sending
                delivery_time=None,  # Will be updated after sending
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
        
        # Add to database first to get an ID
        db.session.add(new_comm)
        db.session.commit()
        
        # Send SMS if the communication type is SMS
        if data['type'] == 'sms' and data.get('recipient'):
            try:
                from services.infobip_sms_service import InfobipSmsService
                from models.sms_gateway import SmsGatewayConfig
                from utils.encryption import decrypt_value
                
                # Get SMS gateway configuration
                config = SmsGatewayConfig.query.first()
                if not config:
                    current_app.logger.error('SMS Gateway configuration not found')
                    new_comm.status = 'failed'
                    new_comm.delivery_status = 'SMS Gateway configuration not found'
                else:
                    try:
                        # Decrypt API key
                        api_key = decrypt_value(config.sms_api_key)
                        
                        # Initialize SMS service
                        sms_service = InfobipSmsService(
                            api_key=api_key,
                            default_sender_id=config.sms_sender_id
                        )
                        
                        # Send SMS
                        success = sms_service.send_sms(
                            to=data['recipient'],
                            message=data['message']
                        )
                        
                        # Update communication status
                        if success:
                            new_comm.status = 'delivered'
                            new_comm.delivery_status = 'Sent successfully'
                            new_comm.delivery_time = datetime.now()
                        else:
                            new_comm.status = 'failed'
                            new_comm.delivery_status = 'Failed to send SMS'
                            
                        db.session.commit()
                        current_app.logger.info(f'SMS sent with status: {success}')
                    except Exception as e:
                        current_app.logger.error(f'Error sending SMS: {str(e)}')
                        new_comm.status = 'failed'
                        new_comm.delivery_status = f'Error: {str(e)}'
                        db.session.commit()
            except Exception as e:
                current_app.logger.error(f'Error in SMS service: {str(e)}')
                new_comm.status = 'failed'
                new_comm.delivery_status = f'Service error: {str(e)}'
                db.session.commit()
        
        # Send Email if the communication type is email (placeholder for future implementation)
        elif data['type'] == 'email' and data.get('recipient'):
            # TODO: Implement email sending functionality
            current_app.logger.info('Email sending not yet implemented')
            new_comm.status = 'pending'
            new_comm.delivery_status = 'Email sending not implemented yet'
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
            # Log the incoming data for debugging
            current_app.logger.info(f'Creating collection schedule with data: {data}')
            
            # Create new schedule
            new_schedule = CollectionSchedule(
                assigned_id=data['assigned_id'],  # Using assigned_id consistently
                client_id=data['client_id'],  # Reference to client in core banking system
                loan_id=data['loan_id'],
                supervisor_id=data.get('supervisor_id'),  # Add supervisor_id
                manager_id=data.get('manager_id'),  # Add manager_id
                follow_up_deadline=data['follow_up_deadline'],
                collection_priority=data['collection_priority'],
                follow_up_frequency=data['follow_up_frequency'],
                next_follow_up_date=datetime.strptime(data['next_follow_up_date'], '%Y-%m-%dT%H:%M'),
                promised_payment_date=datetime.strptime(data['promised_payment_date'], '%Y-%m-%d'),
                attempts_allowed=data['attempts'],  # Change this line to attempts_allowed
                preferred_collection_method=data['preferred_collection_method'],
                task_description=data['task_description'],
                special_instructions=data.get('special_instructions', None),
                assigned_branch=data['branch_id'],
                
                # Add loan details
                outstanding_balance=float(data.get('outstanding_balance', 0)),
                missed_payments=int(data.get('missed_payments', 0)),
                
                # Add contact details
                best_contact_time=data.get('best_contact_time'),
                collection_location=data.get('collection_location'),
                alternative_contact=data.get('alternative_contact')
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

@api_bp.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        staff = Staff.query.filter_by(username=current_user.username).first()
        if not staff:
            return jsonify({
                'status': 'error',
                'message': 'Staff record not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': {
                'id': staff.id,
                'username': staff.username,
                'role': staff.role.name if staff.role else None
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting current user: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while getting current user information'
        }), 500

@api_bp.route('/collection-schedules/<int:schedule_id>', methods=['GET'])
@login_required
def get_collection_schedule(schedule_id):
    """Get details of a specific collection schedule."""
    try:
        schedule = CollectionSchedule.query.get(schedule_id)
        if not schedule:
            return jsonify({
                'status': 'error',
                'message': 'Schedule not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': schedule.to_dict()
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error fetching schedule: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch schedule details'
        }), 500

@api_bp.route('/collection-schedules/<int:schedule_id>/comment', methods=['POST'])
@login_required
def add_schedule_comment(schedule_id):
    """Add a comment to a collection schedule."""
    try:
        data = request.get_json()
        comment = data.get('comment')
        action = data.get('action')

        if not comment:
            return jsonify({
                'status': 'error',
                'message': 'Comment is required'
            }), 400

        schedule = CollectionSchedule.query.get(schedule_id)
        if not schedule:
            return jsonify({
                'status': 'error',
                'message': 'Schedule not found'
            }), 404

        # Create correspondence record
        correspondence = Correspondence(
            loan_id=schedule.loan_id,
            staff_id=current_user.id,
            message=comment,
            type='comment',
            status='active'
        )
        db.session.add(correspondence)

        # Update schedule status if this is a submit action
        if action == 'submit':
            schedule.progress_status = 'pending_review'
            schedule.last_updated = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Comment added successfully'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error adding comment: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to add comment'
        }), 500

@api_bp.route('/collection-schedules/<int:schedule_id>/update', methods=['POST'])
@login_required
def update_collection_schedule(schedule_id):
    """Update a collection schedule progress."""
    try:
        data = request.get_json()
        comment = data.get('comment')
        status = data.get('status', 'in_progress')

        if not comment:
            return jsonify({
                'status': 'error',
                'message': 'Update notes are required'
            }), 400

        schedule = CollectionSchedule.query.get(schedule_id)
        if not schedule:
            return jsonify({
                'status': 'error',
                'message': 'Schedule not found'
            }), 404

        # Only assigned staff can update the schedule
        if schedule.assigned_id != current_user.id:
            return jsonify({
                'status': 'error',
                'message': 'Only assigned staff can update this schedule'
            }), 403

        # Create correspondence record for the update
        correspondence = Correspondence(
            loan_id=schedule.loan_id,
            staff_id=current_user.id,
            message=comment,
            type='update',
            status='active'
        )
        db.session.add(correspondence)

        # Update schedule
        schedule.notes = comment
        schedule.progress_status = status
        schedule.last_updated = datetime.utcnow()
        schedule.attempts_made = schedule.attempts_made + 1

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Schedule updated successfully'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error updating schedule: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update schedule'
        }), 500

@api_bp.route('/guarantor-claims/create', methods=['POST'])
@login_required
def create_guarantor_claim():
    """Create a new guarantor claim with document attachments."""
    try:
        # Extract form data
        data = request.form
        
        # Validate required fields
        required_fields = {
            'loanId': 'Loan ID',
            'loanNo': 'Loan Number',
            'borrowerId': 'Borrower ID',
            'borrowerName': 'Borrower Name',
            'guarantorId': 'Guarantor ID',
            'guarantorName': 'Guarantor Name',
            'claimAmount': 'Claim Amount'
        }
        
        for field, label in required_fields.items():
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'{label} is required'
                }), 400

        # Handle document uploads
        document_paths = []
        if 'documents' in request.files:
            files = request.files.getlist('documents')
            for file in files:
                if file and file.filename:
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'claims')
                        os.makedirs(upload_dir, exist_ok=True)
                        file_path = os.path.join('uploads/claims', filename)
                        file.save(os.path.join(upload_dir, filename))
                        document_paths.append(file_path)
                    else:
                        return jsonify({
                            'status': 'error',
                            'message': f'Invalid file type: {file.filename}'
                        }), 400

        # Connect to database
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database='loan_system',
            auth_plugin=db_config['auth_plugin']
        )
        cursor = conn.cursor(dictionary=True)

        try:
            # Start transaction
            conn.start_transaction()

            # Insert claim record
            sql = """
            INSERT INTO guarantor_claims (
                loan_id, loan_no, borrower_id, borrower_name,
                guarantor_id, guarantor_name, claim_amount,
                claim_date, status, notes, document_path,
                created_by, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                NOW(), 'Pending', %s, %s, %s, NOW()
            )
            """
            
            cursor.execute(sql, (
                data['loanId'],
                data['loanNo'],
                data['borrowerId'],
                data['borrowerName'],
                data['guarantorId'],
                data['guarantorName'],
                data['claimAmount'],
                data.get('notes', ''),
                ','.join(document_paths) if document_paths else None,
                current_user.id
            ))

            # Get the inserted claim ID
            claim_id = cursor.lastrowid

            # Commit transaction
            conn.commit()

            current_app.logger.info(f"Successfully created guarantor claim with ID: {claim_id}")
            
            return jsonify({
                'status': 'success',
                'message': 'Guarantor claim submitted successfully',
                'claimId': claim_id
            }), 201

        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Database error in guarantor claim creation: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Database error occurred'
            }), 500

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        current_app.logger.error(f"Error creating guarantor claim: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your request'
        }), 500

@api_bp.route('/letter_templates', methods=['GET'])
@login_required
def get_letter_templates():
    """Get letter templates for a specific letter type."""
    letter_type_id = request.args.get('letter_type_id')
    
    if not letter_type_id:
        current_app.logger.error('No letter_type_id provided')
        return jsonify({'error': 'Letter type ID is required'}), 400
    
    try:
        # Log the incoming letter_type_id
        current_app.logger.info(f'Fetching letter templates for letter_type_id: {letter_type_id}')
        
        # Use explicit column selection to avoid automatic column inclusion
        stmt = select(
            LetterTemplate.id, 
            LetterTemplate.letter_type_id, 
            LetterTemplate.name, 
            LetterTemplate.template_content, 
            LetterTemplate.is_active
        ).where(
            LetterTemplate.letter_type_id == int(letter_type_id),
            LetterTemplate.is_active == True
        )
        
        # Execute the query
        result = db.session.execute(stmt)
        
        # Convert results to list of dictionaries
        template_list = [
            {
                'id': row.id, 
                'letter_type_id': row.letter_type_id,
                'name': row.name, 
                'template_content': row.template_content,
                'is_active': row.is_active
            } 
            for row in result
        ]
        
        # Log the number of templates found
        current_app.logger.info(f'Found {len(template_list)} templates for letter_type_id: {letter_type_id}')
        
        return jsonify(template_list)
    
    except Exception as e:
        current_app.logger.error(f'Error fetching letter templates for letter_type_id {letter_type_id}: {str(e)}')
        return jsonify({'error': 'Failed to fetch letter templates'}), 500

@api_bp.route('/guarantor-claims', methods=['GET'])
@login_required
def get_guarantor_claims():
    """Get paginated list of guarantor claims with optional filters."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')

        # Calculate offset
        offset = (page - 1) * per_page

        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Build base query
        query = """
            SELECT 
                gc.*,
                s.username as created_by_name,
                COALESCE(s2.username, '') as updated_by_name
            FROM guarantor_claims gc
            LEFT JOIN staff s ON gc.created_by = s.id
            LEFT JOIN staff s2 ON gc.updated_by = s2.id
            WHERE 1=1
        """
        count_query = "SELECT COUNT(*) as total FROM guarantor_claims WHERE 1=1"
        params = []

        # Add filters
        if status:
            query += " AND gc.status = %s"
            count_query += " AND status = %s"
            params.append(status)

        if start_date:
            query += " AND gc.claim_date >= %s"
            count_query += " AND claim_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND gc.claim_date <= %s"
            count_query += " AND claim_date <= %s"
            params.append(end_date)

        if search:
            search_term = f"%{search}%"
            query += """ AND (
                gc.loan_no LIKE %s OR 
                gc.borrower_name LIKE %s OR 
                gc.guarantor_name LIKE %s
            )"""
            count_query += """ AND (
                loan_no LIKE %s OR 
                borrower_name LIKE %s OR 
                guarantor_name LIKE %s
            )"""
            params.extend([search_term, search_term, search_term])

        # Add sorting and pagination
        query += " ORDER BY gc.created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        # Execute queries
        cursor.execute(count_query, params[:-2])
        total_count = cursor.fetchone()['total']

        cursor.execute(query, params)
        claims = cursor.fetchall()

        # Process results
        for claim in claims:
            # Convert decimal to float for JSON serialization
            claim['claim_amount'] = float(claim['claim_amount'])
            # Format dates
            claim['claim_date'] = claim['claim_date'].strftime('%Y-%m-%d')
            claim['created_at'] = claim['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if claim['updated_at']:
                claim['updated_at'] = claim['updated_at'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({
            'items': claims,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching guarantor claims: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch guarantor claims'
        }), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@api_bp.route('/guarantor-claims/stats', methods=['GET'])
@login_required
def get_guarantor_claims_stats():
    """Get statistics for guarantor claims."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get claims statistics
        stats_query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN status = 'pending' THEN claim_amount ELSE 0 END) as pending_amount,
                SUM(CASE WHEN status = 'approved' THEN claim_amount ELSE 0 END) as approved_amount
            FROM guarantor_claims
        """
        cursor.execute(stats_query)
        stats = cursor.fetchone()
        
        return jsonify({
            'status': 'success',
            'data': {
                'total': stats['total'] or 0,
                'pending': stats['pending'] or 0,
                'approved': stats['approved'] or 0,
                'rejected': stats['rejected'] or 0,
                'pending_amount': float(stats['pending_amount'] or 0),
                'approved_amount': float(stats['approved_amount'] or 0)
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"Error fetching guarantor claims stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch statistics'
        }), 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@api_bp.route('/loans/<int:loan_id>', methods=['GET'])
@login_required
def get_loan_details(loan_id):
    """Get details for a specific loan."""
    try:
        # Statically define the module ID
        module_id = 1  # Module ID for loan data

        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 400

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    expected_columns = expected.columns
                    actual_columns = actual.columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict
                    }
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Mapping Data: {mapping}")
        except Exception as e:
            return jsonify({'error': f'Error retrieving mapping data: {str(e)}'}), 500

        # Build dynamic query for a specific loan
        def build_loan_query(mapping, loan_id):
            try:
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})
                m = mapping.get("Members", {})
                guarantors = mapping.get("Guarantors", {})
                
                # Define base query
                base_query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    l.{ll["columns"]["ArrearsAmount"]} AS ArrearsAmount,
                    l.{ll["columns"]["ArrearsDays"]} AS ArrearsDays,
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus,
                    CONCAT(m.{m["columns"]["FirstName"]}, ' ', m.{m["columns"]["LastName"]}) AS CustomerName
                """
                
                # Add guarantor information if available
                guarantor_query = ""
                if guarantors and "columns" in guarantors and "actual_table_name" in guarantors:
                    g_cols = guarantors.get("columns", {})
                    guarantor_query = f"""
                    ,GROUP_CONCAT(
                        CASE
                            WHEN g.{g_cols.get('GuarantorID', 'GuarantorID')} IS NOT NULL 
                            THEN CONCAT(
                                COALESCE(g.{g_cols.get('GuarantorID', 'GuarantorID')}, ''),
                                ':', COALESCE(g.{g_cols.get('GuarantorMemberID', 'GuarantorMemberID')}, ''),
                                ':', COALESCE(CONCAT(gm.{m["columns"]["FirstName"]}, ' ', gm.{m["columns"]["LastName"]}), ''),
                                ':', COALESCE(g.{g_cols.get('GuaranteedAmount', 'GuaranteedAmount')}, '0'),
                                ':', COALESCE(g.{g_cols.get('Status', 'Status')}, 'Unknown'),
                                ':', COALESCE(g.{g_cols.get('LoanAppID', 'LoanAppID')}, '')
                            )
                            ELSE NULL
                        END
                        SEPARATOR ','
                    ) AS GuarantorInfo
                    """
                
                # Combine queries
                from_query = f"""
                FROM {ll["actual_table_name"]} l
                JOIN (
                    SELECT {ll["columns"]["LoanID"]} AS LoanID,
                        MAX({ll["columns"]["LedgerID"]}) AS latest_id
                    FROM {ll["actual_table_name"]}
                    GROUP BY {ll["columns"]["LoanID"]}
                ) latest ON l.{ll["columns"]["LoanID"]} = latest.LoanID AND l.{ll["columns"]["LedgerID"]} = latest.latest_id
                JOIN {la["actual_table_name"]} la ON l.{ll["columns"]["LoanID"]} = la.{la["columns"]["LoanAppID"]}
                JOIN {ld["actual_table_name"]} ld ON la.{la["columns"]["LoanAppID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {m["actual_table_name"]} m ON la.{la["columns"]["MemberID"]} = m.{m["columns"]["MemberID"]}
                """
                
                # Add guarantor joins if available
                if guarantors and "columns" in guarantors and "actual_table_name" in guarantors:
                    g_cols = guarantors.get("columns", {})
                    from_query += f"""
                    LEFT JOIN {guarantors["actual_table_name"]} g ON la.{la["columns"]["LoanAppID"]} = g.{g_cols.get('LoanAppID', 'LoanAppID')}
                    LEFT JOIN {m["actual_table_name"]} gm ON g.{g_cols.get('GuarantorMemberID', 'GuarantorMemberID')} = gm.{m["columns"]["MemberID"]}
                    """
                
                # Add where clause
                where_clause = f"""WHERE l.{ll["columns"]["LoanID"]} = %s"""
                
                # Add group by if using guarantors
                group_by = ""
                if guarantors and "columns" in guarantors and "actual_table_name" in guarantors:
                    group_by = f"""GROUP BY l.{ll["columns"]["LoanID"]}, l.{ll["columns"]["OutstandingBalance"]}, l.{ll["columns"]["ArrearsAmount"]}, l.{ll["columns"]["ArrearsDays"]}, la.{la["columns"]["LoanNo"]}, la.{la["columns"]["LoanAmount"]}, ld.{ld["columns"]["LoanStatus"]}, m.{m["columns"]["FirstName"]}, m.{m["columns"]["LastName"]}"""

                
                # Combine all parts of the query
                query = f"""{base_query} {guarantor_query} {from_query} {where_clause} {group_by}"""
                
                return query
            except Exception as e:
                current_app.logger.error(f"Error building loan query: {str(e)}")
                raise

        try:
            query = build_loan_query(mapping, loan_id)
            current_app.logger.info(f"Executing loan query: {query}")
            cursor.execute(query, (loan_id,))
            loan_data = cursor.fetchone()
            
            if not loan_data:
                return jsonify({'error': 'Loan not found'}), 404
                
            # Format the loan data
            loan_dict = dict(loan_data)
            
            # Process guarantor information if available
            guarantors = []
            if 'GuarantorInfo' in loan_dict and loan_dict['GuarantorInfo'] and loan_dict['GuarantorInfo'] != 'NULL':
                current_app.logger.info(f"Raw GuarantorInfo: {loan_dict['GuarantorInfo']}")
                guarantor_info_list = [g for g in loan_dict['GuarantorInfo'].split(',') if g]  # Filter out empty strings
                for guarantor_info in guarantor_info_list:
                    try:
                        fields = guarantor_info.split(':')
                        if len(fields) >= 6:
                            guarantor_id, member_id, guarantor_name, guaranteed_amount, status, loan_app_id = fields
                            
                            if guarantor_id and member_id and status == 'Active':
                                guarantors.append({
                                    'guarantor_id': guarantor_id,
                                    'member_id': member_id,
                                    'name': guarantor_name.strip() if guarantor_name else '',
                                    'guaranteed_amount': float(guaranteed_amount) if guaranteed_amount and guaranteed_amount.strip() else 0,
                                    'status': status
                                })
                    except Exception as e:
                        current_app.logger.error(f"Error parsing guarantor info: {guarantor_info}, Error: {str(e)}")
            
            formatted_loan = {
                'loan_id': loan_dict['LoanID'],
                'loan_no': loan_dict['LoanNo'],
                'customer_name': loan_dict['CustomerName'],
                'outstanding_balance': float(loan_dict['OutstandingBalance']),
                'arrears_amount': float(loan_dict.get('ArrearsAmount', 0)),
                'days_in_arrears': int(loan_dict.get('ArrearsDays', 0)),
                'loan_amount': float(loan_dict['LoanAmount']),
                'loan_status': loan_dict['LoanStatus'],
                'guarantors': guarantors
            }
            
            return jsonify(formatted_loan)
            
        except Exception as e:
            current_app.logger.error(f"Error fetching loan details: {str(e)}")
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in get_loan_details: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@api_bp.route('/borrower/<loan_id>', methods=['GET'])
@login_required
def get_borrower_name(loan_id):
    """Get borrower name from core banking system using loan ID."""
    try:
        # Statically define the module ID
        module_id = 1  # Module ID for loan data

        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 400

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    expected_columns = expected.columns
                    actual_columns = actual.columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict
                    }
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Mapping Data: {mapping}")
        except Exception as e:
            return jsonify({'error': f'Error retrieving mapping data: {str(e)}'}), 500

        # Build dynamic query
        def build_dynamic_query(mapping):
            try:
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})
                m = mapping.get("Members", {})
                
                # Ensure that the necessary columns are present in the mapping
                required_ll_columns = ["LoanID"]
                required_ld_columns = ["LoanAppID"]
                required_la_columns = ["LoanAppID", "MemberID"]
                required_m_columns = ["MemberID", "FirstName", "LastName"]

                if not all(column in ll.get("columns", []) for column in required_ll_columns):
                    raise KeyError(f"Missing columns in LoanLedgerEntries mapping: {required_ll_columns}")

                if not all(column in ld.get("columns", []) for column in required_ld_columns):
                    raise KeyError(f"Missing columns in LoanDisbursements mapping: {required_ld_columns}")

                if not all(column in la.get("columns", []) for column in required_la_columns):
                    raise KeyError(f"Missing columns in LoanApplications mapping: {required_la_columns}")

                if not all(column in m.get("columns", []) for column in required_m_columns):
                    raise KeyError(f"Missing columns in Members mapping: {required_m_columns}")

                query = f"""
                SELECT
                    m.{m["columns"]["FirstName"]} AS FirstName,
                    m.{m["columns"]["LastName"]} AS LastName
                FROM {ll["actual_table_name"]} l
                JOIN {ld["actual_table_name"]} ld ON l.{ll["columns"]["LoanID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {la["actual_table_name"]} la ON ld.{ld["columns"]["LoanAppID"]} = la.{la["columns"]["LoanAppID"]}
                JOIN {m["actual_table_name"]} m ON la.{la["columns"]["MemberID"]} = m.{m["columns"]["MemberID"]}
                WHERE l.{ll["columns"]["LoanID"]} = %s
                """
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        try:
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Dynamic Query: {query}")
            
            # Execute query
            cursor.execute(query, (loan_id,))
            result = cursor.fetchone()
            
            if result:
                # Construct full name from first and last name
                name_parts = [result['FirstName'], result['LastName']]
                borrower_name = ' '.join(filter(None, name_parts))
                
                return jsonify({
                    'success': True,
                    'borrower_name': borrower_name
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Borrower not found'
                }), 404

        except mysql.connector.Error as e:
            current_app.logger.error(f"Database error: {str(e)}")
            return jsonify({'error': 'Database error'}), 500
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        current_app.logger.error(f"Error getting borrower name: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/overdue-loans', methods=['GET'])
@login_required
def get_overdue_loans():
    """Get overdue loans from core banking system."""
    try:
        # Statically define the module ID
        module_id = 1  # Module ID for loan data

        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 400

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    expected_columns = expected.columns
                    actual_columns = actual.columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict
                    }
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Mapping Data: {mapping}")
        except Exception as e:
            return jsonify({'error': f'Error retrieving mapping data: {str(e)}'}), 500

        # Build dynamic query
        def build_dynamic_query(mapping):
            try:
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})
                m = mapping.get("Members", {})
        
                # Ensure that the necessary columns are present in the mapping
                required_ll_columns = ["LoanID", "LedgerID", "OutstandingBalance", "ArrearsAmount", "ArrearsDays"]
                required_ld_columns = ["LoanAppID", "LoanStatus"]
                required_la_columns = ["LoanAppID", "LoanNo", "LoanAmount", "MemberID"]
                required_m_columns = ["MemberID", "FirstName", "LastName"]
        
                if not all(column in ll.get("columns", []) for column in required_ll_columns):
                    raise KeyError(f"Missing columns in LoanLedgerEntries mapping: {required_ll_columns}")
        
                if not all(column in ld.get("columns", []) for column in required_ld_columns):
                    raise KeyError(f"Missing columns in LoanDisbursements mapping: {required_ld_columns}")
        
                if not all(column in la.get("columns", []) for column in required_la_columns):
                    raise KeyError(f"Missing columns in LoanApplications mapping: {required_la_columns}")
        
                if not all(column in m.get("columns", []) for column in required_m_columns):
                    raise KeyError(f"Missing columns in Members mapping: {required_m_columns}")
        
                query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    l.{ll["columns"]["ArrearsAmount"]} AS ArrearsAmount,
                    l.{ll["columns"]["ArrearsDays"]} AS ArrearsDays,
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus,
                    CONCAT(m.{m["columns"]["FirstName"]}, ' ', m.{m["columns"]["LastName"]}) AS CustomerName
                FROM {ll["actual_table_name"]} l
                JOIN (
                    SELECT {ll["columns"]["LoanID"]} AS LoanID,
                        MAX({ll["columns"]["LedgerID"]}) AS latest_id
                    FROM {ll["actual_table_name"]}
                    GROUP BY {ll["columns"]["LoanID"]}
                ) latest ON l.{ll["columns"]["LoanID"]} = latest.LoanID AND l.{ll["columns"]["LedgerID"]} = latest.latest_id
                JOIN {la["actual_table_name"]} la ON l.{ll["columns"]["LoanID"]} = la.{la["columns"]["LoanAppID"]}
                JOIN {ld["actual_table_name"]} ld ON la.{la["columns"]["LoanAppID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {m["actual_table_name"]} m ON la.{la["columns"]["MemberID"]} = m.{m["columns"]["MemberID"]}
                WHERE ld.{ld["columns"]["LoanStatus"]} = 'Active'
                AND l.{ll["columns"]["ArrearsDays"]} > 0
                ORDER BY l.{ll["columns"]["LoanID"]}
                """
                current_app.logger.info(f"Built query: {query}")
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        try:
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            loan_data = cursor.fetchall()
            current_app.logger.info(f"Fetched Loan Data: {loan_data}")
        except Exception as e:
            return jsonify({'error': f'Error executing query: {str(e)}'}), 500

        # Format dates and ensure list format
        formatted_data = []
        for loan in loan_data:
            loan_dict = dict(loan)
            formatted_data.append({
                'loan_id': loan_dict['LoanID'],
                'loan_no': loan_dict['LoanNo'],
                'customer_name': loan_dict['CustomerName'],
                'outstanding_balance': float(loan_dict['OutstandingBalance']),
                'arrears_amount': float(loan_dict['ArrearsAmount']),
                'arrears_days': int(loan_dict['ArrearsDays'])
            })

        return jsonify({'data': formatted_data})

    except Exception as e:
        current_app.logger.error(f"Error fetching overdue loans: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@api_bp.route('/collection-schedules/<int:schedule_id>/progress', methods=['GET'])
@login_required
def get_progress_updates(schedule_id):
    try:
        # Get progress updates using the service
        updates = ProgressUpdateService.get_progress_updates(schedule_id)
        
        # Convert to list of dictionaries for JSON serialization
        updates_list = []
        if updates is not None:  # Check if query result is not None
            for update in updates:
                updates_list.append({
                    'id': update.id,
                    'status': update.status,
                    'amount': float(update.amount) if update.amount is not None else None,
                    'collection_method': update.collection_method,
                    'notes': update.notes,
                    'attachment_url': update.attachment_url,  # Changed from 'attachment' to 'attachment_url'
                    'created_at': update.created_at.isoformat()
                })
        
        return jsonify({'updates': updates_list})
        
    except Exception as e:
        current_app.logger.error(f"Error getting progress updates: {str(e)}")
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
