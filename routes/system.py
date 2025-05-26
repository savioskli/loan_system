from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from extensions import db, csrf
from models.module import Module
from sqlalchemy import text
from functools import wraps

bp = Blueprint('system_reference_admin', __name__, url_prefix='/admin/system')

@bp.route('/reference-fields')
def reference_fields():
    """List all system reference fields."""
    query = text("""
        SELECT 
            srf.id,
            srf.code,
            srf.name,
            srf.description,
            srf.is_active,
            COUNT(srv.id) as value_count
        FROM system_reference_fields srf
        LEFT JOIN system_reference_values srv ON srf.id = srv.field_id
        GROUP BY srf.id
        ORDER BY srf.name
    """)
    
    result = db.session.execute(query)
    fields = [{
        'id': row.id,
        'code': row.code,
        'name': row.name,
        'description': row.description,
        'is_active': row.is_active,
        'value_count': row.value_count
    } for row in result]
    
    return render_template('admin/system/reference_fields.html', reference_fields=fields)

@bp.route('/reference-fields/<int:field_id>/values')
def reference_values(field_id):
    """List values for a specific reference field."""
    # Get field info
    field_query = text("""
        SELECT id, code, name, description, is_active
        FROM system_reference_fields
        WHERE id = :field_id
    """)
    
    # Get values with parent info
    values_query = text("""
        SELECT 
            srv.id,
            srv.value,
            srv.label,
            srv.is_active,
            srv.parent_value_id,
            p.label as parent_label,
            p.value as parent_value
        FROM system_reference_values srv
        LEFT JOIN system_reference_values p ON srv.parent_value_id = p.id
        WHERE srv.field_id = :field_id
        ORDER BY COALESCE(p.label, srv.label)
    """)
    
    # Get potential parent values
    parent_values_query = text("""
        SELECT id, value, label
        FROM system_reference_values
        WHERE field_id = :field_id AND is_active = 1
        ORDER BY label
    """)
    
    field_result = db.session.execute(field_query, {'field_id': field_id})
    field = field_result.fetchone()
    
    if not field:
        return redirect(url_for('system_reference_admin.reference_fields'))
        
    field_dict = {
        'id': field.id,
        'code': field.code,
        'name': field.name,
        'description': field.description,
        'is_active': field.is_active
    }
    
    values_result = db.session.execute(values_query, {'field_id': field_id})
    values = []
    for row in values_result:
        value_dict = {
            'id': row.id,
            'value': row.value,
            'label': row.label,
            'is_active': row.is_active,
            'parent_value_id': row.parent_value_id,
            'parent_value': row.parent_value,
            'parent_label': row.parent_label
        }
        values.append(value_dict)
    
    parent_values_result = db.session.execute(parent_values_query, {'field_id': field_id})
    parent_values = []
    for row in parent_values_result:
        parent_dict = {
            'id': row.id,
            'value': row.value,
            'label': row.label
        }
        parent_values.append(parent_dict)
    
    return render_template('admin/system/reference_values.html',
                         field=field_dict,
                         values=values,
                         parent_values=parent_values)

# API Endpoints

@bp.route('/fields/<int:field_id>', methods=['GET'])
def get_field(field_id):
    """Get a single system reference field."""
    query = text("""
        SELECT id, code, name, description, is_active
        FROM system_reference_fields
        WHERE id = :field_id
    """)
    
    result = db.session.execute(query, {'field_id': field_id})
    row = result.fetchone()
    
    if not row:
        return jsonify({'error': 'Field not found'}), 404
        
    field = {
        'id': row.id,
        'code': row.code,
        'name': row.name,
        'description': row.description,
        'is_active': row.is_active
    }
    
    return jsonify(field)

@bp.route('/fields', methods=['POST'])
def create_field():
    """Create a new system reference field."""
    data = request.json
    
    query = text("""
        INSERT INTO system_reference_fields (code, name, description)
        VALUES (:code, :name, :description)
    """)
    
    db.session.execute(query, {
        'code': data['code'],
        'name': data['name'],
        'description': data.get('description')
    })
    db.session.commit()
        
    return jsonify({"status": "success"})

@bp.route('/fields/<int:field_id>', methods=['PUT'])
def update_field(field_id):
    """Update a system reference field."""
    data = request.json
    
    query = text("""
        UPDATE system_reference_fields
        SET code = :code, name = :name, description = :description
        WHERE id = :field_id
    """)
    
    params = {
        'code': data['code'],
        'name': data['name'],
        'description': data.get('description'),
        'field_id': field_id
    }
    
    db.session.execute(query, params)
    db.session.commit()
        
    return jsonify({"status": "success"})

@bp.route('/fields/<int:field_id>/toggle', methods=['POST'])
def toggle_field(field_id):
    """Toggle active status of a field."""
    query = text("""
        UPDATE system_reference_fields
        SET is_active = NOT is_active
        WHERE id = :field_id
    """)
    
    db.session.execute(query, {'field_id': field_id})
    db.session.commit()
        
    return jsonify({"status": "success"})

@bp.route('/values', methods=['POST'])
def create_value():
    """Create a new reference value."""
    data = request.json
    
    query = text("""
        INSERT INTO system_reference_values (field_id, value, label, parent_value_id)
        VALUES (:field_id, :value, :label, :parent_value_id)
    """)
    
    params = {
        'field_id': data['field_id'],
        'value': data['value'],
        'label': data['label'],
        'parent_value_id': data.get('parent_value_id') if data.get('parent_value_id') else None
    }
    
    db.session.execute(query, params)
    db.session.commit()
        
    return jsonify({"status": "success"})

@bp.route('/values/<int:value_id>', methods=['GET'])
def get_value(value_id):
    """Get a single reference value."""
    query = text("""
        SELECT id, field_id, value, label, parent_value_id, is_active
        FROM system_reference_values
        WHERE id = :value_id
    """)
    
    result = db.session.execute(query, {'value_id': value_id})
    row = result.fetchone()
    
    if not row:
        return jsonify({'error': 'Value not found'}), 404
        
    value = {
        'id': row.id,
        'field_id': row.field_id,
        'value': row.value,
        'label': row.label,
        'parent_value_id': row.parent_value_id,
        'is_active': row.is_active
    }
    
    return jsonify(value)

@bp.route('/values/<int:value_id>', methods=['PUT'])
def update_value(value_id):
    """Update a reference value."""
    data = request.json
    
    query = text("""
        UPDATE system_reference_values
        SET value = :value, label = :label, parent_value_id = :parent_value_id
        WHERE id = :value_id
    """)
    
    params = {
        'value': data['value'],
        'label': data['label'],
        'parent_value_id': data.get('parent_value_id') if data.get('parent_value_id') else None,
        'value_id': value_id
    }
    
    db.session.execute(query, params)
    db.session.commit()
        
    return jsonify({"status": "success"})

@bp.route('/values/<int:value_id>/toggle', methods=['POST'])
def toggle_value(value_id):
    """Toggle active status of a value."""
    query = """
        UPDATE system_reference_values
        SET is_active = NOT is_active
        WHERE id = %s
    """
    
    with db.engine.connect() as conn:
        conn.execute(query, [value_id])
        
    return jsonify({"status": "success"})
