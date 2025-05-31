from flask import Blueprint, jsonify, request, current_app
from extensions import db
import logging
from sqlalchemy.exc import SQLAlchemyError
import traceback

bp = Blueprint('system_references', __name__)

@bp.route('/system-references/by-id/<int:reference_id>')
def get_reference_values_by_id(reference_id):
    """Get system reference values for a given reference ID."""
    try:
        current_app.logger.info(f'Received request for reference_id: {reference_id}')
        current_app.logger.info(f'Request URL: {request.url}')
        current_app.logger.info(f'Request headers: {dict(request.headers)}')
        parent_value = request.args.get('parent_value')
        current_app.logger.info(f'Parent value: {parent_value}')
        
        # Log database connection info
        current_app.logger.info(f'Database URL: {current_app.config.get("SQLALCHEMY_DATABASE_URI")}')
    
        # First, verify the reference field exists
        field_query = "SELECT id, name FROM system_reference_fields WHERE id = :field_id"
        current_app.logger.info(f'Checking field existence with query: {field_query}, field_id: {reference_id}')
        
        with db.engine.connect() as conn:
            # Check if the field exists using text() for parameter binding
            from sqlalchemy import text
            
            # First check if the field exists
            field_result = conn.execute(
                text(field_query),
                {'field_id': reference_id}
            ).fetchone()
            
            if not field_result:
                current_app.logger.error(f'No system reference field found with id: {reference_id}')
                return jsonify({
                    'error': 'Not Found',
                    'message': f'No system reference field found with id: {reference_id}'
                }), 404
            
            field_id, field_name = field_result
            current_app.logger.info(f'Found field: {field_name} (ID: {field_id})')
            
            # Get the reference values using text() for parameter binding
            query = """
                SELECT id, value, label, is_active, 
                       COALESCE(parent_value_id, '') as parent_value_id
                FROM system_reference_values 
                WHERE field_id = :field_id AND is_active = 1
            """
            
            params = {'field_id': reference_id}
            
            if parent_value:
                query += " AND parent_value_id = :parent_value"
                params['parent_value'] = parent_value
            
            query += " ORDER BY label"
            
            current_app.logger.info(f'Executing values query: {query} with params: {params}')
            
            # Execute the query with named parameters
            result = conn.execute(text(query), params)
            
            # Convert result to list of dicts for better logging
            values = []
            for row in result:
                # Convert row to dictionary using _asdict() if available, otherwise manual conversion
                if hasattr(row, '_asdict'):
                    row_dict = row._asdict()
                else:
                    # Manual conversion for SQLAlchemy 1.4+
                    row_dict = {}
                    for key in row.keys():
                        row_dict[key] = row[key]
                
                current_app.logger.info(f'Row data: {row_dict}')
                
                # Ensure required fields exist
                if 'value' in row_dict and 'label' in row_dict:
                    values.append({
                        'value': str(row_dict['value']),
                        'label': str(row_dict['label'])
                    })
                else:
                    current_app.logger.error(f'Missing required fields in row: {row_dict}')
            
            current_app.logger.info(f'Found {len(values)} reference values for field {field_name} (ID: {field_id})')
            
            if not values:
                current_app.logger.warning(f'No reference values found for field {field_name} (ID: {field_id})')
                
            return jsonify(values)
        
    except SQLAlchemyError as e:
        current_app.logger.error(f'Database error: {str(e)}')
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Database error',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500
    except Exception as e:
        current_app.logger.error(f'Unexpected error: {str(e)}')
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Keep the old endpoint for backward compatibility
@bp.route('/api/system-references/<code>')
def get_reference_values_by_code(code):
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

@bp.route('/system-references', methods=['POST'])
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
