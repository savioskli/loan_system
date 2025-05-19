#!/usr/bin/env python3
"""
Script to update the system name in the database.
"""
import os
import sys
from flask import Flask

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask and SQLAlchemy extensions
from extensions import db

# Import models after db initialization to avoid circular imports
from models.system_settings import SystemSettings

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/loan_system?auth_plugin=mysql_native_password'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Import models after db initialization to avoid circular imports
    with app.app_context():
        # Import models here to avoid circular imports
        from models.role import Role
        from models.branch import Branch
        from models.staff import Staff
        
        # Create tables if they don't exist
        db.create_all()
    
    return app

def update_system_name():
    """Update the system name in the database."""
    app = create_app()
    
    with app.app_context():
        try:
            # Update the system name
            SystemSettings.set_setting('system_name', 'Loan Origination, Appraisal & Post Disbursement System', 1)
            print("System name updated successfully!")
            
        except Exception as e:
            print(f"Error updating system name: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    if update_system_name():
        print("System name has been updated to 'Loan Origination, Appraisal & Post Disbursement System'.")
    else:
        print("Failed to update system name.")
