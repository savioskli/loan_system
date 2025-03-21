from flask import Blueprint, jsonify, render_template, request, current_app
from flask_login import login_required, current_user
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from extensions import db
from models import Client, Loan
from models.correspondence import Correspondence
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
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        account_no = request.args.get('account_no')
        client_name = request.args.get('client_name')
        corr_type = request.args.get('type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Base query
        query = Correspondence.query
        
        # Apply filters
        if account_no:
            query = query.filter(Correspondence.account_no.ilike(f'%{account_no}%'))
        if client_name:
            query = query.filter(Correspondence.client_name.ilike(f'%{client_name}%'))
        if corr_type:
            query = query.filter(Correspondence.type == corr_type)
        if status:
            query = query.filter(Correspondence.status == status)
        if start_date:
            query = query.filter(Correspondence.created_at >= start_date)
        if end_date:
            query = query.filter(Correspondence.created_at <= end_date)
        
        # Get total count for pagination
        total = query.count()
        
        # Get correspondence for current page
        correspondence = query.order_by(Correspondence.created_at.desc())\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        # Prepare pagination info
        total_pages = (total + per_page - 1) // per_page
        pages = []
        for p in range(max(1, page - 2), min(total_pages + 1, page + 3)):
            pages.append({
                'number': p,
                'current': p == page
            })
        
        pagination = {
            'current_page': page,
            'total_pages': total_pages,
            'total': total,
            'start': (page - 1) * per_page + 1 if total > 0 else 0,
            'end': min(page * per_page, total),
            'pages': pages
        }
        
        # Convert correspondence to dict
        correspondence_data = [c.to_dict() for c in correspondence]
        
        return jsonify({
            'correspondence': correspondence_data,
            'pagination': pagination
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
