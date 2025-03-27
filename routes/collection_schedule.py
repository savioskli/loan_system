from flask import Blueprint, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from services.collection_schedule_service import CollectionScheduleService
from models.staff import Staff
from models.role import Role
from models.loan import Loan
from models.payment_record import PaymentRecord
from extensions import db
from datetime import datetime
import os
import uuid
import traceback

collection_schedule_bp = Blueprint('collection_schedule', __name__)

@collection_schedule_bp.route('/api/collection-schedules', methods=['POST'])
@login_required
def create_collection_schedule():
    """Create a new collection schedule."""
    try:
        data = request.json
        new_schedule = CollectionScheduleService.create_schedule(data)
        current_app.logger.info(f"Created schedule {new_schedule.id}")
        return jsonify({
            'message': 'Collection schedule created successfully',
            'schedule_id': new_schedule.id
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error creating schedule: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@collection_schedule_bp.route('/api/collection-schedules', methods=['GET'])
@login_required
def get_collection_schedules():
    """Get collection schedules with filters."""
    try:
        current_app.logger.info("Starting get_collection_schedules endpoint")
        filters = {}
        
        # Only add filters if they are provided and valid
        if request.args.get('staff_id'):
            try:
                filters['staff_id'] = int(request.args.get('staff_id'))
            except ValueError:
                current_app.logger.error(f"Invalid staff_id: {request.args.get('staff_id')}")
        
        if request.args.get('loan_id'):
            try:
                filters['loan_id'] = int(request.args.get('loan_id'))
            except ValueError:
                current_app.logger.error(f"Invalid loan_id: {request.args.get('loan_id')}")
        
        if request.args.get('priority'):
            filters['priority'] = request.args.get('priority')
        
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        if request.args.get('escalation_level'):
            try:
                filters['escalation_level'] = int(request.args.get('escalation_level'))
            except ValueError:
                current_app.logger.error(f"Invalid escalation_level: {request.args.get('escalation_level')}")
        
        # Handle date filters
        if request.args.get('date_from'):
            try:
                filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
            except ValueError:
                current_app.logger.error(f"Invalid date_from format: {request.args.get('date_from')}")
        
        if request.args.get('date_to'):
            try:
                filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
            except ValueError:
                current_app.logger.error(f"Invalid date_to format: {request.args.get('date_to')}")

        current_app.logger.info(f"Getting schedules with filters: {filters}")
        
        try:
            schedules = CollectionScheduleService.get_schedules(filters)
            current_app.logger.info(f"Found {len(schedules) if schedules else 0} schedules")
            current_app.logger.debug(f"Schedule data: {schedules}")
            
            if not schedules:
                current_app.logger.warning("No schedules found")
                return jsonify([]), 200
                
            return jsonify(schedules), 200
            
        except Exception as e:
            current_app.logger.error(f"Error in get_collection_schedules service call: {str(e)}\n{traceback.format_exc()}")
            return jsonify({'error': 'Failed to retrieve collection schedules'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in get_collection_schedules endpoint: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@collection_schedule_bp.route('/api/collection-schedules/<int:schedule_id>', methods=['GET'])
@login_required
def get_collection_schedule(schedule_id):
    """Get a specific collection schedule."""
    try:
        current_app.logger.info(f"Getting schedule {schedule_id}")
        schedule = CollectionScheduleService.get_schedule(schedule_id)
        if not schedule:
            current_app.logger.warning(f"Schedule {schedule_id} not found")
            return jsonify({'error': 'Schedule not found'}), 404
            
        return jsonify({
            'id': schedule.id,
            'staff_id': schedule.staff_id,
            'staff_name': schedule.staff.full_name if schedule.staff else None,
            'loan_id': schedule.loan_id,
            'loan_account': schedule.loan.account_no if schedule.loan else None,
            'borrower_name': schedule.loan.client.full_name if schedule.loan and schedule.loan.client else None,
            'assigned_branch': schedule.assigned_branch,
            'collection_priority': schedule.collection_priority,
            'follow_up_frequency': schedule.follow_up_frequency,
            'next_follow_up_date': schedule.next_follow_up_date.isoformat() if schedule.next_follow_up_date else None,
            'preferred_collection_method': schedule.preferred_collection_method,
            'promised_payment_date': schedule.promised_payment_date.isoformat() if schedule.promised_payment_date else None,
            'attempts_made': schedule.attempts_made,
            'attempts_allowed': schedule.attempts_allowed,
            'progress_status': schedule.progress_status,
            'escalation_level': schedule.escalation_level,
            'task_description': schedule.task_description,
            'special_instructions': schedule.special_instructions
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting schedule {schedule_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@collection_schedule_bp.route('/api/collection-schedules/<int:schedule_id>', methods=['PUT'])
@login_required
def update_collection_schedule(schedule_id):
    """Update a collection schedule."""
    try:
        current_app.logger.info(f"Updating schedule {schedule_id}")
        data = request.json
        updated_schedule = CollectionScheduleService.update_schedule(schedule_id, data)
        current_app.logger.info(f"Updated schedule {schedule_id}")
        return jsonify({
            'message': 'Collection schedule updated successfully',
            'schedule_id': updated_schedule.id
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error updating schedule {schedule_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@collection_schedule_bp.route('/api/collection-schedules/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_collection_schedule(schedule_id):
    """Delete a collection schedule."""
    try:
        current_app.logger.info(f"Deleting schedule {schedule_id}")
        CollectionScheduleService.delete_schedule(schedule_id)
        current_app.logger.info(f"Deleted schedule {schedule_id}")
        return jsonify({'message': 'Collection schedule deleted successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting schedule {schedule_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@collection_schedule_bp.route('/api/collection-schedules/<int:schedule_id>/progress', methods=['PUT'])
@login_required
def update_schedule_progress(schedule_id):
    """Update the progress status of a schedule."""
    try:
        current_app.logger.info(f"Updating progress of schedule {schedule_id}")
        data = request.json
        updated_schedule = CollectionScheduleService.update_progress(
            schedule_id,
            data['status'],
            datetime.strptime(data['resolution_date'], '%Y-%m-%dT%H:%M') if data.get('resolution_date') else None
        )
        current_app.logger.info(f"Updated progress of schedule {schedule_id}")
        return jsonify({
            'message': 'Schedule progress updated successfully',
            'status': updated_schedule.progress_status
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error updating progress of schedule {schedule_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@collection_schedule_bp.route('/api/collection-schedules/<int:schedule_id>/escalate', methods=['PUT'])
@login_required
def escalate_schedule(schedule_id):
    """Escalate a collection schedule."""
    try:
        current_app.logger.info(f"Escalating schedule {schedule_id}")
        data = request.json
        updated_schedule = CollectionScheduleService.escalate_schedule(
            schedule_id,
            data['escalation_level'],
            data.get('notes')
        )
        current_app.logger.info(f"Escalated schedule {schedule_id}")
        return jsonify({
            'message': 'Schedule escalated successfully',
            'escalation_level': updated_schedule.escalation_level
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error escalating schedule {schedule_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@collection_schedule_bp.route('/api/collection-schedules/<int:schedule_id>/approve', methods=['PUT'])
@login_required
def approve_schedule(schedule_id):
    """Approve a collection schedule."""
    try:
        current_app.logger.info(f"Approving schedule {schedule_id}")
        data = request.json
        updated_schedule = CollectionScheduleService.approve_schedule(
            schedule_id,
            current_user.id,
            data.get('instructions')
        )
        current_app.logger.info(f"Approved schedule {schedule_id}")
        return jsonify({
            'message': 'Schedule approved successfully',
            'approval_date': updated_schedule.approval_date.isoformat()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error approving schedule {schedule_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

# Helper endpoints
@collection_schedule_bp.route('/api/collection-schedules/staff', methods=['GET'])
@login_required
def get_available_staff():
    """Get list of staff available for collection assignments."""
    try:
        # Get role parameter (optional)
        role_type = request.args.get('role_type', 'all')
        
        # Start with active staff query
        query = Staff.query.filter_by(is_active=True)
        
        # Filter by role if specified
        if role_type == 'officer':
            # Get staff with Collection Officer role (role_id = 4)
            query = query.filter(Staff.role_id == 4)  # Collection Officer
        elif role_type == 'supervisor':
            # Get staff with Collection Supervisor (role_id = 5) or Collections Manager (role_id = 9) role
            query = query.filter(Staff.role_id.in_([5, 9]))  # Collection Supervisor or Collections Manager
        elif role_type == 'manager':
            # Get staff with Collections Manager role (role_id = 9)
            query = query.filter(Staff.role_id == 9)  # Collections Manager
            
        # Execute query
        staff = query.all()
        
        # Return formatted staff data
        return jsonify([{
            'id': s.id,
            'name': s.full_name,
            'role': s.role.name if s.role else None,
            'role_code': s.role.code if s.role else None,
            'branch': s.branch.name if s.branch else None,
            'branch_id': s.branch_id
        } for s in staff]), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching available staff: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to retrieve staff members'}), 500

@collection_schedule_bp.route('/api/collection-schedules/loans', methods=['GET'])
@login_required
def get_available_loans():
    """Get list of loans available for collection."""
    loans = Loan.query.filter(Loan.status.in_(['ACTIVE', 'OVERDUE'])).all()
    return jsonify([{
        'id': l.id,
        'account_no': l.account_no,
        'client_name': l.client.name if l.client else None,
        'amount': str(l.amount),
        'status': l.status
    } for l in loans]), 200

@collection_schedule_bp.route('/debug/logs')
def view_logs():
    """View the last 50 lines of the Flask server log."""
    try:
        log_file = 'logs/app.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                return jsonify({'logs': lines[-50:]})
        return jsonify({'error': 'Log file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@collection_schedule_bp.route('/api/collection-schedules/<int:schedule_id>/payments', methods=['GET'])
@login_required
def get_payment_records(schedule_id):
    """Get all payment records for a collection schedule."""
    try:
        # Get the schedule
        schedule = CollectionScheduleService.get_schedule_by_id(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
            
        # Get payment records for this schedule
        payment_records = PaymentRecord.query.filter_by(schedule_id=schedule_id).order_by(PaymentRecord.payment_date.desc()).all()
        
        # Convert to dictionaries for JSON response
        payments = [record.to_dict() for record in payment_records]
        
        return jsonify(payments), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching payment records: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch payment records'}), 500

@collection_schedule_bp.route('/api/collection-schedules/<int:schedule_id>/payments', methods=['POST'])
@login_required
def create_payment_record(schedule_id):
    """Create a new payment record for a collection schedule."""
    try:
        # Get the schedule
        schedule = CollectionScheduleService.get_schedule_by_id(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Get form data
        amount = request.form.get('amount')
        payment_date = request.form.get('payment_date')
        description = request.form.get('description')
        loan_id = request.form.get('loan_id') or schedule.loan_id
        
        # Validate required fields
        if not amount or not payment_date or not description:
            return jsonify({'error': 'Amount, payment date, and description are required'}), 400
        
        # Handle file upload if present
        attachment_url = None
        if 'attachment' in request.files and request.files['attachment'].filename:
            file = request.files['attachment']
            filename = secure_filename(file.filename)
            # Generate unique filename to prevent collisions
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Ensure upload directory exists
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'payment_attachments')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Generate URL for the file
            attachment_url = url_for('static', filename=f"uploads/payment_attachments/{unique_filename}")
        
        # Create new payment record
        new_payment = PaymentRecord(
            schedule_id=schedule_id,
            loan_id=loan_id,
            amount=amount,
            payment_date=datetime.strptime(payment_date, '%Y-%m-%dT%H:%M'),
            description=description,
            attachment_url=attachment_url,
            created_by=current_user.id
        )
        
        db.session.add(new_payment)
        db.session.commit()
        
        # Check if this payment should update the schedule status
        # For example, if the payment is the full amount, mark as completed
        update_status = False
        
        # Get the loan's outstanding balance from the database
        loan = Loan.query.get(loan_id)
        if loan and loan.outstanding_balance is not None:
            # If payment amount is at least 50% of the outstanding balance, mark as completed
            if float(amount) >= (float(loan.outstanding_balance) * 0.5):
                update_status = True
        
        return jsonify({
            'message': 'Payment record created successfully', 
            'payment': new_payment.to_dict(),
            'update_status': update_status
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating payment record: {str(e)}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create payment record'}), 500