from sqlalchemy import inspect
from sqlalchemy.orm import class_mapper

def get_table_structure(model_class):
    """
    Inspect a SQLAlchemy model and return its structure including columns,
    types, and constraints.
    """
    if not model_class:
        return None
        
    mapper = class_mapper(model_class)
    inspector = inspect(mapper)
    
    structure = {
        'table_name': mapper.mapped_table.name,
        'columns': [],
        'relationships': []
    }
    
    # Get column information
    for column in mapper.columns:
        column_info = {
            'name': column.name,
            'type': str(column.type),
            'nullable': column.nullable,
            'default': column.default.arg if column.default else None,
            'primary_key': column.primary_key,
            'foreign_key': None,
            'unique': column.unique,
            'index': column.index,
            'doc': column.doc
        }
        
        # Handle foreign keys
        if column.foreign_keys:
            fk = list(column.foreign_keys)[0]
            column_info['foreign_key'] = {
                'target_table': fk.column.table.name,
                'target_column': fk.column.name
            }
            
        structure['columns'].append(column_info)
    
    # Get relationship information
    for rel in mapper.relationships:
        structure['relationships'].append({
            'name': rel.key,
            'target': rel.mapper.class_.__name__,
            'uselist': rel.uselist,
            'lazy': str(rel.lazy)
        })
    
    return structure

def get_form_fields_from_model(model_class, module_id=None):
    """
    Fetch form field definitions from the form_fields table for a given module.
    
    Args:
        model_class: The SQLAlchemy model class (unused, kept for backward compatibility)
        module_id: The ID of the module to fetch fields for
        
    Returns:
        List of form field definitions
    """
    from models.form_field import FormField
    from models.form_section import FormSection
    
    if not module_id:
        return []
    
    # Get all active sections for this module, ordered by section order
    sections = FormSection.query.filter_by(
        module_id=module_id,
        is_active=True
    ).order_by(FormSection.order.asc()).all()
    
    form_fields = []
    
    # Get all fields for this module, ordered by field_order
    query = FormField.query.filter_by(
        module_id=module_id
    ).order_by(FormField.field_order.asc())
    
    fields = query.all()
    
    # Convert FormField objects to dictionary format expected by the template
    for field in fields:
        field_dict = {
            'id': field.id,
            'field_name': field.field_name,
            'field_label': field.field_label,
            'field_placeholder': field.field_placeholder,
            'field_type': field.field_type,
            'is_required': field.is_required,
            'field_order': field.field_order,
            'section_id': field.section_id,
            'section_name': field.section.name if field.section else None,
            'options': field.options or [],
            'validation_rules': field.validation_rules or {},
            'client_type_restrictions': field.client_type_restrictions or [],
            'depends_on': field.depends_on,
            'reference_field_code': field.reference_field_code,
            'is_cascading': field.is_cascading,
            'parent_field_id': field.parent_field_id,
            'is_system': field.is_system,
            'system_reference_field_id': field.system_reference_field_id
        }
        
        # Add validation attributes if they exist
        if field.validation_rules:
            for rule, value in field.validation_rules.items():
                field_dict[rule] = value
        
        form_fields.append(field_dict)
    
    return form_fields

def get_model_by_module_id(module_id):
    """
    Given a module_id, return the corresponding SQLAlchemy model class.
    Maps module IDs to their respective model classes.
    
    Args:
        module_id (int): The ID of the module to get the model for
        
    Returns:
        SQLAlchemy model class or None if no mapping exists
    """
    # Import specific models to avoid circular imports
    from models.client import Client
    from models.loan import Loan
    from models.prospect_registration import ProspectRegistration
    from models.client_registration import ClientRegistration
    from models.staff import Staff
    from models.branch import Branch
    from models.product import Product
    from models.client_type import ClientType
    
    # Module ID to model mapping
    # Update this mapping based on your actual module IDs and models
    model_mapping = {
        1: Client,               # Client management module
        2: Loan,                 # Loan management module
        3: ProspectRegistration,  # Prospect registration module
        32: ProspectRegistration, # Prospect registration data
        33: ClientRegistration,   # Client registration data
        # Add more mappings as needed
    }
    
    # Get the model class from the mapping
    return model_mapping.get(module_id)
