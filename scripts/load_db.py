import json
import os
import sys
from datetime import datetime

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
        with open(dump_file, 'r') as f:
            dump = json.load(f)
        
        # Get all tables and their columns
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        
        # Clear existing data (in reverse order to handle foreign keys)
        for table_name in reversed(list(metadata.tables.keys())):
            print(f"Clearing table: {table_name}")
            db.session.execute(metadata.tables[table_name].delete())
        
        # Load data for each table
        for table_name, table in metadata.tables.items():
            if table_name in dump['data']:
                print(f"Loading data into table: {table_name}")
                for row_data in dump['data'][table_name]:
                    # Convert string values back to their proper types
                    for column in table.columns:
                        if column.name in row_data:
                            row_data[column.name] = parse_value(row_data[column.name], column.type)
                    
                    # Insert the row
                    db.session.execute(table.insert().values(**row_data))
        
        # Commit all changes
        db.session.commit()
        print("Database load completed successfully!")

if __name__ == '__main__':
    load_data()
