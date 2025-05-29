from app import create_app
from models.module import Module
from models.form_field import FormField
from extensions import db

def add_form_field(module_id, field_name, field_label, field_type, is_required=False, field_placeholder='', options=None, max_order=0):
    field = FormField(
        module_id=module_id,
        field_name=field_name.lower().replace(' ', '_'),
        field_label=field_label,
        field_placeholder=field_placeholder,
        field_type=field_type,
        is_required=is_required,
        field_order=max_order + 1,
        options=options
    )
    return field

app = create_app()
with app.app_context():
    module = Module.query.filter_by(code='CLM02').first()
    if not module:
        print("CLM02 module not found!")
        exit(1)
    
    # Get the current max order
    max_order = db.session.query(db.func.max(FormField.field_order)).filter_by(module_id=module.id).scalar() or 0
    
    # Family Information Fields
    family_fields = [
        ('marital_status', 'Marital Status', 'select', True, '', [
            {'label': 'Single', 'value': 'single'},
            {'label': 'Married', 'value': 'married'},
            {'label': 'Divorced', 'value': 'divorced'},
            {'label': 'Widowed', 'value': 'widowed'}
        ]),
        ('spouse_name', 'Spouse Name', 'text', False),
        ('spouse_id_type', 'ID Type', 'select', False, '', [
            {'label': 'National ID', 'value': 'national_id'},
            {'label': 'Passport', 'value': 'passport'},
            {'label': 'Military ID', 'value': 'military_id'},
            {'label': 'Alien ID', 'value': 'alien_id'}
        ]),
        ('spouse_id_number', 'ID Number / Passport', 'text', False),
        ('children_below_12', 'Children (Below 12 Yrs)', 'number', False, '1'),
        ('children_13_to_18', 'Children (Between 13 to 18 Yrs)', 'number', False, '1'),
        ('children_above_18', 'Children (Above 18 Yrs)', 'number', False, '1'),
        ('dependants', 'Dependants', 'number', False, '1')
    ]

    # Next of Kin Fields
    nok_fields = [
        ('nok_first_name', 'First Name', 'text', True),
        ('nok_middle_name', 'Middle Name', 'text', False),
        ('nok_last_name', 'Last Name', 'text', True),
        ('nok_id_type', 'ID Type', 'select', True, '', [
            {'label': 'National ID', 'value': 'national_id'},
            {'label': 'Passport', 'value': 'passport'},
            {'label': 'Military ID', 'value': 'military_id'},
            {'label': 'Alien ID', 'value': 'alien_id'}
        ]),
        ('nok_id_number', 'ID Number / Passport', 'text', True),
        ('nok_postal_address', 'Postal Address', 'text', True),
        ('nok_postal_code', 'Postal Code', 'text', True),
        ('nok_postal_town', 'Postal Town', 'select', False, 'Choose Town'),
        ('nok_mobile_phone', 'Mobile Phone', 'tel', True, '254_________')
    ]

    # Occupation Fields
    occupation_fields = [
        ('occupation', 'Occupation', 'select', True, '', [
            {'label': 'Employed', 'value': 'employed'},
            {'label': 'Self Employed', 'value': 'self_employed'},
            {'label': 'Business Owner', 'value': 'business_owner'},
            {'label': 'Retired', 'value': 'retired'},
            {'label': 'Student', 'value': 'student'},
            {'label': 'Other', 'value': 'other'}
        ]),
        ('occupation_type', 'Occupation Type', 'select', True, '', [
            {'label': 'Full Time', 'value': 'full_time'},
            {'label': 'Part Time', 'value': 'part_time'},
            {'label': 'Contract', 'value': 'contract'},
            {'label': 'Casual', 'value': 'casual'}
        ]),
        ('employer_name', 'Name of Employer / Business', 'text', False),
        ('business_address', 'Address / Location', 'text', False),
        ('business_phone', 'Phone Number', 'tel', False),
        ('business_email', 'Email Address', 'email', False),
        ('professional_membership', 'Professional Membership', 'select', False, '', [
            {'label': 'None', 'value': 'none'},
            {'label': 'Engineering', 'value': 'engineering'},
            {'label': 'Medical', 'value': 'medical'},
            {'label': 'Legal', 'value': 'legal'},
            {'label': 'Accounting', 'value': 'accounting'},
            {'label': 'Other', 'value': 'other'}
        ]),
        ('club_membership', 'Club Membership', 'select', False, '', [
            {'label': 'None', 'value': 'none'},
            {'label': 'Sports Club', 'value': 'sports'},
            {'label': 'Social Club', 'value': 'social'},
            {'label': 'Professional Club', 'value': 'professional'},
            {'label': 'Other', 'value': 'other'}
        ])
    ]

    try:
        # Add all fields
        all_fields = []
        
        print("\nAdding Family Information fields...")
        for field_data in family_fields:
            max_order += 1
            field = add_form_field(module.id, *field_data, max_order=max_order)
            all_fields.append(field)
            print(f"Added field: {field.field_label}")

        print("\nAdding Next of Kin fields...")
        for field_data in nok_fields:
            max_order += 1
            field = add_form_field(module.id, *field_data, max_order=max_order)
            all_fields.append(field)
            print(f"Added field: {field.field_label}")

        print("\nAdding Occupation fields...")
        for field_data in occupation_fields:
            max_order += 1
            field = add_form_field(module.id, *field_data, max_order=max_order)
            all_fields.append(field)
            print(f"Added field: {field.field_label}")

        # Add all fields to the session
        db.session.add_all(all_fields)
        
        # Commit the changes
        db.session.commit()
        print("\nSuccessfully added all form fields!")
        
        # Update the module's table schema
        from utils.dynamic_tables import create_or_update_module_table
        if create_or_update_module_table('CLM02'):
            print("Successfully updated table schema!")
        else:
            print("Failed to update table schema!")

    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
