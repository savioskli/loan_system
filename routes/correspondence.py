from flask import Blueprint, jsonify, render_template, request, current_app
from flask_login import login_required, current_user
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from extensions import db
from models import Client, Loan
from models.correspondence import Correspondence
from models.sms_gateway import SmsGatewayConfig
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

@correspondence_bp.route('/api/clients')
@login_required
def get_clients():
    """Get all clients."""
    try:
        clients = Client.query.all()
        return jsonify([{
            'id': client.id,
            'name': client.name
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
