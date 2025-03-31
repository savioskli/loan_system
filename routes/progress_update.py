from flask import Blueprint, request, jsonify
from services.progress_update_service import ProgressUpdateService
from flask_login import login_required
from utils.decorators import csrf_required

progress_update_bp = Blueprint('progress_update', __name__)

@progress_update_bp.route('/api/collection-schedules/<int:schedule_id>/progress', methods=['POST'])
@login_required
@csrf_required
def create_progress_update(schedule_id):
    try:
        # Extract data from form
        data = request.form
        status = data.get('status')
        amount = float(data.get('amount')) if data.get('amount') else None
        collection_method = data.get('method')
        notes = data.get('notes')
        attachment = request.files.get('attachment')

        # Validate required fields
        if not status:
            return jsonify({'error': 'Status is required'}), 400

        # Create progress update
        progress_update = ProgressUpdateService.create_progress_update(
            collection_schedule_id=schedule_id,
            status=status,
            amount=amount,
            collection_method=collection_method,
            notes=notes,
            attachment=attachment
        )

        return jsonify({
            'message': 'Progress update created successfully',
            'progress_update': {
                'id': progress_update.id,
                'status': progress_update.status,
                'amount': progress_update.amount,
                'collection_method': progress_update.collection_method,
                'notes': progress_update.notes,
                'attachment_url': progress_update.attachment_url,
                'created_at': progress_update.created_at.isoformat()
            }
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An error occurred while creating progress update'}), 500

@progress_update_bp.route('/api/collection-schedules/<int:schedule_id>/progress', methods=['GET'])
@login_required
def get_progress_updates(schedule_id):
    try:
        updates = ProgressUpdateService.get_progress_updates(schedule_id)
        return jsonify({
            'updates': [{
                'id': update.id,
                'status': update.status,
                'amount': update.amount,
                'collection_method': update.collection_method,
                'notes': update.notes,
                'attachment_url': update.attachment_url,
                'created_at': update.created_at.isoformat()
            } for update in updates]
        }), 200

    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching progress updates'}), 500
