import json
import os
import sys
from datetime import datetime
from sqlalchemy import MetaData, text

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models import *  # This will import all your models
from extensions import db
from app import create_app  # Import the create_app function

def parse_value(value, column_type):
    """Convert string values back to their proper Python types"""
    if value is None:
        return None
    
    type_name = str(column_type).lower()
    if 'datetime' in type_name and isinstance(value, str):
        return datetime.fromisoformat(value)
    elif 'boolean' in type_name and isinstance(value, str):
        return value.lower() == 'true'
    
    return value

def load_data(dump_file='database_dump.json'):
    """Load data from the dump file into the database"""
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        with open(dump_file, 'r') as f:
            dump = json.load(f)
        
        # Get all tables and their columns
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        
        # Clear existing data in the correct order to handle foreign key constraints
        tables_in_order = [
            'activity_logs',
            'form_data_clm01',
            'form_data_clm02',
            'form_fields',
            'form_sections',
            'clients',
            'client_types',
            'products',
            'modules',
            'staff',
            'roles',
            'branches',
            'system_settings',
            'alembic_version'
        ]
        
        # Disable foreign key checks
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        
        # Clear existing data
        for table_name in tables_in_order:
            if table_name in metadata.tables:
                print(f"Clearing table: {table_name}")
                db.session.execute(metadata.tables[table_name].delete())
        
        # Re-enable foreign key checks
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        
        # Load data for each table in the correct order (reverse of deletion order)
        for table_name in reversed(tables_in_order):
            if table_name in metadata.tables and table_name in dump['data']:
                print(f"Loading data into table: {table_name}")
                for row_data in dump['data'][table_name]:
                    # Convert string values back to their proper types
                    for column in metadata.tables[table_name].columns:
                        if column.name in row_data:
                            row_data[column.name] = parse_value(row_data[column.name], column.type)
                    
                    # Insert the row
                    db.session.execute(metadata.tables[table_name].insert().values(**row_data))
        
        # Commit all changes
        db.session.commit()
        print("Database loaded successfully!")

if __name__ == '__main__':
    load_data()
