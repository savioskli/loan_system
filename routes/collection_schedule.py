from flask import Blueprint, request, jsonify
from flask_login import login_required
from services.collection_schedule_service import CollectionScheduleService

collection_schedule_bp = Blueprint('collection_schedule', __name__)

@collection_schedule_bp.route('/collection_schedule', methods=['POST'])
@login_required
def create_collection_schedule():
    data = request.json
    new_schedule = CollectionScheduleService.create_schedule(data)
    return jsonify({'message': 'Collection schedule created successfully', 'schedule_id': new_schedule.id}), 201

@collection_schedule_bp.route('/collection_schedule', methods=['GET'])
@login_required
def get_collection_schedules():
    filters = {
        'staff_id': request.args.get('staff_id'),
        'loan_status': request.args.get('loan_status')
    }
    schedules = CollectionScheduleService.get_schedules(filters)
    return jsonify([{
        'id': schedule.id,
        'staff_id': schedule.staff_id,
        'loan_id': schedule.loan_id,
        'schedule_date': schedule.schedule_date.isoformat(),
        'status': schedule.status
    } for schedule in schedules]), 200

@collection_schedule_bp.route('/collection_schedule/<int:schedule_id>', methods=['PUT'])
@login_required
def update_collection_schedule(schedule_id):
    data = request.json
    updated_schedule = CollectionScheduleService.update_schedule(schedule_id, data)
    return jsonify({'message': 'Collection schedule updated successfully', 'schedule_id': updated_schedule.id}), 200

@collection_schedule_bp.route('/collection_schedule/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_collection_schedule(schedule_id):
    CollectionScheduleService.delete_schedule(schedule_id)
    return jsonify({'message': 'Collection schedule deleted successfully'}), 200
