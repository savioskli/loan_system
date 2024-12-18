from flask import Blueprint, jsonify, request
from models.field_dependency import FieldDependency
from models.module import FormField
from extensions import db
from flask_login import login_required, current_user

dependencies_bp = Blueprint('dependencies', __name__)

@dependencies_bp.route('/api/fields/<int:module_id>', methods=['GET'])
@login_required
def get_module_fields(module_id):
    """Get all fields for a module"""
    # Exclude the current field from the list to prevent self-dependency
    current_field_id = request.args.get('current_field_id', None)
    query = FormField.query.filter_by(module_id=module_id)
    
    if current_field_id:
        query = query.filter(FormField.id != int(current_field_id))
    
    fields = query.order_by(FormField.field_name).all()
    return jsonify([{
        'id': field.id,
        'value': str(field.id),  # Use ID as value for better reliability
        'label': field.field_label,  # Use the human-readable label
        'field_type': field.field_type
    } for field in fields])

@dependencies_bp.route('/api/fields/<int:field_id>/options', methods=['GET'])
@login_required
def get_field_options(field_id):
    """Get options for a field"""
    field = FormField.query.get_or_404(field_id)
    if not field.options:
        return jsonify([])
        
    return jsonify([{
        'value': option.get('value', ''),
        'label': option.get('label', option.get('value', ''))  # Use label if available, otherwise value
    } for option in field.options])

@dependencies_bp.route('/api/field-dependencies/<int:field_id>', methods=['GET'])
@login_required
def get_dependencies(field_id):
    """Get all dependencies for a field"""
    dependencies = FieldDependency.query.filter_by(parent_field_id=field_id).all()
    return jsonify([{
        'id': dep.id,
        'dependent_field_id': dep.dependent_field_id,
        'dependent_field_name': dep.dependent_field.field_name,
        'dependent_field_label': dep.dependent_field.field_label,
        'show_on_values': dep.get_show_values()
    } for dep in dependencies])

@dependencies_bp.route('/api/field-dependencies/<field_name>', methods=['GET'])
@login_required
def get_field_dependencies_by_name(field_name):
    """Get all dependencies where this field is the parent"""
    field = FormField.query.filter_by(field_name=field_name).first_or_404()
    dependencies = FieldDependency.query.filter_by(parent_field_id=field.id).all()
    
    return jsonify([{
        'id': dep.id,
        'dependent_field': dep.dependent_field.field_name,
        'show_values': dep.get_show_values()
    } for dep in dependencies])

@dependencies_bp.route('/api/field-dependencies', methods=['POST'])
@login_required
def create_dependency():
    """Create a new field dependency"""
    data = request.json
    dependency = FieldDependency(
        parent_field_id=data['parent_field_id'],
        dependent_field_id=data['dependent_field_id']
    )
    dependency.set_show_values(data['show_on_values'])
    
    db.session.add(dependency)
    db.session.commit()
    
    return jsonify({
        'id': dependency.id,
        'dependent_field_id': dependency.dependent_field_id,
        'dependent_field_name': dependency.dependent_field.field_name,
        'dependent_field_label': dependency.dependent_field.field_label,
        'show_on_values': dependency.get_show_values()
    })

@dependencies_bp.route('/api/field-dependencies/<int:dep_id>', methods=['PUT'])
@login_required
def update_dependency(dep_id):
    """Update a field dependency"""
    dependency = FieldDependency.query.get_or_404(dep_id)
    data = request.json
    
    if 'show_on_values' in data:
        dependency.set_show_values(data['show_on_values'])
    if 'dependent_field_id' in data:
        dependency.dependent_field_id = data['dependent_field_id']
    
    db.session.commit()
    
    return jsonify({
        'id': dependency.id,
        'dependent_field_id': dependency.dependent_field_id,
        'dependent_field_name': dependency.dependent_field.field_name,
        'show_on_values': dependency.get_show_values()
    })

@dependencies_bp.route('/api/field-dependencies/<int:dep_id>', methods=['DELETE'])
@login_required
def delete_dependency(dep_id):
    """Delete a field dependency"""
    dependency = FieldDependency.query.get_or_404(dep_id)
    db.session.delete(dependency)
    db.session.commit()
    return jsonify({'message': 'Dependency deleted successfully'}), 200
