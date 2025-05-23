from flask import current_app
from extensions import db
from sqlalchemy import text
import re

def get_sql_type(field_type, validation_rules=None):
    """
    Convert form field type to SQL column type.
    
    Args:
        field_type (str): Form field type
        validation_rules (dict): Validation rules for the field
    
    Returns:
        str: SQL column type
    """
    if field_type in ['text', 'email', 'tel', 'password']:
        max_length = validation_rules.get('max_length', 255) if validation_rules else 255
        return f'VARCHAR({max_length})'
    elif field_type == 'textarea':
        return 'TEXT'
    elif field_type == 'number':
        return 'INT'
    elif field_type == 'decimal':
        return 'DECIMAL(10,2)'
    elif field_type == 'date':
        return 'DATE'
    elif field_type == 'datetime':
        return 'DATETIME'
    elif field_type == 'boolean':
        return 'BOOLEAN'
    elif field_type in ['select', 'radio']:
        return 'VARCHAR(100)'
    elif field_type == 'checkbox':
        return 'JSON'
    elif field_type == 'file':
        return 'VARCHAR(255)'
    else:
        return 'VARCHAR(255)'

def create_module_table(module_name):
    """
    Create a new table for a module.
    
    Args:
        module_name (str): Name of the module
    
    Returns:
        str: Name of the created table
    """
    try:
        # Convert module name to snake_case for table name
        # First, replace any spaces with underscores
        table_name = module_name.replace(' ', '_')
        # Then convert any remaining CamelCase to snake_case
        table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', table_name).lower()
        # Clean up any non-alphanumeric chars
        table_name = re.sub(r'[^a-z0-9_]', '_', table_name)
        # Replace multiple underscores with single underscore
        table_name = re.sub(r'_+', '_', table_name)
        # Add _data suffix
        table_name = f"{table_name}_data"
        
        # Create the table
        sql = text(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            created_by INT,
            updated_by INT,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (created_by) REFERENCES staff(id),
            FOREIGN KEY (updated_by) REFERENCES staff(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        db.session.execute(sql)
        db.session.commit()
        
        return table_name
    except Exception as e:
        current_app.logger.error(f"Error creating module table: {str(e)}")
        raise e

def add_field_to_table(table_name, field_name, field_type, validation_rules=None, is_required=False):
    """
    Add a new field to a module's table.
    
    Args:
        table_name (str): Name of the table to add field to
        field_name (str): Name of the field to add
        field_type (str): Type of the field (text, number, date, etc.)
        validation_rules (dict): Validation rules for the field
        is_required (bool): Whether the field is required
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        current_app.logger.info(f"Adding field to table {table_name}:")
        current_app.logger.info(f"Field name: {field_name}")
        current_app.logger.info(f"Field type: {field_type}")
        current_app.logger.info(f"Validation rules: {validation_rules}")
        current_app.logger.info(f"Is required: {is_required}")
        
        if not table_name:
            raise ValueError("No table name provided")
        
        # Convert field name to snake_case
        # First, replace any spaces with underscores
        column_name = field_name.replace(' ', '_')
        # Then convert any remaining CamelCase to snake_case
        column_name = re.sub(r'(?<!^)(?=[A-Z])', '_', column_name).lower()
        # Finally clean up any non-alphanumeric chars
        column_name = re.sub(r'[^a-z0-9_]', '_', column_name)
        # Replace multiple underscores with single underscore
        column_name = re.sub(r'_+', '_', column_name)
        current_app.logger.info(f"Column name after conversion: {column_name}")
        
        # Get SQL type
        sql_type = get_sql_type(field_type, validation_rules)
        current_app.logger.info(f"SQL type: {sql_type}")
        
        # Create ALTER TABLE SQL
        sql = text(f"""
        ALTER TABLE {table_name}
        ADD COLUMN {column_name} {sql_type} {'' if is_required else 'DEFAULT NULL'}
        """)
        current_app.logger.info(f"SQL query: {sql}")
        
        # Execute SQL
        db.session.execute(sql)
        db.session.commit()
        current_app.logger.info("Field added successfully")
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error adding field to table {table_name}:")
        current_app.logger.error(f"Error message: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return False
