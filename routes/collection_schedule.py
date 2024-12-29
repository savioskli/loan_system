from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from services.collection_schedule_service import CollectionScheduleService
from models.staff import Staff
from models.loan import Loan
from datetime import datetime
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
    staff = Staff.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'branch': s.branch
    } for s in staff]), 200

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