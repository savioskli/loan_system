from extensions import db
from sqlalchemy import text
import re

def create_module_table(module_name):
    """
    Create a database table for a module.
    
    Args:
        module_name (str): Name of the module, will be converted to snake_case for table name
    
    Returns:
        str: Name of the created table
    """
    # Convert module name to snake_case for table name
    table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', module_name).lower()  # Convert CamelCase to snake_case
    table_name = re.sub(r'[^a-z0-9_]', '_', table_name)  # Replace any non-alphanumeric chars with underscore
    table_name = f"{table_name}_data"  # Add _data suffix to avoid conflicts
    
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
