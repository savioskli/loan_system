from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models.module import Module, FormField
from extensions import db
import os
import json
from werkzeug.utils import secure_filename
from data.kenya_locations import KENYA_COUNTIES

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
    
    # Get client management modules
    client_mgmt = Module.query.filter_by(code='CLT00').first()
    client_modules = []
    if client_mgmt:
        client_modules = Module.query.filter(
            Module.code.like('CLT%'),
            Module.code != 'CLT00',
            Module.is_active == True
        ).order_by(Module.code).all()
    
    return render_template('user/dashboard.html',
                         pending_clients=pending_clients,
                         pending_loans=pending_loans,
                         approved_loans=approved_loans,
                         rejected_loans=rejected_loans,
                         portfolio_value=portfolio_value,
                         client_modules=client_modules)

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
            
            # Process each form field
            for field_name, field in field_dict.items():
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
                    if field.field_name == 'county':
                        # For county field, always use the complete list from KENYA_COUNTIES
                        counties = sorted(list(KENYA_COUNTIES.keys()))
                        field.options = [{'value': county, 'label': county} for county in counties]
                    elif field.options:
                        try:
                            if isinstance(field.options, str):
                                field.options = json.loads(field.options)
                        except json.JSONDecodeError:
                            # If it's a comma-separated string, convert to list of dicts
                            options = [x.strip() for x in field.options.split(',')]
                            field.options = [{'value': opt, 'label': opt} for opt in options]
            
            return render_template('user/dynamic_form.html', 
                                module=module,
                                form_fields=form_fields)
                             
    except Exception as e:
        print(f"Error in dynamic_form route: {str(e)}")
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
