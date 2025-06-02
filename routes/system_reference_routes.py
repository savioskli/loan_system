from flask import Blueprint, jsonify, current_app
from flask_login import login_required
from extensions import db
from sqlalchemy import text

system_reference_bp = Blueprint('system_reference', __name__, url_prefix='/api/system-references')

@system_reference_bp.route('/<int:reference_id>')
@login_required
def get_system_reference_options(reference_id):
    """Get options for a system reference field."""
    try:
        # Query for the reference options using raw SQL since we don't have the model
        query = text("""
            SELECT id as value, label
            FROM system_reference_values
            WHERE field_id = :reference_id
            AND is_active = 1
            ORDER BY label
        """)
        
        current_app.logger.info(f'Executing query for reference_id: {reference_id}')
        result = db.session.execute(query, {'reference_id': reference_id})
        
        # Convert result rows to list of dicts using proper mapping
        options = [{'value': row.value, 'label': row.label} for row in result]
        current_app.logger.info(f'Found {len(options)} options for reference_id {reference_id}')
        
        return jsonify(options)
        
    except Exception as e:
        current_app.logger.error(f'Error fetching system reference options for ID {reference_id}: {str(e)}')
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch system reference options'
        }), 500
