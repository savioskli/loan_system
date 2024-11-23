import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

from extensions import db
from models.client_type import ClientType
from app import create_app
from sqlalchemy import text

def column_exists(conn, table, column):
    """Check if a column exists in the table."""
    result = conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = DATABASE() "
        "AND table_name = :table "
        "AND column_name = :column"
    ), {"table": table, "column": column})
    return result.scalar() > 0

def fix_client_types_table():
    """Fix the client_types table schema to match the model."""
    app = create_app()
    with app.app_context():
        # Create a connection
        conn = db.engine.connect()
        
        try:
            # Start a transaction
            trans = conn.begin()
            
            # Rename columns if they exist with old names
            renames = [
                ("code", "client_code", "VARCHAR(20)"),
                ("name", "client_name", "VARCHAR(100)")
            ]
            
            for old_name, new_name, col_type in renames:
                if column_exists(conn, "client_types", old_name):
                    conn.execute(text(f"ALTER TABLE client_types CHANGE {old_name} {new_name} {col_type}"))
                elif not column_exists(conn, "client_types", new_name):
                    # If neither old nor new column exists, create the new column
                    conn.execute(text(f"ALTER TABLE client_types ADD COLUMN {new_name} {col_type}"))
            
            # Add new columns if they don't exist
            new_columns = [
                ("effective_from", "DATE NULL"),
                ("effective_to", "DATE NULL"),
                ("status", "BOOLEAN DEFAULT TRUE")
            ]
            
            for col_name, col_type in new_columns:
                if not column_exists(conn, "client_types", col_name):
                    conn.execute(text(f"ALTER TABLE client_types ADD COLUMN {col_name} {col_type}"))
            
            # Drop columns if they exist
            drop_columns = ["description", "form_schema"]
            for col_name in drop_columns:
                if column_exists(conn, "client_types", col_name):
                    conn.execute(text(f"ALTER TABLE client_types DROP COLUMN {col_name}"))
            
            # Commit the transaction
            trans.commit()
            print("Successfully updated client_types table schema")
            
        except Exception as e:
            # Rollback in case of error
            trans.rollback()
            print(f"Error updating client_types table: {str(e)}")
            raise
        finally:
            # Close the connection
            conn.close()

if __name__ == '__main__':
    fix_client_types_table()
