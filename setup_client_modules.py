from flask import Flask
from extensions import db
from models.module import Module, FormField
from models.staff import Staff
from models.role import Role
from datetime import datetime
from data.kenya_locations import KENYA_COUNTIES
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def get_or_create_module(name, code, description, parent_id=None):
    module = Module.query.filter_by(code=code).first()
    if module:
        # Only update if fields are empty
        if not module.name:
            module.name = name
        if not module.description:
            module.description = description
        if not module.parent_id:
            module.parent_id = parent_id
        module.is_active = True
        print(f"Updated existing module: {name} ({code})")
    else:
        module = Module(
            name=name,
            code=code,
            description=description,
            parent_id=parent_id,
            is_active=True
        )
        db.session.add(module)
        print(f"Created new module: {name} ({code})")
    return module

def create_default_field(module_id, field_name, field_label, field_type, field_order=0,
                       field_placeholder=None, is_required=True, options=None, depends_on=None,
                       validation_rules=None):
    """Create a default form field."""
    
    # Check if field already exists
    existing_field = FormField.query.filter_by(module_id=module_id, field_name=field_name).first()
    
    # For county field, always use the complete list from KENYA_COUNTIES
    if field_name == 'county':
        counties = sorted(list(KENYA_COUNTIES.keys()))
        options = json.dumps([{'value': county, 'label': county} for county in counties])
        print(f"Setting up county field with {len(counties)} counties")
    elif options:
        # For other fields, if options is a list, convert to JSON
        if isinstance(options, list):
            if all(isinstance(x, dict) for x in options):
                options = json.dumps(options)
            else:
                options = json.dumps([{'value': x, 'label': x} for x in options])
        elif isinstance(options, str) and not options.startswith('['):
            # If it's a comma-separated string, convert to JSON
            options = json.dumps([{'value': x.strip(), 'label': x.strip()} 
                                for x in options.split(',')])
    
    if existing_field:
        # Update existing field
        existing_field.field_label = field_label
        existing_field.field_type = field_type
        existing_field.field_order = field_order
        existing_field.field_placeholder = field_placeholder
        existing_field.is_required = is_required
        existing_field.options = options
        existing_field.depends_on = depends_on
        existing_field.validation_rules = json.dumps(validation_rules) if validation_rules else None
        db.session.commit()
        
        if field_name == 'county':
            # Verify the options were saved correctly
            saved_options = json.loads(existing_field.options) if existing_field.options else []
            print(f"Updated county field with {len(saved_options)} options")
            if saved_options:
                print("First 5 counties:", [opt['value'] for opt in saved_options[:5]])
        
        return existing_field
    
    # Create new field
    new_field = FormField(
        module_id=module_id,
        field_name=field_name,
        field_label=field_label,
        field_type=field_type,
        field_order=field_order,
        field_placeholder=field_placeholder,
        is_required=is_required,
        options=options,
        depends_on=depends_on,
        validation_rules=json.dumps(validation_rules) if validation_rules else None
    )
    
    db.session.add(new_field)
    db.session.commit()
    
    if field_name == 'county':
        # Verify the options were saved correctly
        saved_options = json.loads(new_field.options) if new_field.options else []
        print(f"Created new county field with {len(saved_options)} options")
        if saved_options:
            print("First 5 counties:", [opt['value'] for opt in saved_options[:5]])
    
    return new_field

