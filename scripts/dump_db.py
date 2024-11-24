from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.schema import CreateTable
import json
import os
import sys
import datetime
from decimal import Decimal

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models import *  # This will import all your models
from extensions import db
from app import create_app  # Import the create_app function

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def dump_table_schema(table):
    """Returns the CREATE TABLE statement for a table"""
    return str(CreateTable(table).compile(db.engine))

def dump_table_data(table):
    """Returns all data from a table as a list of dictionaries"""
    data = []
    result = db.session.query(table).all()
    for row in result:
        row_dict = {}
        for column in table.columns:
            value = getattr(row, column.name)
            row_dict[column.name] = value
        data.append(row_dict)
    return data

def main():
    app = create_app()
    with app.app_context():
        dump = {
            'schema': {},
            'data': {}
        }
        
        # Get all tables
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        
        # Dump schema and data for each table
        for table_name, table in metadata.tables.items():
            print(f"Dumping table: {table_name}")
            dump['schema'][table_name] = dump_table_schema(table)
            dump['data'][table_name] = dump_table_data(table)
        
        # Write to file using custom JSON encoder
        with open('database_dump.json', 'w') as f:
            json.dump(dump, f, indent=2, cls=JSONEncoder)
        
        print("Database dump completed successfully!")

if __name__ == '__main__':
    main()
