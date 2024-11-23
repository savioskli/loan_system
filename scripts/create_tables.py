import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from utils.dynamic_tables import create_or_update_module_table

def create_module_tables():
    app = create_app()
    with app.app_context():
        # Create CLM01 table
        print("Creating table for CLM01...")
        success = create_or_update_module_table('CLM01')
        if success:
            print("Successfully created table for CLM01")
        else:
            print("Failed to create table for CLM01")

if __name__ == '__main__':
    create_module_tables()
