from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models.module import Module, FormField
from models.product import Product
from models.client_type import ClientType
from extensions import db
import os
import json
from werkzeug.utils import secure_filename
from data.kenya_locations import KENYA_COUNTIES
from sqlalchemy import and_

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get statistics for the dashboard
    pending_clients = 0  # TODO: Implement client count logic
    pending_loans = 0    # TODO: Implement loan count logic
    approved_loans = 0   # TODO: Implement approved loans count
    rejected_loans = 0   # TODO: Implement rejected loans count
    portfolio_value = 0  # TODO: Implement portfolio value calculation
    
    # Get client management modules (only child modules)
    client_modules = Module.query.join(FormField).filter(
        and_(
            Module.code.like('CLM%'),
            Module.code != 'CLM00',  # Exclude parent module
            Module.is_active == True
        )
    ).group_by(Module.id).order_by(Module.code).all()
    
    # Get loan management modules (only child modules)
    loan_modules = Module.query.join(FormField).filter(
        and_(
            Module.code.like('LN%'),
            ~Module.code.endswith('00'),  # Exclude parent modules
            Module.is_active == True
        )
    ).group_by(Module.id).order_by(Module.code).all()
    
    # Get parent modules for organization
    client_parent = Module.query.filter_by(code='CLM00').first()
    loan_parent = Module.query.filter(
        and_(
            Module.code.like('LN%'),
            Module.code.endswith('00')
        )
    ).first()
    
    return render_template('user/dashboard.html',
                         pending_clients=pending_clients,
                         pending_loans=pending_loans,
                         approved_loans=approved_loans,
                         rejected_loans=rejected_loans,
                         portfolio_value=portfolio_value,
                         client_modules=client_modules,
                         loan_modules=loan_modules,
                         client_parent=client_parent,
                         loan_parent=loan_parent)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@user_bp.route('/dynamic_form/<module_code>', methods=['GET', 'POST'])
@login_required
def dynamic_form(module_code):
    try:
        # Get the module
        module = Module.query.filter_by(code=module_code).first_or_404()
        
        if request.method == 'POST':
            # Create a dictionary to store form data
            form_data = {}
            
            # Get form fields for validation
            form_fields = FormField.query.filter_by(module_id=module.id).all()
            field_dict = {field.field_name: field for field in form_fields}
            
            # Get selected client type
            client_type_id = request.form.get('client_type')
            
            # Process each form field
            for field_name, field in field_dict.items():
                # Check client type restrictions
                if field.client_type_restrictions and client_type_id:
                    if int(client_type_id) not in field.client_type_restrictions:
                        continue  # Skip fields not allowed for this client type
                
                if field.field_type == 'file':
                    # Handle file upload
                    if field_name in request.files:
                        file = request.files[field_name]
                        if file and file.filename:
                            # Get allowed extensions from validation rules
                            allowed_extensions = set()
                            if field.validation_rules and 'accept' in field.validation_rules:
                                extensions = field.validation_rules['accept'].split(',')
                                allowed_extensions = {ext.strip('.') for ext in extensions}
                            
                            if allowed_file(file.filename, allowed_extensions):
                                filename = secure_filename(file.filename)
                                # Create upload directory if it doesn't exist
                                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], module_code)
                                os.makedirs(upload_dir, exist_ok=True)
                                
                                # Save the file
                                file_path = os.path.join(upload_dir, filename)
                                file.save(file_path)
                                form_data[field_name] = filename
                            else:
                                return jsonify({
                                    'success': False,
                                    'message': f'Invalid file type for {field.field_label}. Allowed types: {", ".join(allowed_extensions)}'
                                })
                    elif field.is_required:
                        return jsonify({
                            'success': False,
                            'message': f'Required file missing: {field.field_label}'
                        })
                else:
                    # Handle other form fields
                    value = request.form.get(field_name)
                    if field.is_required and not value:
                        return jsonify({
                            'success': False,
                            'message': f'Required field missing: {field.field_label}'
                        })
                    form_data[field_name] = value
            
            try:
                # TODO: Save form data to appropriate table based on module_code
                # For now, just log the form data
                print(f"Form data for module {module_code}:", json.dumps(form_data, indent=2))
                
                return jsonify({
                    'success': True,
                    'message': 'Form submitted successfully',
                    'redirect': url_for('user.dashboard')
                })
                
            except Exception as e:
                print(f"Error saving form data: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Error saving form data'
                })
        
        else:
            # Get form fields
            form_fields = FormField.query.filter_by(module_id=module.id).order_by(FormField.field_order).all()
            
            # Process fields
            for field in form_fields:
                if field.field_type == 'select':
                    if field.field_name == 'county' or field.field_name == 'postal_town':
                        # For county and postal town fields, use the complete list from KENYA_COUNTIES
                        counties = sorted(list(KENYA_COUNTIES.keys()))
                        field.options = [{'value': county, 'label': county} for county in counties]
                    elif field.field_name == 'product':
                        # For product field, get all active products
                        products = Product.query.filter_by(status='Active').all()
                        field.options = [{'value': str(product.id), 'label': product.name} for product in products]
                    elif field.field_name == 'client_type':
                        # For client type field, get all active client types
                        client_types = ClientType.query.filter_by(status=True).all()
                        field.options = [{'value': str(client_type.id), 'label': client_type.client_name} for client_type in client_types]
            
            return render_template('user/dynamic_form.html', module=module, form_fields=form_fields)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        })

@user_bp.route('/get_sub_counties/<county>')
@login_required
def get_sub_counties(county):
    """Get sub-counties for a given county."""
    try:
        county = county.strip()
        if county in KENYA_COUNTIES:
            sub_counties = KENYA_COUNTIES[county]
            return jsonify(sub_counties)
        else:
            print(f"County not found: {county}")
            return jsonify([])
    except Exception as e:
        print(f"Error getting sub-counties for {county}: {str(e)}")
        return jsonify([])

@user_bp.route('/reports')
@login_required
def reports():
    # TODO: Implement reports page
    return render_template('user/reports.html')
