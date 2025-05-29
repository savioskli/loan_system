from flask import current_app
from extensions import db
from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from models.module import Module
from models.form_field import FormField
import logging
import traceback

logger = logging.getLogger(__name__)

def get_sql_type(field_type):
    """Convert form field type to SQL type string"""
    type_mapping = {
        'text': 'VARCHAR(255)',
        'email': 'VARCHAR(255)',
        'tel': 'VARCHAR(20)',
        'number': 'FLOAT',
        'textarea': 'VARCHAR(1000)',
        'select': 'VARCHAR(255)',
        'radio': 'VARCHAR(255)',
        'checkbox': 'BOOLEAN',
        'date': 'DATETIME',
        'file': 'VARCHAR(500)',  # Store file path
    }
    return type_mapping.get(field_type, 'VARCHAR(255)')

def create_or_update_module_table(module_code):
    """Create or update a database table based on module form fields"""
    try:
        logger.info(f"Starting table update for module {module_code}")
        # Get module and its fields
        module = Module.query.filter_by(code=module_code).first()
        if not module:
            logger.error(f"Module {module_code} not found")
            return False

        form_fields = FormField.query.filter_by(module_id=module.id).all()
        logger.info(f"Found {len(form_fields)} fields for module {module_code}")
        
        if not form_fields:
            logger.error(f"No form fields found for module {module_code}")
            return False
        
        # Table name will be lowercase module code
        table_name = f"form_data_{module_code.lower()}"
        logger.info(f"Working with table: {table_name}")
        
        # Create MetaData instance
        metadata = MetaData()
        
        # Get existing table if it exists
        inspector = db.inspect(db.engine)
        existing_columns = {}
        if table_name in inspector.get_table_names():
            existing_columns = {col['name']: col for col in inspector.get_columns(table_name)}
            logger.info(f"Existing columns in {table_name}: {list(existing_columns.keys())}")
        
        # Define base columns that should never be removed
        base_columns = {'id', 'user_id', 'submission_date', 'status', 'client_type_id'}
        
        try:
            with db.engine.connect() as conn:
                # Create table if it doesn't exist
                if table_name not in inspector.get_table_names():
                    logger.info(f"Creating new table: {table_name}")
                    # Validate SQL type for each field before creating table
                    for field in form_fields:
                        sql_type = get_sql_type(field.field_type)
                        if not sql_type:
                            logger.error(f"Invalid field type {field.field_type} for field {field.field_name}")
                            return False
                    
                    sql = f"""
                    CREATE TABLE {table_name} (
                        id INT NOT NULL AUTO_INCREMENT,
                        user_id INT NOT NULL,
                        submission_date DATETIME NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                        client_type_id INT,
                        client_type VARCHAR(255),
                        PRIMARY KEY (id),
                        FOREIGN KEY (user_id) REFERENCES staff(id),
                        FOREIGN KEY (client_type_id) REFERENCES client_types(id)
                    )
                    """
                    logger.debug(f"Executing SQL: {sql}")
                    try:
                        conn.execute(text(sql))
                        logger.info(f"Successfully created table {table_name}")
                    except Exception as create_error:
                        logger.error(f"Error creating table: {str(create_error)}")
                        logger.error(traceback.format_exc())
                        return False
                
                # Add new columns or modify existing ones
                for field in form_fields:
                    col_name = field.field_name.lower()
                    sql_type = get_sql_type(field.field_type)
                    if not sql_type:
                        logger.error(f"Invalid field type {field.field_type} for field {field.field_name}")
                        continue
                        
                    logger.info(f"Processing field: {col_name} (type: {field.field_type} -> {sql_type})")
                    
                    if col_name not in existing_columns:
                        # Add new column
                        logger.info(f"Adding new column: {col_name}")
                        sql = f'ALTER TABLE {table_name} ADD COLUMN {col_name} {sql_type} {"NOT NULL" if field.is_required else "NULL"}'
                        logger.debug(f"Executing SQL: {sql}")
                        try:
                            conn.execute(text(sql))
                            logger.info(f"Successfully added column {col_name}")
                        except Exception as add_error:
                            logger.error(f"Error adding column {col_name}: {str(add_error)}")
                            logger.error(traceback.format_exc())
                            continue
                    else:
                        # Modify existing column if type changed
                        current_type = str(existing_columns[col_name]['type'])
                        if current_type.upper() != sql_type.upper():
                            logger.info(f"Modifying column type for {col_name}: {current_type} -> {sql_type}")
                            sql = f'ALTER TABLE {table_name} MODIFY COLUMN {col_name} {sql_type} {"NOT NULL" if field.is_required else "NULL"}'
                            logger.debug(f"Executing SQL: {sql}")
                            try:
                                conn.execute(text(sql))
                                logger.info(f"Successfully modified column {col_name}")
                            except Exception as modify_error:
                                logger.error(f"Error modifying column {col_name}: {str(modify_error)}")
                                logger.error(traceback.format_exc())
                                continue
                
                # Remove columns that no longer exist in form_fields
                field_names = {field.field_name.lower() for field in form_fields}
                for col_name in existing_columns:
                    if col_name not in field_names and col_name not in base_columns:
                        logger.info(f"Removing column: {col_name}")
                        sql = f'ALTER TABLE {table_name} DROP COLUMN {col_name}'
                        logger.debug(f"Executing SQL: {sql}")
                        try:
                            conn.execute(text(sql))
                            logger.info(f"Successfully removed column {col_name}")
                        except Exception as drop_error:
                            logger.error(f"Error dropping column {col_name}: {str(drop_error)}")
                            logger.error(traceback.format_exc())
                            continue
                
                conn.commit()
                logger.info(f"Successfully updated table {table_name}")
                
                # Verify all required columns exist
                inspector = db.inspect(db.engine)
                final_columns = {col['name'] for col in inspector.get_columns(table_name)}
                missing_base_columns = base_columns - final_columns
                if missing_base_columns:
                    logger.error(f"Table {table_name} is missing required base columns: {missing_base_columns}")
                    return False
                    
                return True
                
        except Exception as sql_error:
            logger.error(f"SQL Error: {str(sql_error)}")
            logger.error(traceback.format_exc())
            return False
            
    except Exception as e:
        logger.error(f"Error creating/updating table for module {module_code}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def drop_module_table(module_code):
    """Drop the database table for a module"""
    try:
        table_name = f"form_data_{module_code.lower()}"
        with db.engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error dropping table for module {module_code}: {str(e)}")
        return False
