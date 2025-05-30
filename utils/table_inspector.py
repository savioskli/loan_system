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

def get_form_fields_from_model(model_class):
    """
    Convert a SQLAlchemy model structure into form field definitions.
    """
    structure = get_table_structure(model_class)
    if not structure:
        return []
    
    form_fields = []
    
    # Skip these standard columns as they're typically not needed in forms
    skip_columns = {'id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted'}
    
    for column in structure['columns']:
        if column['name'] in skip_columns:
            continue
            
        field = {
            'field_name': column['name'],
            'field_label': ' '.join(word.capitalize() for word in column['name'].split('_')),
            'field_type': 'text',  # Default type
            'is_required': not column['nullable'],
            'default_value': column['default']
        }
        
        # Map SQL types to form field types
        column_type = column['type'].lower()
        if 'varchar' in column_type or 'char' in column_type or 'text' in column_type:
            field['field_type'] = 'text'
            if 'email' in column['name']:
                field['field_type'] = 'email'
            elif 'phone' in column['name'] or 'mobile' in column['name'] or 'tel' in column['name']:
                field['field_type'] = 'tel'
                field['validation'] = {'pattern': '[0-9]{10,}'}
                field['hint'] = 'Format: 07XXXXXXXX or +254XXXXXXXXX'
        elif 'int' in column_type or 'decimal' in column_type or 'float' in column_type or 'numeric' in column_type:
            field['field_type'] = 'number'
            if 'decimal' in column_type or 'numeric' in column_type or 'float' in column_type:
                field['step'] = '0.01'
        elif 'date' in column_type or 'time' in column_type:
            field['field_type'] = 'date'
        elif 'boolean' in column_type:
            field['field_type'] = 'checkbox'
        elif 'enum' in column_type:
            field['field_type'] = 'select'
            # Extract enum values
            enum_values = column_type.replace('enum(', '').replace(')', '').replace("'", '').split(',')
            field['options'] = [{'value': v, 'label': v.replace('_', ' ').title()} for v in enum_values]
        
        # Handle foreign keys as select fields
        if column['foreign_key']:
            field['field_type'] = 'select'
            field['related_model'] = column['foreign_key']['target_table']
            
        form_fields.append(field)
    
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
        # Add more mappings as needed
    }
    
    # Get the model class from the mapping
    return model_mapping.get(module_id)
