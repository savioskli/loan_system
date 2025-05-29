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

def add_child_module(parent_code, child_name, child_code, description):
    try:
        # Find parent module
        parent = Module.query.filter_by(code=parent_code).first()
        if not parent:
            print(f"Parent module with code {parent_code} not found!")
            return
        
        # Create child module
        child = Module(
            name=child_name,
            code=child_code,
            description=description,
            parent_id=parent.id,
            is_active=True
        )
        
        # Add to session
        db.session.add(child)
        db.session.commit()
        
        print(f"Child module created successfully under {parent.name}:")
        print(f"Name: {child.name}")
        print(f"Code: {child.code}")
        print(f"Parent: {parent.name} (Code: {parent.code})")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {str(e)}")
        print("Changes have been rolled back.")

with app.app_context():
    # Add Prospect Registration under Client Management
    add_child_module(
        parent_code='CLT00',
        child_name='Prospect Registration',
        child_code='CLT01',  # Using parent prefix + incremental number
        description='Module for registering new client prospects'
    )

    # Add modules under Client Management (CLT00)
    add_child_module(
        parent_code='CLT00',
        child_name='Client Registration',
        child_code='CLT02',
        description='Module for registering approved clients'
    )
    
    add_child_module(
        parent_code='CLT00',
        child_name='Client Profile Update',
        child_code='CLT03',
        description='Module for updating client information'
    )
    
    # Add modules under Loan Management (LN00)
    add_child_module(
        parent_code='LN00',
        child_name='Loan Application',
        child_code='LN01',
        description='Module for new loan applications'
    )
    
    add_child_module(
        parent_code='LN00',
        child_name='Loan Assessment',
        child_code='LN02',
        description='Module for loan assessment and approval'
    )
    
    add_child_module(
        parent_code='LN00',
        child_name='Loan Disbursement',
        child_code='LN03',
        description='Module for loan disbursement processing'
    )
