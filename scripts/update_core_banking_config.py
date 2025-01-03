"""
Script to update core banking configurations with database and table mappings
"""
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from flask import Flask
from extensions import db

# Import all models to ensure they are registered with SQLAlchemy
from models.core_banking import CoreBankingSystem
from models.staff import Staff
from models.role import Role
from models.module import Module
from models.client import Client
from models.client_type import ClientType
from models.form_section import FormSection
from models.form_submission import FormSubmission
from models.product import Product
from models.calendar_event import CalendarEvent
from models.correspondence import Correspondence
from models.guarantor import Guarantor

import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/loan_system?auth_plugin=mysql_native_password'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def update_core_banking_configs():
    with app.app_context():
        # Get all core banking systems
        systems = CoreBankingSystem.query.all()
        
        if not systems:
            print("No core banking systems found")
            return
        
        for system in systems:
            try:
                # Connect and list available databases
                print(f"\nUpdating configuration for {system.name}...")
                
                # Get database connection
                connection = system.get_database_connection()
                print("✓ Database connection successful")
                
                # List available databases
                databases = system.list_databases()
                print(f"Available databases: {', '.join(databases)}")
                
                # Select database (example: sacco_db)
                database_name = input(f"\nEnter database name to use [{', '.join(databases)}]: ").strip()
                if not database_name:
                    print("No database selected, skipping...")
                    continue
                
                system.select_database(database_name)
                print(f"✓ Selected database: {database_name}")
                
                # List available tables
                tables = system.list_tables()
                print(f"\nAvailable tables: {', '.join(tables)}")
                
                # Configure table mappings
                table_configs = {}
                while True:
                    table_name = input("\nEnter table name to configure (or press Enter to finish): ").strip()
                    if not table_name:
                        break
                        
                    if table_name not in tables:
                        print(f"Table '{table_name}' not found in database")
                        continue
                    
                    # Get table schema
                    schema = system.get_table_schema(table_name)
                    print(f"\nTable schema for {table_name}:")
                    for field in schema:
                        print(f"- {field['name']} ({field['type']})")
                    
                    # Get key field
                    key_field = input("\nEnter key field name: ").strip()
                    if not key_field or key_field not in [f['name'] for f in schema]:
                        print("Invalid key field")
                        continue
                    
                    # Get field mappings
                    print("\nEnter field mappings (source_field:target_field), one per line (press Enter twice to finish):")
                    mappings = {}
                    while True:
                        mapping = input().strip()
                        if not mapping:
                            break
                            
                        try:
                            source, target = mapping.split(':')
                            source = source.strip()
                            target = target.strip()
                            
                            if source not in [f['name'] for f in schema]:
                                print(f"Field '{source}' not found in table schema")
                                continue
                                
                            mappings[source] = target
                            
                        except ValueError:
                            print("Invalid mapping format. Use source_field:target_field")
                            continue
                    
                    table_configs[table_name] = {
                        'name': table_name,
                        'key_field': key_field,
                        'mappings': mappings
                    }
                
                if table_configs:
                    system.configure_tables(table_configs)
                    print(f"\n✓ Successfully configured {len(table_configs)} tables")
                    print("\nTable configurations:")
                    print(json.dumps(table_configs, indent=2))
                
            except Exception as e:
                print(f"Error updating {system.name}: {str(e)}")
                continue

if __name__ == '__main__':
    update_core_banking_configs()