def setup_client_modules():
    try:
        # Get the parent Client Management module
        client_mgmt = Module.query.filter_by(code='CLT00').first()
        if not client_mgmt:
            print("Client Management module not found! Please run setup_base_modules.py first.")
            return

        # Create or update modules
        modules = {
            'CLT01': {
                'name': 'New Client Application',
                'description': 'Register new client applications'
            },
            'CLT02': {
                'name': 'Update Client Information',
                'description': 'Update existing client information'
            },
            'CLT03': {
                'name': 'Client Verification',
                'description': 'Verify client information and documents'
            },
            'CLT04': {
                'name': 'Client Documents',
                'description': 'Manage client documents'
            }
        }

        # Create or update modules
        for code, info in modules.items():
            module = get_or_create_module(
                name=info['name'],
                code=code,
                description=info['description'],
                parent_id=client_mgmt.id
            )
            db.session.flush()

            # Only add default fields if the module has no fields
            if code == 'CLT01' and not FormField.query.filter_by(module_id=module.id).first():
                # Add default fields for CLT01
                create_default_field(
                    module.id, 'client_type', 'Client Type', 'select',
                    field_order=1,
                    field_placeholder='Choose Client Type',
                    options=[
                        {'value': 'individual', 'label': 'Individual'},
                        {'value': 'company', 'label': 'Company'},
                        {'value': 'group', 'label': 'Group'},
                        {'value': 'joint_venture', 'label': 'Joint Venture'}
                    ]
                )
                create_default_field(
                    module.id, 'purpose_of_visit', 'Purpose of Visit', 'text',
                    field_order=2,
                    field_placeholder='Loan Inquiry'
                )
                create_default_field(
                    module.id, 'purpose_description', 'Purpose Description', 'textarea',
                    field_order=3
                )
                create_default_field(
                    module.id, 'product', 'Product', 'select',
                    field_order=4,
                    field_placeholder='Choose Product',
                    options=[
                        {'value': 'personal_loan', 'label': 'Personal Loan'},
                        {'value': 'business_loan', 'label': 'Business Loan'},
                        {'value': 'group_loan', 'label': 'Group Loan'},
                        {'value': 'asset_financing', 'label': 'Asset Financing'}
                    ]
                )
                create_default_field(
                    module.id, 'first_name', 'First Name', 'text',
                    field_order=5
                )
                create_default_field(
                    module.id, 'middle_name', 'Middle Name', 'text',
                    field_order=6
                )
                create_default_field(
                    module.id, 'last_name', 'Last Name', 'text',
                    field_order=7
                )
                create_default_field(
                    module.id, 'gender', 'Gender', 'select',
                    field_order=8,
                    options=[
                        {'value': 'male', 'label': 'Male'},
                        {'value': 'female', 'label': 'Female'}
                    ]
                )
                create_default_field(
                    module.id, 'id_type', 'ID Type', 'select',
                    field_order=9,
                    field_placeholder='Choose ID Type',
                    options=[
                        {'value': 'national_id', 'label': 'National ID'},
                        {'value': 'passport', 'label': 'Passport'},
                        {'value': 'company_reg', 'label': 'Company Registration'},
                        {'value': 'alien_id', 'label': 'Alien ID'}
                    ]
                )
                create_default_field(
                    module.id, 'id_number', 'ID Number / Company Registration', 'text',
                    field_order=10
                )
                create_default_field(
                    module.id, 'serial_number', 'Serial Number (for National ID)', 'text',
                    field_order=11
                )
                create_default_field(
                    module.id, 'group_name', 'Group / Company Name / JV Name', 'text',
                    field_order=12
                )
                create_default_field(
                    module.id, 'birth_date', 'Birth Date / Company Registration Date', 'date',
                    field_order=13
                )
                create_default_field(
                    module.id, 'member_count', 'Number of Members / Partners / Directors', 'number',
                    field_order=14,
                    field_placeholder='Enter Number'
                )
                create_default_field(
                    module.id, 'postal_address', 'Postal Address', 'text',
                    field_order=15
                )
                create_default_field(
                    module.id, 'postal_code', 'Postal Code', 'text',
                    field_order=16
                )
                # Delete ALL existing county and sub-county fields
                FormField.query.filter(
                    FormField.module_id == module.id,
                    field_name='county'
                ).delete(synchronize_session='fetch')
                db.session.commit()
                print("Deleted existing county field")

                # Add location fields with complete list of counties
                counties = sorted(list(KENYA_COUNTIES.keys()))
                county_options = [{'value': county, 'label': county} for county in counties]
                
                print(f"Adding {len(counties)} counties to the dropdown")
                
                # Create the county field directly with JSON-encoded options
                county_field = FormField(
                    module_id=module.id,
                    field_name='county',
                    field_label='County',
                    field_type='select',
                    field_order=17,
                    field_placeholder='Select County',
                    is_required=True,
                    options=json.dumps(county_options)  # Properly encode as JSON
                )
                db.session.add(county_field)
                db.session.commit()
                
                # Verify the options were saved correctly
                saved_field = FormField.query.filter_by(module_id=module.id, field_name='county').first()
                if saved_field and saved_field.options:
                    try:
                        saved_options = json.loads(saved_field.options)
                        print(f"Successfully saved {len(saved_options)} counties to database")
                        print("First 5 counties:", [opt['value'] for opt in saved_options[:5]])
                    except json.JSONDecodeError:
                        print("Warning: Counties not saved in correct JSON format")
                        print("Current options:", saved_field.options)

                # Create the sub-county field
                FormField.query.filter(
                    FormField.module_id == module.id,
                    field_name='sub_county'
                ).delete(synchronize_session='fetch')
                db.session.commit()
                
                sub_county_field = FormField(
                    module_id=module.id,
                    field_name='sub_county',
                    field_label='Sub County',
                    field_type='select',
                    field_order=18,
                    field_placeholder='Select Sub County',
                    is_required=True,
                    options=json.dumps([]),  # Empty list for now, will be populated dynamically
                    depends_on='county'
                )
                db.session.add(sub_county_field)
                db.session.commit()
                
                create_default_field(
                    module.id, 'mobile_phone', 'Mobile Phone', 'text',
                    field_order=19,
                    field_placeholder='254-###-######',
                    validation_rules={'pattern': '^254-[0-9]{3}-[0-9]{6}$'},
                    validation_text='Format: 254-###-######'
                )
                create_default_field(
                    module.id, 'email', 'Email Address', 'text',
                    field_order=20,
                    validation_rules={'type': 'email'},
                    validation_text='Enter a valid email address'
                )
                create_default_field(
                    module.id, 'ward', 'Ward', 'text',
                    field_order=21
                )
                create_default_field(
                    module.id, 'village', 'Village', 'text',
                    field_order=22
                )
                create_default_field(
                    module.id, 'trade_center', 'Nearest Trade Center', 'text',
                    field_order=23
                )
            elif code == 'CLT02' and not FormField.query.filter_by(module_id=module.id).first():
                create_default_field(
                    module.id, 'client_id', 'Client ID', 'text',
                    field_order=1,
                    field_placeholder='Enter client ID'
                )
                create_default_field(
                    module.id, 'update_type', 'Information to Update', 'select',
                    field_order=2,
                    options=[
                        {'value': 'contact', 'label': 'Contact Details'},
                        {'value': 'address', 'label': 'Address'},
                        {'value': 'employment', 'label': 'Employment Details'},
                        {'value': 'bank', 'label': 'Bank Details'}
                    ]
                )
                create_default_field(
                    module.id, 'new_value', 'New Information', 'textarea',
                    field_order=3,
                    field_placeholder='Enter the new information'
                )
                create_default_field(
                    module.id, 'reason', 'Reason for Update', 'textarea',
                    field_order=4,
                    field_placeholder='Explain why this information needs to be updated'
                )
            elif code == 'CLT03' and not FormField.query.filter_by(module_id=module.id).first():
                create_default_field(
                    module.id, 'client_id', 'Client ID', 'text',
                    field_order=1,
                    field_placeholder='Enter client ID'
                )
                create_default_field(
                    module.id, 'verification_type', 'Verification Type', 'select',
                    field_order=2,
                    options=['Identity Verification', 'Address Verification', 'Income Verification', 'Employment Verification']
                )
                create_default_field(
                    module.id, 'verification_method', 'Verification Method', 'select',
                    field_order=3,
                    options=['Document Review', 'Phone Call', 'Site Visit', 'Third Party Verification']
                )
                create_default_field(
                    module.id, 'verification_notes', 'Verification Notes', 'textarea',
                    field_order=4,
                    field_placeholder='Enter detailed notes about the verification process'
                )
            elif code == 'CLT04' and not FormField.query.filter_by(module_id=module.id).first():
                create_default_field(
                    module.id, 'client_id', 'Client ID', 'text',
                    field_order=1,
                    field_placeholder='Enter client ID'
                )
                create_default_field(
                    module.id, 'document_type', 'Document Type', 'select',
                    field_order=2,
                    options=['ID Document', 'Proof of Address', 'Bank Statements', 'Payslips', 'Tax Returns', 'Employment Contract']
                )
                create_default_field(
                    module.id, 'document_file', 'Upload Document', 'file',
                    field_order=3,
                    validation_rules={'accept': '.pdf,.jpg,.png,.doc,.docx'}
                )
                create_default_field(
                    module.id, 'document_description', 'Document Description', 'textarea',
                    field_order=4,
                    field_placeholder='Enter a description of the document'
                )
                create_default_field(
                    module.id, 'expiry_date', 'Document Expiry Date', 'date',
                    field_order=5
                )

        db.session.commit()
        print("Client management modules and form fields updated successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {str(e)}")
        print("Changes have been rolled back.")

if __name__ == '__main__':
    with app.app_context():
        setup_client_modules()
