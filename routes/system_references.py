from flask import Blueprint, jsonify, request
from extensions import db

bp = Blueprint('system_references', __name__)

@bp.route('/api/system-references/<code>')
def get_reference_values(code):
    """Get system reference values for a given code."""
    parent_value = request.args.get('parent_value')
    
    query = """
        SELECT srv.id, srv.value, srv.label
        FROM system_reference_values srv
        JOIN system_reference_fields srf ON srv.field_id = srf.id
        WHERE srf.code = %s AND srv.is_active = TRUE
    """
    params = [code]
    
    if parent_value:
        query += " AND srv.parent_value_id = %s"
        params.append(parent_value)
    
    query += " ORDER BY srv.label"
    
    with db.engine.connect() as conn:
        result = conn.execute(query, params)
        values = [{"value": row[1], "label": row[2]} for row in result]
        
    return jsonify(values)

@bp.route('/api/system-references', methods=['POST'])
def create_reference_value():
    """Create a new system reference value."""
    data = request.json
    
    query = """
        INSERT INTO system_reference_values (field_id, value, label, parent_value_id)
        SELECT srf.id, %s, %s, %s
        FROM system_reference_fields srf
        WHERE srf.code = %s
    """
    
    with db.engine.connect() as conn:
        conn.execute(query, [
            data['value'],
            data['label'],
            data.get('parent_value_id'),
            data['reference_code']
        ])
        
    return jsonify({"status": "success"})
