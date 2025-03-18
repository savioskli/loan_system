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
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from models.letter_template import LetterTemplate  # Import LetterTemplate model
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
                    COALESCE(l.LoanAmount, 0),
                    COALESCE(lle.OutstandingBalance, 0),
                    COALESCE(l.RepaymentPeriod, 0)
                )) AS LoanInfo,
                GROUP_CONCAT(DISTINCT 
                    CASE 
                        WHEN g.GuarantorID IS NOT NULL 
                        THEN CONCAT_WS(':', 
                            COALESCE(g.GuarantorID, ''),
                            COALESCE(g.GuarantorMemberID, ''),
                            COALESCE(gm.FullName, ''),
                            COALESCE(g.GuaranteedAmount, 0),
                            COALESCE(g.Status, ''),
                            COALESCE(l.LoanAppID, '')
                        )
                    END
                ) AS GuarantorInfo
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
# Process loan information
            if member['LoanInfo']:
                loan_info_list = member['LoanInfo'].split(',')
                for loan_info in loan_info_list:
                    try:
                        loan_id, loan_no, loan_amount, outstanding, repayment_period = loan_info.split(':')
                        if loan_id and loan_no:  # Only add if we have valid loan info
                            loans.append({
                                'LoanAppID': loan_id,
                                'LoanNo': loan_no,
                                'LoanAmount': float(loan_amount) if loan_amount else 0,
                                'OutstandingBalance': float(outstanding) if outstanding else 0,
                                'RepaymentPeriod': int(repayment_period) if repayment_period else 0
                            })
                    except ValueError as e:
                        current_app.logger.error(f"Error parsing loan info: {loan_info}, Error: {str(e)}")
                        continue
            
            # Process guarantor information
            if member['GuarantorInfo'] and member['GuarantorInfo'] != 'NULL':
                current_app.logger.info(f"Raw GuarantorInfo: {member['GuarantorInfo']}")
                guarantor_info_list = [g for g in member['GuarantorInfo'].split(',') if g]  # Filter out empty strings
                for guarantor_info in guarantor_info_list:
                    try:
                        fields = guarantor_info.split(':')
                        if len(fields) == 6:  # Only process if we have all fields
                            guarantor_id, member_id, guarantor_name, guaranteed_amount, status, loan_app_id = fields
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

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
