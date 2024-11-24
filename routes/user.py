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
from sqlalchemy import and_, or_
from datetime import datetime
from sqlalchemy import Table, MetaData
from flask_wtf import FlaskForm
import traceback
from models.staff import Staff  # Import Staff model

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
    # Create a dynamic form with CSRF protection at the start
    class DynamicForm(FlaskForm):
        pass
    form = DynamicForm()
    
    try:
        print(f"\n=== Dynamic Form Access ===")
        print(f"Module Code: {module_code}")
        print(f"Method: {request.method}")
        print(f"User: {current_user}")
        
        # Get the module
        module = Module.query.filter_by(code=module_code).first_or_404()
        print(f"Found module: {module.name} (ID: {module.id})")
        
        # Get form fields
        form_fields = FormField.query.filter_by(module_id=module.id).order_by(FormField.field_order).all()
        
        # Create field dictionary for easy lookup
        field_dict = {field.field_name: field for field in form_fields}
        
        # Pre-populate form data if provided in URL parameters
        form_data = {}
        for field in form_fields:
            value = request.args.get(field.field_name)
            if value:
                form_data[field.field_name] = value
        
        # Store prospect_id if provided
        prospect_id = request.args.get('prospect_id')
        if prospect_id:
            form_data['prospect_id'] = prospect_id
        
        # Populate options for select fields
        for field in form_fields:
            if field.field_type == 'select':
                print(f"\nProcessing select field: {field.field_name}")
                if field.field_name == 'county' or field.field_name == 'postal_town':
                    # For county and postal town fields, use predefined list of counties
                    field.options = [{'value': county, 'label': county} for county in KENYA_COUNTIES]
                    print(f"Added {len(field.options)} county/postal town options")
                elif field.field_name == 'client_type':
                    # For client type field, get active client types from database
                    client_types = ClientType.query.filter_by(status=True).all()
                    field.options = [{'value': str(ct.id), 'label': ct.client_name} for ct in client_types]
                    print(f"Added {len(field.options)} client type options")
                elif field.field_name == 'sub_county':
                    # Sub-county will be populated via AJAX
                    field.options = []
                elif field.field_name == 'product':
                    # For product field, get all active products
                    products = Product.query.filter_by(status='Active').all()
                    field.options = [{'value': str(product.id), 'label': product.name} for product in products]
                    print(f"Added {len(field.options)} product options")
                    print(f"Product options: {field.options}")
                elif field.options:
                    # Use predefined options from the database
                    print(f"Using predefined options: {field.options}")
                else:
                    field.options = []
                    print(f"No options available for field: {field.field_name}")
        
        print(f"\nFound {len(form_fields)} form fields:")
        for field in form_fields:
            print(f"\nField: {field.field_name}")
            print(f"- Type: {field.field_type}")
            print(f"- Required: {field.is_required}")
            print(f"- Order: {field.field_order}")
            if field.client_type_restrictions:
                print(f"- Client Type Restrictions: {field.client_type_restrictions}")
            if field.options:
                print(f"- Options: {field.options}")
            if field.validation_rules:
                print(f"- Validation Rules: {field.validation_rules}")
        
        if request.method == 'POST':
            if not form.validate():
                print("Form validation failed")
                flash('Form validation failed. Please try again.', 'error')
                return render_template('user/dynamic_form.html', 
                                    module=module, 
                                    form_fields=form_fields,
                                    form=form,
                                    form_data=request.form)
            
            # Get selected client type
            client_type_id = request.form.get('client_type')
            print(f"Received client_type_id from form: {client_type_id}")

            if not client_type_id:
                flash('Client type is required', 'error')
                print("No client_type_id provided in form")
                return render_template('user/dynamic_form.html',
                                    module=module,
                                    form_fields=form_fields,
                                    form=form,
                                    form_data=request.form)

            try:
                client_type = ClientType.query.filter_by(id=client_type_id, status=True).first()
                if not client_type:
                    flash('Selected client type is not valid or inactive', 'error')
                    print(f"No active client type found for id: {client_type_id}")
                    return render_template('user/dynamic_form.html',
                                        module=module,
                                        form_fields=form_fields,
                                        form=form,
                                        form_data=request.form)
                print(f"Found client type: {client_type.client_name} (ID: {client_type.id})")
            except Exception as e:
                print(f"Error retrieving client type: {str(e)}")
                flash('Error processing client type', 'error')
                return render_template('user/dynamic_form.html',
                                    module=module,
                                    form_fields=form_fields,
                                    form=form,
                                    form_data=request.form)
            
            # Validate required fields
            missing_fields = []
            for field in form_fields:
                if field.is_required:
                    # Skip validation if field is restricted to certain client types and current client type is not in the list
                    if field.client_type_restrictions and client_type_id:
                        if client_type_id not in field.client_type_restrictions:
                            continue
                    
                    field_value = request.form.get(field.field_name)
                    if not field_value and field.field_type != 'file':
                        missing_fields.append(field.field_label)
                    elif field.field_type == 'file':
                        if field.field_name not in request.files or not request.files[field.field_name].filename:
                            missing_fields.append(field.field_label)
            
            if missing_fields:
                flash(f"Please fill in the following required fields: {', '.join(missing_fields)}", 'error')
                return render_template('user/dynamic_form.html', 
                                    module=module, 
                                    form_fields=form_fields,
                                    form=form,
                                    form_data=request.form)
            
            # Process form data
            form_data = {}
            files_to_save = {}
            
            for field_name, field_value in request.form.items():
                if field_name in field_dict:
                    field = field_dict[field_name]
                    
                    # Skip processing if field is restricted to certain client types and current client type is not in the list
                    if field.client_type_restrictions and client_type_id:
                        if client_type_id not in field.client_type_restrictions:
                            continue
                    
                    # Validate field value based on field type
                    if field.field_type == 'number':
                        try:
                            float(field_value)
                        except ValueError:
                            flash(f"Invalid number format for field: {field.field_label}", 'error')
                            return render_template('user/dynamic_form.html', 
                                                module=module, 
                                                form_fields=form_fields,
                                                form=form,
                                                form_data=request.form)
                    
                    form_data[field_name] = field_value
            
            # Process file uploads
            for field in form_fields:
                if field.field_type == 'file' and field.field_name in request.files:
                    file = request.files[field.field_name]
                    
                    # Skip processing if field is restricted to certain client types and current client type is not in the list
                    if field.client_type_restrictions and client_type_id:
                        if client_type_id not in field.client_type_restrictions:
                            continue
                    
                    if file and file.filename:
                        # Get allowed extensions from validation rules
                        allowed_extensions = set()
                        if field.validation_rules and 'allowed_extensions' in field.validation_rules:
                            allowed_extensions = set(field.validation_rules['allowed_extensions'])
                        
                        if not allowed_file(file.filename, allowed_extensions):
                            flash(f'Invalid file type for {field.field_label}. Allowed types: {", ".join(allowed_extensions)}', 'error')
                            return render_template('user/dynamic_form.html', 
                                                module=module, 
                                                form_fields=form_fields,
                                                form=form,
                                                form_data=request.form)
                        
                        # Secure the filename and save the file
                        filename = secure_filename(file.filename)
                        files_to_save[field.field_name] = (file, filename)
            
            try:
                # Create dynamic table name based on module code
                table_name = f"form_data_{module.code.lower()}"
                print(f"\n=== Form Submission for {module.code} ===")
                print(f"Table name: {table_name}")
                
                # Get the table metadata and reflect the table
                metadata = MetaData()
                try:
                    metadata.reflect(bind=db.engine, only=[table_name])
                    print(f"Successfully reflected metadata for table {table_name}")
                except Exception as reflect_error:
                    print(f"Error reflecting table metadata: {str(reflect_error)}")
                    print(f"Full traceback: {traceback.format_exc()}")
                    raise ValueError(f"Failed to reflect table {table_name}: {str(reflect_error)}")

                if table_name not in metadata.tables:
                    print(f"Table {table_name} not found in metadata after reflection")
                    raise ValueError(f"Table {table_name} not found in database")
                
                dynamic_table = metadata.tables[table_name]
                print(f"Got dynamic table object")
                
                # Verify required columns exist
                required_columns = {'user_id', 'submission_date', 'status', 'client_type_id'}
                missing_columns = required_columns - set(column.name for column in dynamic_table.columns)
                if missing_columns:
                    print(f"Missing required columns in table {table_name}: {missing_columns}")
                    raise ValueError(f"Table {table_name} is missing required columns: {missing_columns}")
                
                # Filter record to only include existing columns and respect client type restrictions
                valid_columns = set(column.name for column in dynamic_table.columns)
                print(f"Valid columns in table: {valid_columns}")
                
                filtered_record = {}
                for field_name, field_value in form_data.items():
                    # Skip if field is not in the table
                    if field_name not in valid_columns:
                        continue
                        
                    # Skip empty values for non-required fields
                    if not field_value and field_name in field_dict:
                        field = field_dict[field_name]
                        if not field.is_required:
                            continue
                    
                    # Check client type restrictions
                    if field_name in field_dict:
                        field = field_dict[field_name]
                        if field.client_type_restrictions:
                            if not client_type_id or int(client_type_id) not in field.client_type_restrictions:
                                continue
                    
                    filtered_record[field_name] = field_value
                
                print(f"Form data before filtering: {form_data}")
                print(f"Filtered form data: {filtered_record}")
                
                # Handle client type fields
                if client_type:
                    filtered_record['client_type_id'] = client_type.id
                    if 'client_type' in valid_columns:  # Only add if column exists
                        filtered_record['client_type'] = client_type.client_name
                    print(f"Added client type fields: id={client_type.id}, name={client_type.client_name}")
                
                # Handle postal_town (use same value as county if not provided)
                if 'county' in filtered_record and 'postal_town' in valid_columns and 'postal_town' not in filtered_record:
                    filtered_record['postal_town'] = filtered_record['county']
                
                # Add required fields
                filtered_record['submission_date'] = datetime.now()
                filtered_record['status'] = 'Pending'
                filtered_record['user_id'] = current_user.id
                
                print("Final form data for submission:", filtered_record)
                
                # Validate required fields
                missing_fields = []
                for field in form_fields:
                    if field.is_required:
                        # Skip validation if field is restricted to certain client types and current client type is not in the list
                        if field.client_type_restrictions and client_type_id:
                            if int(client_type_id) not in field.client_type_restrictions:
                                continue
                        
                        field_value = filtered_record.get(field.field_name)
                        if not field_value and field.field_type != 'file':
                            missing_fields.append(field.field_label)
                
                if missing_fields:
                    print(f"Missing required fields: {missing_fields}")
                    flash(f"Please fill in the following required fields: {', '.join(missing_fields)}", 'error')
                    return render_template('user/dynamic_form.html',
                                        module=module,
                                        form_fields=form_fields,
                                        form=form,
                                        form_data=request.form)
                
                # Insert record into dynamic table
                try:
                    print("Attempting to insert record into database...")
                    result = db.session.execute(dynamic_table.insert().values(**filtered_record))
                    record_id = result.inserted_primary_key[0]
                    
                    # If this is a CLM02 form and we have a prospect_id, update the prospect's status
                    if module.code == 'CLM02' and 'prospect_id' in request.args:
                        prospect_id = request.args.get('prospect_id')
                        try:
                            # Update the prospect's status to 'Converted'
                            metadata_clm01 = MetaData()
                            metadata_clm01.reflect(bind=db.engine, only=['form_data_clm01'])
                            if 'form_data_clm01' in metadata_clm01.tables:
                                prospect_table = metadata_clm01.tables['form_data_clm01']
                                stmt = prospect_table.update().where(
                                    prospect_table.c.id == prospect_id
                                ).values(
                                    status='Converted'
                                )
                                db.session.execute(stmt)
                                print(f"Updated prospect {prospect_id} status to Converted")
                        except Exception as e:
                            print(f"Error updating prospect status: {str(e)}")
                            # Don't rollback the client registration, just log the error
                            
                    db.session.commit()
                    print(f"Successfully inserted record with ID: {record_id}")
                    flash('Form submitted successfully!', 'success')
                    return redirect(url_for('user.dashboard'))
                except Exception as insert_error:
                    db.session.rollback()
                    print(f"Error during database insert/commit: {str(insert_error)}")
                    print(f"Full traceback: {traceback.format_exc()}")
                    raise
                
            except Exception as e:
                db.session.rollback()
                print(f"Error saving form data: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
                error_msg = str(e)
                
                # Provide more specific error messages
                if 'missing required columns' in error_msg.lower():
                    flash('The form structure is invalid. Please contact support.', 'error')
                elif 'table not found' in error_msg.lower():
                    flash('The form table does not exist. Please contact support.', 'error')
                elif 'failed to save uploaded file' in error_msg.lower():
                    flash('Failed to save one or more uploaded files. Please try again.', 'error')
                elif 'duplicate entry' in error_msg.lower():
                    flash('A record with this information already exists.', 'error')
                elif 'foreign key constraint' in error_msg.lower():
                    flash('Invalid reference data provided. Please check your selections.', 'error')
                elif 'null value in column' in error_msg.lower():
                    flash('Please fill in all required fields.', 'error')
                else:
                    flash('An error occurred while saving the form data. Please try again.', 'error')
                
                return render_template('user/dynamic_form.html',
                                    module=module,
                                    form_fields=form_fields,
                                    form=form,
                                    form_data=request.form)
        
        return render_template('user/dynamic_form.html',
                            module=module,
                            form_fields=form_fields,
                            form=form,
                            form_data=form_data)
                            
    except Exception as e:
        print(f"Error loading form: {str(e)}")
        flash('An error occurred while loading the form. Please try again.', 'error')
        return render_template('error.html', error=str(e))

@user_bp.route('/prospects')
@login_required
def prospects():
    """List all prospect registrations."""
    try:
        # Get search parameters
        search_query = request.args.get('search', '').strip()
        
        # Get all prospect registrations
        metadata = MetaData()
        metadata.reflect(bind=db.engine, only=['form_data_clm01'])
        if 'form_data_clm01' not in metadata.tables:
            flash('Prospect registration table not found.', 'error')
            return redirect(url_for('user.dashboard'))
            
        # Get the table
        table = metadata.tables['form_data_clm01']
        
        # Build base query
        query = db.session.query(table).join(
            Staff, Staff.id == table.c.user_id
        ).join(
            ClientType, ClientType.id == table.c.client_type_id
        )

        # Apply search filter if search query exists
        if search_query:
            search_filter = or_(
                table.c.first_name.ilike(f'%{search_query}%'),
                table.c.last_name.ilike(f'%{search_query}%'),
                table.c.mobile_phone.ilike(f'%{search_query}%'),
                table.c.email.ilike(f'%{search_query}%'),
                table.c.id_number.ilike(f'%{search_query}%'),
                table.c.county.ilike(f'%{search_query}%'),
                table.c.purpose_of_visit.ilike(f'%{search_query}%'),
                Staff.username.ilike(f'%{search_query}%')
            )
            query = query.filter(search_filter)
        
        # Order by submission date
        query = query.order_by(table.c.submission_date.desc())
        
        prospects = query.all()
        
        return render_template('user/prospects.html', 
                            prospects=prospects,
                            Staff=Staff,
                            ClientType=ClientType,
                            search_query=search_query)
                            
    except Exception as e:
        print(f"Error loading prospects: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        flash('An error occurred while loading prospects.', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/get_sub_counties/<county>')
@login_required
def get_sub_counties(county):
    """Get sub-counties for a given county."""
    try:
        # Clean the county name
        county = county.strip()
        
        # Check if county exists in our data
        if county in KENYA_COUNTIES:
            sub_counties = sorted(KENYA_COUNTIES[county])  # Sort alphabetically
            return jsonify({
                'success': True,
                'data': sub_counties
            })
        else:
            print(f"County not found: {county}")
            return jsonify({
                'success': False,
                'message': f'County "{county}" not found',
                'data': []
            }), 404
            
    except Exception as e:
        print("\n=== Error Details ===")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\nTraceback:")
        import traceback
        traceback.print_exc()
        print("\nRequest Details:")
        print(f"URL: {request.url}")
        print(f"Method: {request.method}")
        print(f"Headers: {dict(request.headers)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@user_bp.route('/convert_to_client/<int:prospect_id>')
@login_required
def convert_to_client(prospect_id):
    """Convert a prospect to a client by pre-populating CLM02 form."""
    try:
        # Get the prospect's data
        metadata = MetaData()
        metadata.reflect(bind=db.engine, only=['form_data_clm01'])
        if 'form_data_clm01' not in metadata.tables:
            flash('Prospect data not found.', 'error')
            return redirect(url_for('user.prospects'))
            
        # Get the prospect's data
        table = metadata.tables['form_data_clm01']
        prospect = db.session.query(table).filter(table.c.id == prospect_id).first()
        
        if not prospect:
            flash('Prospect not found.', 'error')
            return redirect(url_for('user.prospects'))
            
        if prospect.status != 'Pending':
            flash('This prospect has already been processed.', 'error')
            return redirect(url_for('user.prospects'))
        
        # Prepare data for CLM02 form
        form_data = {
            'first_name': getattr(prospect, 'first_name', ''),
            'middle_name': getattr(prospect, 'middle_name', ''),
            'last_name': getattr(prospect, 'last_name', ''),
            'id_type': getattr(prospect, 'id_type', ''),
            'id_number': getattr(prospect, 'id_number', ''),
            'mobile_phone': getattr(prospect, 'mobile_phone', ''),
            'email': getattr(prospect, 'email', ''),
            'county': getattr(prospect, 'county', ''),
            'sub_county': getattr(prospect, 'sub_county', ''),
            'client_type': getattr(prospect, 'client_type_id', ''),
            'prospect_id': prospect_id  # Reference to original prospect
        }
        
        # Filter out empty values
        form_data = {k: v for k, v in form_data.items() if v}
        
        # Redirect to CLM02 form with pre-populated data
        return redirect(url_for('user.dynamic_form', 
                              module_code='CLM02',
                              **form_data))
                              
    except Exception as e:
        print(f"Error converting prospect to client: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        flash('An error occurred while converting prospect to client.', 'error')
        return redirect(url_for('user.prospects'))

@user_bp.route('/update_prospect_status/<int:prospect_id>', methods=['POST'])
@login_required
def update_prospect_status(prospect_id):
    """Update the status of a prospect."""
    try:
        # Get the prospect's data
        metadata = MetaData()
        metadata.reflect(bind=db.engine, only=['form_data_clm01'])
        if 'form_data_clm01' not in metadata.tables:
            flash('Prospect data not found.', 'error')
            return redirect(url_for('user.prospects'))
            
        # Get the prospect's data
        table = metadata.tables['form_data_clm01']
        prospect = db.session.query(table).filter(table.c.id == prospect_id).first()
        
        if not prospect:
            flash('Prospect not found.', 'error')
            return redirect(url_for('user.prospects'))
        
        # Update status to Pending
        stmt = table.update().where(table.c.id == prospect_id).values(status='Pending')
        db.session.execute(stmt)
        db.session.commit()
        
        flash('Prospect status updated successfully.', 'success')
        return redirect(url_for('user.prospects'))
                              
    except Exception as e:
        print(f"Error updating prospect status: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        flash('An error occurred while updating prospect status.', 'error')
        return redirect(url_for('user.prospects'))

@user_bp.route('/reports')
@login_required
def reports():
    # TODO: Implement reports page
    return render_template('user/reports.html')
