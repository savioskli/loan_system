from flask import Blueprint, jsonify, render_template, request, current_app
from flask_login import login_required, current_user
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from extensions import db
from models import Client, Loan
from models.correspondence import Correspondence
from models.sms_gateway import SmsGatewayConfig
from models.email_config import EmailConfig
from services.correspondence_service import CorrespondenceService
import csv
from io import StringIO
from flask import Response
from datetime import timedelta

correspondence_bp = Blueprint('correspondence', __name__, url_prefix='/correspondence')

@correspondence_bp.route('/capture-correspondence')
@login_required
def capture_correspondence():
    return render_template('user/capture_correspondence.html')

@correspondence_bp.route('/correspondence-history')
@login_required
def correspondence_history():
    """View correspondence history."""
    try:
        # Get query parameters with defaults
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        date_range = request.args.get('date_range', 'all')
        comm_type = request.args.get('comm_type', 'all')
        status = request.args.get('status', 'all')
        search = request.args.get('search', '')
        
        # Base query
        query = Correspondence.query
        
        # Apply filters
        if date_range != 'all':
            today = datetime.utcnow().date()
            if date_range == 'today':
                query = query.filter(db.func.date(Correspondence.created_at) == today)
            elif date_range == 'yesterday':
                query = query.filter(db.func.date(Correspondence.created_at) == today - timedelta(days=1))
            elif date_range == 'last_7_days':
                query = query.filter(Correspondence.created_at >= today - timedelta(days=7))
            elif date_range == 'last_30_days':
                query = query.filter(Correspondence.created_at >= today - timedelta(days=30))
            elif date_range == 'this_month':
                query = query.filter(db.func.extract('month', Correspondence.created_at) == today.month,
                                  db.func.extract('year', Correspondence.created_at) == today.year)
            elif date_range == 'last_month':
                last_month = today.replace(day=1) - timedelta(days=1)
                query = query.filter(db.func.extract('month', Correspondence.created_at) == last_month.month,
                                  db.func.extract('year', Correspondence.created_at) == last_month.year)
        
        # Apply type filter
        if comm_type != 'all':
            query = query.filter(Correspondence.type == comm_type)
        
        # Apply status filter
        if status != 'all':
            query = query.filter(Correspondence.status == status)
        
        # Apply search filter
        if search:
            search_term = f'%{search}%'
            query = query.filter(db.or_(
                Correspondence.account_no.ilike(search_term),
                Correspondence.client_name.ilike(search_term),
                Correspondence.message.ilike(search_term)
            ))
        
        # Get total count for pagination
        total = query.count()
        
        # Get correspondence for current page
        correspondence = query.order_by(Correspondence.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # Prepare pagination info
        total_pages = (total + per_page - 1) // per_page
        pages = []
        for p in range(max(1, page - 2), min(total_pages + 1, page + 3)):
            pages.append({
                'number': p,
                'current': p == page
            })
        
        return render_template(
            'user/correspondence_history.html',
            correspondence=correspondence.items if correspondence else [],
            pagination={
                'current_page': page,
                'total_pages': total_pages,
                'total': total,
                'start': (page - 1) * per_page + 1 if total > 0 else 0,
                'end': min(page * per_page, total),
                'pages': pages
            },
            filters={
                'date_range': date_range,
                'comm_type': comm_type,
                'status': status,
                'search': search
            }
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in correspondence history: {str(e)}")
        return render_template(
            'user/correspondence_history.html',
            correspondence=[],
            pagination={
                'current_page': 1,
                'total_pages': 1,
                'total': 0,
                'start': 0,
                'end': 0,
                'pages': []
            },
            filters={},
            error="An error occurred while loading correspondence history. Please try again."
        )

@correspondence_bp.route('/api/correspondence', methods=['POST'])
@login_required
def create_correspondence():
    try:
        # Validate required fields
        required_fields = ['client_id', 'type', 'message']
        for field in required_fields:
            if field not in request.form:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get form data
        client_id = request.form.get('client_id')
        corr_type = request.form.get('type')
        message = request.form.get('message')
        
        # Get loan details
        loan = Loan.query.filter_by(client_id=client_id).first()
        if not loan:
            return jsonify({'error': 'No loan found for this client'}), 404
            
        # Handle file upload if present
        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                try:
                    filename = secure_filename(file.filename)
                    # Create uploads directory if it doesn't exist
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'correspondence')
                    os.makedirs(upload_dir, exist_ok=True)
                    # Save file
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    attachment_path = f'/static/uploads/correspondence/{filename}'
                except Exception as e:
                    current_app.logger.error(f"File upload error: {str(e)}")
                    return jsonify({'error': 'Error uploading file'}), 500
        
        # Create correspondence record
        try:
            correspondence = Correspondence(
                account_no=loan.account_no,
                client_name=loan.client.name,
                type=corr_type,
                message=message,
                status='Sent',
                sent_by=current_user.username,
                recipient=request.form.get('recipient'),
                delivery_status='Delivered',
                delivery_time=datetime.utcnow(),
                call_duration=request.form.get('call_duration'),
                call_outcome=request.form.get('call_outcome'),
                location=request.form.get('location'),
                visit_purpose=request.form.get('visit_purpose'),
                visit_outcome=request.form.get('visit_outcome'),
                staff_id=current_user.id,
                loan_id=loan.id,
                attachment_path=attachment_path
            )
            
            db.session.add(correspondence)
            db.session.commit()
            
            return jsonify({
                'message': 'Correspondence created successfully',
                'id': correspondence.id
            }), 201
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return jsonify({'error': 'Error saving correspondence to database'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@correspondence_bp.route('/api/send-email-reminder', methods=['POST'])  # Full URL: /correspondence/api/send-email-reminder
@login_required
def send_email_reminder():
    """
    Send an email reminder to a client.
    
    Expected JSON payload:
    {
        "client_id": int,
        "loan_id": int,
        "email": str
    }
    """
    # Main try block for the entire function
    try:
        # Try to print the raw request data for debugging
        try:
            print(f"[DEBUG] Raw request data: {request.data}")
        except Exception as e:
            print(f"[ERROR] Error accessing request data: {str(e)}")
        
        # Check if email is configured
        email_config = CorrespondenceService.is_email_configured()
        if not email_config:
            print(f"[ERROR] Email service is not configured")
            return jsonify({
                'success': False,
                'message': 'Email service is not configured'
            }), 400
        else:
            print(f"[INFO] Email configuration found and valid")
            
        # Validate request data
        try:
            data = request.json
            print(f"[DEBUG] Parsed JSON data: {data}")
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON data: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Invalid JSON data: {str(e)}'
            }), 400
            
        if not data:
            print(f"[ERROR] Empty request data")
            return jsonify({
                'success': False,
                'message': 'Empty request data'
            }), 400
            
        # Check if we're using the old format (client_id and loan_id) or new format (direct client details)
        old_format = 'client_id' in data and 'loan_id' in data
        new_format = all(field in data for field in ['email', 'client_name', 'account_no', 'loan_amount', 'outstanding_balance'])
        
        # Get email which is required in both formats
        email = data.get('email')
        if not email:
            print(f"[ERROR] Missing required field: email")
            return jsonify({
                'success': False,
                'message': 'Missing required field: email'
            }), 400
            
        # Handle old format (client_id and loan_id)
        if old_format and not new_format:
            print(f"[INFO] Using old format with client_id and loan_id")
            client_id = data.get('client_id')
            loan_id = data.get('loan_id')
            
            if not client_id or not loan_id:
                print(f"[ERROR] Missing required fields: client_id or loan_id")
                return jsonify({
                    'success': False,
                    'message': 'Missing required fields: client_id and loan_id are required'
                }), 400
                
            # Get client and loan details from database
            try:
                client = Client.query.get(client_id)
                if not client:
                    print(f"[ERROR] Client with ID {client_id} not found")
                    return jsonify({
                        'success': False,
                        'message': f'Client with ID {client_id} not found'
                    }), 404
                
                loan = Loan.query.get(loan_id)
                if not loan:
                    print(f"[ERROR] Loan with ID {loan_id} not found")
                    return jsonify({
                        'success': False,
                        'message': f'Loan with ID {loan_id} not found'
                    }), 404
                    
                # Set variables from database objects
                client_name = client.full_name
                account_no = loan.account_no
                try:
                    loan_amount = float(loan.amount)
                except (ValueError, TypeError) as e:
                    print(f"[ERROR] Invalid loan amount value: {loan.amount}. Error: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': f'Invalid loan amount value: {str(e)}'
                    }), 400
                    
                try:
                    outstanding_balance = float(loan.outstanding_balance)
                except (ValueError, TypeError) as e:
                    print(f"[ERROR] Invalid outstanding balance value: {loan.outstanding_balance}. Error: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': f'Invalid outstanding balance value: {str(e)}'
                    }), 400
                    
            except Exception as e:
                print(f"[ERROR] Database error when fetching client/loan: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Database error: {str(e)}'
                }), 500
                
        # Handle new format (direct client details)
        elif new_format:
            print(f"[INFO] Using new format with direct client details")
            client_name = data.get('client_name')
            account_no = data.get('account_no')
            
            try:
                loan_amount = float(data.get('loan_amount'))
                outstanding_balance = float(data.get('outstanding_balance'))
            except (ValueError, TypeError) as e:
                print(f"[ERROR] Invalid numeric value in request data: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Invalid numeric value: {str(e)}'
                }), 400
                
        # Neither format is valid
        else:
            print(f"[ERROR] Invalid request format. Must provide either client_id and loan_id, or all client details directly")
            return jsonify({
                'success': False,
                'message': 'Invalid request format. Must provide either client_id and loan_id, or all client details directly'
            }), 400
        
        print(f"[INFO] Processing email reminder request for client={client_name}, account={account_no}, email={email}")
        
        # Validate email format
        if not email or '@' not in email:
            print(f"[ERROR] Invalid email format: {email}")
            return jsonify({
                'success': False,
                'message': f'Invalid email format: {email}'
            }), 400
            
        # Log the email sending attempt - using data directly from the request
        current_app.logger.info(f"Sending email reminder to {email} for client {client_name}")
        print(f"[INFO] Preparing to send email reminder to {email} for client {client_name}")
        
        # Prepare data for the email reminder
        try:
            # Set due date to 7 days from now if not provided
            due_date = data.get('due_date')
            if not due_date:
                due_date = datetime.utcnow() + timedelta(days=7)
                print(f"[INFO] Using default due date: {due_date}")
            else:
                print(f"[INFO] Using provided due date: {due_date}")
            
            # As per system requirements, use OutstandingBalance when InstallmentAmount is not available
            try:
                outstanding_balance = float(outstanding_balance)
                print(f"[INFO] Using outstanding balance: {outstanding_balance}")
            except (ValueError, TypeError) as e:
                print(f"[ERROR] Invalid outstanding balance value: {outstanding_balance}. Error: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Invalid outstanding balance value: {str(e)}'
                }), 400
                
            try:
                loan_amount = float(loan_amount)
                print(f"[INFO] Using loan amount: {loan_amount}")
            except (ValueError, TypeError) as e:
                print(f"[ERROR] Invalid loan amount value: {loan_amount}. Error: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Invalid loan amount value: {str(e)}'
                }), 400
        except Exception as e:
            print(f"[ERROR] Error preparing email data: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error preparing email data: {str(e)}'
            }), 500
        
        # Validate staff information
        if not current_user or not current_user.id:
            print(f"[ERROR] Invalid current user information")
            return jsonify({
                'success': False,
                'message': 'Invalid staff information'
            }), 400
        
        print(f"[INFO] Sending email with the following data: To: {email}, Client: {client_name}, Account: {account_no}, Loan Amount: {loan_amount}, Outstanding: {outstanding_balance}, Due Date: {due_date}, Staff: {current_user.username} (ID: {current_user.id})")
        
        # Send email reminder
        try:
            result = CorrespondenceService.send_payment_reminder_email(
                to=email,
                client_name=client_name,
                account_no=account_no,
                loan_amount=loan_amount,
                outstanding_balance=outstanding_balance,
                due_date=due_date,
                staff_id=current_user.id,
                sent_by=current_user.username
            )
            
            print(f"[DEBUG] Email service result: {result}")
            
            if result['success']:
                current_app.logger.info(f"Email reminder sent successfully to {email}")
                print(f"[SUCCESS] Email reminder sent successfully to {email}")
                return jsonify({
                    'success': True,
                    'message': 'Email reminder sent successfully',
                    'correspondence_id': result.get('correspondence_id')
                }), 200
            else:
                error_message = result.get('message', 'Unknown error')
                current_app.logger.error(f"Failed to send email reminder: {error_message}")
                print(f"[ERROR] Failed to send email reminder: {error_message}")
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 500
        except Exception as e:
            print(f"[ERROR] Exception while calling correspondence service: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Exception while sending email: {str(e)}'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error sending email reminder: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@correspondence_bp.route('/api/batch-send-email-reminders', methods=['POST'])
@login_required
def batch_send_email_reminders():
    """
    Send email reminders to multiple clients in a single batch operation.
    This is more efficient than sending emails one by one as it reuses a single SMTP connection.
    
    Expected JSON payload:
    {
        "reminders": [
            {
                "client_id": int,
                "loan_id": int,
                "email": str
            },
            ...
        ]
    }
    """
    # Main try block for the entire function
    try:
        # Try to print the raw request data for debugging
        try:
            print(f"[DEBUG] Raw batch request data: {request.data}")
        except Exception as e:
            print(f"[ERROR] Error accessing batch request data: {str(e)}")
        
        # Check if email is configured
        email_config = CorrespondenceService.is_email_configured()
        if not email_config:
            print(f"[ERROR] Email service is not configured")
            return jsonify({
                'success': False,
                'message': 'Email service is not configured'
            }), 400
        else:
            print(f"[INFO] Email configuration found and valid")
            
        # Validate request data
        try:
            data = request.json
            print(f"[DEBUG] Parsed batch JSON data: {data}")
        except Exception as e:
            print(f"[ERROR] Failed to parse batch JSON data: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Invalid JSON data: {str(e)}'
            }), 400
            
        if not data:
            print(f"[ERROR] Empty batch request data")
            return jsonify({
                'success': False,
                'message': 'Empty request data'
            }), 400
        
        # Check for reminders array
        reminders = data.get('reminders', [])
        if not reminders or not isinstance(reminders, list):
            print(f"[ERROR] Missing or invalid reminders array")
            return jsonify({
                'success': False,
                'message': 'Missing or invalid reminders array'
            }), 400
        
        print(f"[INFO] Processing batch email reminders for {len(reminders)} recipients")
        
        # Prepare data for batch email sending
        email_data = []
        invalid_reminders = []
        
        for i, reminder in enumerate(reminders):
            try:
                # Check if we're using the old format (client_id and loan_id) or new format (direct client details)
                old_format = 'client_id' in reminder and 'loan_id' in reminder
                new_format = all(field in reminder for field in ['email', 'client_name', 'account_no', 'loan_amount', 'outstanding_balance'])
                
                # Get email which is required in both formats
                email = reminder.get('email')
                if not email:
                    invalid_reminders.append({
                        'index': i,
                        'error': 'Missing required field: email',
                        'data': reminder
                    })
                    continue
                    
                # Handle old format (client_id and loan_id)
                if old_format and not new_format:
                    print(f"[INFO] Using old format with client_id and loan_id for reminder {i}")
                    client_id = reminder.get('client_id')
                    loan_id = reminder.get('loan_id')
                    
                    if not client_id or not loan_id:
                        invalid_reminders.append({
                            'index': i,
                            'error': 'Missing required fields: client_id or loan_id',
                            'data': reminder
                        })
                        continue
                    
                    # Get client and loan details from database
                    try:
                        client = Client.query.get(client_id)
                        if not client:
                            invalid_reminders.append({
                                'index': i,
                                'error': f'Client with ID {client_id} not found',
                                'data': reminder
                            })
                            continue
                        
                        loan = Loan.query.get(loan_id)
                        if not loan:
                            invalid_reminders.append({
                                'index': i,
                                'error': f'Loan with ID {loan_id} not found',
                                'data': reminder
                            })
                            continue
                            
                        # Set variables from database objects
                        client_name = client.full_name
                        account_no = loan.account_no
                        
                        try:
                            loan_amount = float(loan.amount)
                        except (ValueError, TypeError):
                            invalid_reminders.append({
                                'index': i,
                                'error': f'Invalid loan amount value: {loan.amount}',
                                'data': reminder
                            })
                            continue
                            
                        try:
                            outstanding_balance = float(loan.outstanding_balance)
                        except (ValueError, TypeError):
                            invalid_reminders.append({
                                'index': i,
                                'error': f'Invalid outstanding balance value: {loan.outstanding_balance}',
                                'data': reminder
                            })
                            continue
                            
                    except Exception as e:
                        invalid_reminders.append({
                            'index': i,
                            'error': f'Database error: {str(e)}',
                            'data': reminder
                        })
                        continue
                        
                # Handle new format (direct client details)
                elif new_format:
                    print(f"[INFO] Using new format with direct client details for reminder {i}")
                    client_name = reminder.get('client_name')
                    account_no = reminder.get('account_no')
                    
                    try:
                        loan_amount = float(reminder.get('loan_amount'))
                        outstanding_balance = float(reminder.get('outstanding_balance'))
                    except (ValueError, TypeError) as e:
                        invalid_reminders.append({
                            'index': i,
                            'error': f'Invalid numeric value in request data: {str(e)}',
                            'data': reminder
                        })
                        continue
                        
                # Neither format is valid
                else:
                    invalid_reminders.append({
                        'index': i,
                        'error': 'Invalid request format. Must provide either client_id and loan_id, or all client details directly',
                        'data': reminder
                    })
                    continue
                
                # Validate email format
                if not email or '@' not in email:
                    invalid_reminders.append({
                        'index': i,
                        'error': f'Invalid email format: {email}',
                        'data': reminder
                    })
                    continue
                
                # Set due date to 7 days from now if not provided
                due_date = reminder.get('due_date')
                if not due_date:
                    due_date = datetime.utcnow() + timedelta(days=7)
                
                # Add to valid email data
                email_data.append({
                    'to': email,
                    'client_name': client_name,
                    'account_no': account_no,
                    'loan_amount': loan_amount,
                    'outstanding_balance': outstanding_balance,  # Using outstanding balance as per system requirements
                    'due_date': due_date
                })
                
            except Exception as e:
                invalid_reminders.append({
                    'index': i,
                    'error': f'Error processing reminder: {str(e)}',
                    'data': reminder
                })
        
        # Check if we have any valid reminders to send
        if not email_data:
            print(f"[ERROR] No valid reminders to send after validation")
            return jsonify({
                'success': False,
                'message': 'No valid reminders to send after validation',
                'invalid_reminders': invalid_reminders
            }), 400
        
        # Validate staff information
        if not current_user or not current_user.id:
            print(f"[ERROR] Invalid current user information")
            return jsonify({
                'success': False,
                'message': 'Invalid staff information'
            }), 400
        
        print(f"[INFO] Sending batch emails to {len(email_data)} recipients")
        
        # Send batch email reminders
        try:
            result = CorrespondenceService.batch_send_payment_reminder_emails(
                reminders=email_data,
                staff_id=current_user.id,
                sent_by=current_user.username
            )
            
            print(f"[DEBUG] Batch email service result: {result}")
            
            # Prepare response with both successes and failures
            response = {
                'success': result['success'],
                'message': result['message'],
                'total': result['total'],
                'sent': result['sent'],
                'failed': result['failed'],
                'invalid_reminders': invalid_reminders
            }
            
            if result['sent'] > 0:
                current_app.logger.info(f"Batch email reminders sent successfully to {result['sent']} recipients")
                print(f"[SUCCESS] Batch email reminders sent successfully to {result['sent']} recipients")
                return jsonify(response), 200
            else:
                error_message = result.get('message', 'Unknown error')
                current_app.logger.error(f"Failed to send any batch email reminders: {error_message}")
                print(f"[ERROR] Failed to send any batch email reminders: {error_message}")
                return jsonify(response), 500
                
        except Exception as e:
            print(f"[ERROR] Exception while calling batch correspondence service: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Exception while sending batch emails: {str(e)}',
                'invalid_reminders': invalid_reminders
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error sending batch email reminders: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@correspondence_bp.route('/api/clients')
@login_required
def get_clients():
    """Get all clients."""
    try:
        clients = Client.query.all()
        return jsonify([{
            'id': client.id,
            'name': client.full_name  # Using full_name property instead of name attribute
        } for client in clients])
    except Exception as e:
        current_app.logger.error(f"Error getting clients: {str(e)}")
        return jsonify({'error': 'Error getting clients'}), 500

@correspondence_bp.route('/api/client/<int:client_id>/loans')
@login_required
def get_client_loans(client_id):
    loans = Loan.query.filter_by(client_id=client_id).all()
    return jsonify([{
        'id': loan.id,
        'account_no': loan.account_no,
        'amount': float(loan.amount),
        'status': loan.status,
        'classification': loan.classification,
        'days_in_arrears': loan.days_in_arrears,
        'outstanding_balance': float(loan.outstanding_balance)
    } for loan in loans])

@correspondence_bp.route('/api/correspondence')
@login_required
def get_correspondence():
    """Get correspondence data with filters."""
    try:
        current_app.logger.info("Getting correspondence data")
        
        # Get query parameters
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(50, max(10, int(request.args.get('per_page', 10))))
        search = request.args.get('search', '').strip()
        
        # Base query
        query = Correspondence.query
        
        # Apply search filter if provided
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Correspondence.client_name.ilike(search_term),
                    Correspondence.account_no.ilike(search_term),
                    Correspondence.message.ilike(search_term),
                    Correspondence.type.ilike(search_term),
                    Correspondence.status.ilike(search_term)
                )
            )
        
        # Always order by created_at in descending order (newest first)
        query = query.order_by(Correspondence.created_at.desc())
        
        # Get total count for pagination
        total = query.count()
        total_pages = max(1, (total + per_page - 1) // per_page)
        
        # Ensure page is within valid range
        page = min(page, total_pages)
        
        # Get correspondence for current page
        correspondence = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert correspondence to dict and format dates
        correspondence_data = []
        for c in correspondence:
            data = c.to_dict()
            if isinstance(data.get('created_at'), datetime):
                data['created_at'] = data['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            correspondence_data.append(data)
        
        return jsonify({
            'correspondence': correspondence_data,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total': total,
                'per_page': per_page
            }
        })
        
    except Exception as e:
        error_msg = f"Error getting correspondence data: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({'error': str(e)}), 500

@correspondence_bp.route('/api/correspondence/<int:id>', endpoint='get_correspondence_details')
@login_required
def get_correspondence_details(id):
    """Get correspondence details by ID."""
    try:
        correspondence = Correspondence.query.get_or_404(id)
        return jsonify({
            'id': correspondence.id,
            'account_no': correspondence.account_no,
            'client_name': correspondence.client_name,
            'type': correspondence.type,
            'message': correspondence.message,
            'status': correspondence.status,
            'sent_by': correspondence.sent_by,
            'created_at': correspondence.created_at.isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error getting correspondence details: {str(e)}")
        return jsonify({'error': 'Failed to get correspondence details'}), 500

@correspondence_bp.route('/api/correspondence/export', endpoint='export_correspondence')
@login_required
def export_correspondence():
    """Export correspondence to CSV."""
    try:
        # Get filter parameters
        date_range = request.args.get('date_range', 'all')
        comm_type = request.args.get('comm_type', 'all')
        status = request.args.get('status', 'all')
        search = request.args.get('search', '')
        
        # Base query
        query = Correspondence.query
        
        # Apply filters (same as in correspondence_history)
        if date_range != 'all':
            today = datetime.utcnow().date()
            if date_range == 'today':
                query = query.filter(db.func.date(Correspondence.created_at) == today)
            elif date_range == 'yesterday':
                query = query.filter(db.func.date(Correspondence.created_at) == today - timedelta(days=1))
            elif date_range == 'last_7_days':
                query = query.filter(Correspondence.created_at >= today - timedelta(days=7))
            elif date_range == 'last_30_days':
                query = query.filter(Correspondence.created_at >= today - timedelta(days=30))
            elif date_range == 'this_month':
                query = query.filter(db.func.extract('month', Correspondence.created_at) == today.month,
                                  db.func.extract('year', Correspondence.created_at) == today.year)
            elif date_range == 'last_month':
                last_month = today.replace(day=1) - timedelta(days=1)
                query = query.filter(db.func.extract('month', Correspondence.created_at) == last_month.month,
                                  db.func.extract('year', Correspondence.created_at) == last_month.year)
        
        if comm_type != 'all':
            query = query.filter(Correspondence.type == comm_type)
        
        if status != 'all':
            query = query.filter(Correspondence.status == status)
        
        if search:
            search_term = f'%{search}%'
            query = query.filter(db.or_(
                Correspondence.account_no.ilike(search_term),
                Correspondence.client_name.ilike(search_term),
                Correspondence.message.ilike(search_term)
            ))
        
        # Get all correspondence
        correspondence = query.order_by(Correspondence.created_at.desc()).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date & Time', 'Account No', 'Client Name', 'Type', 'Message', 'Status', 'Sent By'])
        
        # Write data
        for comm in correspondence:
            writer.writerow([
                comm.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                comm.account_no,
                comm.client_name,
                comm.type,
                comm.message,
                comm.status,
                comm.sent_by
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=correspondence_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exporting correspondence: {str(e)}")
        return jsonify({'error': 'Failed to export correspondence'}), 500

@correspondence_bp.route('/api/send-sms', methods=['POST'])
@login_required
def send_sms():
    """Send an SMS message using the configured SMS gateway."""
    try:
        # Validate required fields
        required_fields = ['recipient', 'message', 'account_no', 'client_name']
        for field in required_fields:
            if field not in request.json:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Get request data
        recipient = request.json.get('recipient')
        message = request.json.get('message')
        account_no = request.json.get('account_no')
        client_name = request.json.get('client_name')
        
        # Send SMS using the correspondence service
        # We'll use the single configured SMS provider from the database
        result = CorrespondenceService.send_sms(
            to=recipient,
            message=message,
            account_no=account_no,
            client_name=client_name,
            staff_id=current_user.id,
            sent_by=current_user.username,
            provider=None  # Use the default provider configured in the database
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error sending SMS: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error sending SMS: {str(e)}",
            'correspondence_id': None
        }), 500

@correspondence_bp.route('/api/sms-providers', methods=['GET'])
@login_required
def get_sms_providers():
    """Get available SMS providers and the active provider."""
    try:
        active_provider = CorrespondenceService.get_active_sms_provider()
        available_providers = CorrespondenceService.get_available_sms_providers()
        
        return jsonify({
            'active_provider': active_provider,
            'available_providers': available_providers
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SMS providers: {str(e)}")
        return jsonify({'error': f"Error getting SMS providers: {str(e)}"}), 500

@correspondence_bp.route('/api/send-bulk-sms', methods=['POST'])
@login_required
def send_bulk_sms():
    """Send SMS messages to multiple recipients."""
    try:
        # Log the incoming request for debugging
        current_app.logger.info(f"Received bulk SMS request: {request.data}")
        
        # Validate request data
        if not request.json or not isinstance(request.json, list):
            current_app.logger.error(f"Invalid request format: {request.data}")
            return jsonify({'success': False, 'error': 'Invalid request format. Expected a list of SMS messages.'}), 400
        
        messages = request.json
        current_app.logger.info(f"Processing {len(messages)} SMS messages")
        results = []
        
        # Process each message in the list
        for msg in messages:
            # Validate required fields for each message
            required_fields = ['recipient', 'message', 'account_no', 'client_name']
            for field in required_fields:
                if field not in msg:
                    current_app.logger.error(f"Missing required field: {field} in message: {msg}")
                    return jsonify({'success': False, 'error': f'Missing required field: {field} in one of the messages'}), 400
                    
            # Validate phone number format
            if not msg['recipient'] or len(msg['recipient'].strip()) < 10:
                current_app.logger.error(f"Invalid phone number format: {msg['recipient']} in message: {msg}")
                return jsonify({'success': False, 'error': f'Invalid phone number format: {msg["recipient"]}'}), 400
            
            # Send SMS using the correspondence service
            result = CorrespondenceService.send_sms(
                to=msg['recipient'],
                message=msg['message'],
                account_no=msg['account_no'],
                client_name=msg['client_name'],
                staff_id=current_user.id,
                sent_by=current_user.username
            )
            
            results.append(result)
        
        # Return the results
        return jsonify({
            'success': all(result['success'] for result in results),
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Error sending bulk SMS: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error sending bulk SMS: {str(e)}",
            'results': []
        }), 500
