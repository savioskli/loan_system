from flask import Flask
from extensions import db
from models.module import Module
from models.form_field import FormField
from models.staff import Staff
from models.role import Role
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_base_modules():
    try:
        # Create parent modules
        client_mgmt = Module(
            name='Client Management',
            code='CLT00',  # Using a clear prefix for client management
            description='Client-related modules and forms',
            is_active=True
        )
        
        loan_mgmt = Module(
            name='Loan Management',
            code='LN00',   # Using a clear prefix for loan management
            description='Loan-related modules and forms',
            is_active=True
        )
        
        # Add to session
        db.session.add(client_mgmt)
        db.session.add(loan_mgmt)
        db.session.commit()
        
        print("Base modules created successfully:")
        print(f"1. {client_mgmt.name} (Code: {client_mgmt.code})")
        print(f"2. {loan_mgmt.name} (Code: {loan_mgmt.code})")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {str(e)}")
        print("Changes have been rolled back.")

with app.app_context():
    create_base_modules()
