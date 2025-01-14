import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from models.module import Module, FormField
from models.form_section import FormSection
from models.product import Product
from models.client_type import ClientType
from models.staff import Staff
from models.form_submission import FormSubmission
from models.calendar_event import CalendarEvent
from models.client import Client
from models.correspondence import Correspondence
from models.guarantor import Guarantor
from services.guarantor_service import GuarantorService
from extensions import db, csrf
from flask_wtf import FlaskForm
from services.scheduler import get_cached_tables
from datetime import datetime, timedelta
import traceback
import os
import json
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_, text, MetaData, Table
import time
from flask import current_app
from routes.collection_schedule import collection_schedule_bp
from services.collection_schedule_service import CollectionScheduleService
import io
import mysql.connector
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint

user_bp = Blueprint('user', __name__)

# Register collection schedule blueprint without additional prefix
user_bp.register_blueprint(collection_schedule_bp)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get client management modules (only child modules)
    client_modules = Module.query.filter(
        and_(
            Module.code.like('CLM%'),
            Module.code != 'CLM00',  # Exclude parent module
            Module.is_active == True
        )
    ).order_by(Module.code).all()
    
    # Get loan management modules (only child modules)
    loan_modules = Module.query.filter(
        and_(
            Module.code.like('LN%'),
            ~Module.code.endswith('00'),  # Exclude parent modules
            Module.is_active == True
        )
    ).order_by(Module.code).all()
    
    # Get parent modules for organization
    client_parent = Module.query.filter_by(code='CLM00', is_active=True).first()
    loan_parent = Module.query.filter(
        and_(
            Module.code.like('LN%'),
            Module.code.endswith('00'),
            Module.is_active == True
        )
    ).first()
    
    return render_template('user/dashboard.html',
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
        
        # Get module sections with fields
        sections = FormSection.query.filter_by(
            module_id=module.id,
            is_active=True
        ).order_by(FormSection.order).all()
        
        # Get client types and products
        client_types = ClientType.query.filter_by(status=True).all()
        products = Product.query.filter_by(status='Active').all()

        # ID types configuration
        ID_TYPES = [
            {'value': 'National ID', 'label': 'National ID'},
            {'value': 'Passport', 'label': 'Passport'},
            {'value': 'Alien ID', 'label': 'Alien ID'},
            {'value': 'Military ID', 'label': 'Military ID'}
        ]

        # Postal towns list - Comprehensive list of Kenya's major postal towns
        POSTAL_TOWNS = [
            'Baringo', 'Bomet', 'Bondo', 'Bungoma', 'Busia', 'Butere',
            'Chogoria', 'Chuka', 'Dandora', 'Eastleigh', 'Eldama Ravine', 'Eldoret', 
            'Emali', 'Embu', 'Garissa', 'Gatundu', 'Gede', 'Gilgil', 'Githunguri',
            'Hola', 'Homabay', 'Industrial Area', 'Isiolo', 'Kabarnet', 'Kajiado',
            'Kakamega', 'Kakuma', 'Kaloleni', 'Kandara', 'Kangema', 'Kangundo', 'Karen',
            'Karatina', 'Kericho', 'Keroka', 'Kerugoya', 'Kiambu', 'Kibwezi', 'Kilifi',
            'Kimilili', 'Kinango', 'Kipkelion', 'Kisii', 'Kisumu', 'Kitale', 'Kitengela',
            'Kitui', 'Kwale', 'Lamu', 'Langata', 'Lare', 'Limuru', 'Lodwar', 'Lokichoggio',
            'Londiani', 'Luanda', 'Lugari', 'Machakos', 'Makindu', 'Malaba', 'Malindi',
            'Maragoli', 'Maralal', 'Mariakani', 'Maseno', 'Maua', 'Mbale', 'Meru',
            'Migori', 'Mombasa', 'Moyale', 'Mpeketoni', 'Mtito Andei', 'Muhoroni',
            'Mumias', 'Muranga', 'Mwatate', 'Mwingi', 'Nairobi GPO', 'Naivasha',
            'Nakuru', 'Namanga', 'Nandi Hills', 'Nanyuki', 'Narok', 'Ngong',
            'Nyahururu', 'Nyamira', 'Nyeri', 'Olenguruone', 'Oyugis', 'Parklands',
            'Rongo', 'Ruiru', 'Sagana', 'Sarit Centre', 'Shimoni', 'Siaya', 'Sidindi',
            'Suba', 'Taveta', 'Thika', 'Timau', 'Ukunda', 'Vihiga', 'Voi', 'Wajir',
            'Watamu', 'Webuye', 'Westlands', 'Witu', 'Wote', 'Wundanyi', 'Yala'
        ]
        
        # Render the form template
        return render_template('user/dynamic_form.html',
                            module=module,
                            sections=sections,
                            client_types=client_types,
                            products=products,
                            counties=[],
                            id_types=ID_TYPES,
                            postal_towns=sorted(POSTAL_TOWNS))  # Sort alphabetically
                            
    except Exception as e:
        current_app.logger.error(f"Error loading form: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the form. Please try again.', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/get_sub_counties/<county>')
@login_required
def get_sub_counties(county):
    """Get sub-counties for a given county."""
    try:
        # Clean the county name
        county = county.strip()
        
        # Check if county exists in our data
        if county in []:
            sub_counties = sorted([])  # Sort alphabetically
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

@user_bp.route('/get_postal_towns/<county>')
@login_required
def get_postal_towns(county):
    """Get postal towns for a given county."""
    try:
        # Clean the county name
        county = county.strip()
        
        # Check if county exists in our data
        if county in []:
            # Use the sub-counties as postal towns
            towns = sorted([])  # Sort alphabetically
            return jsonify({
                'success': True,
                'data': towns
            })
        else:
            return jsonify({
                'success': False,
                'message': f'County "{county}" not found',
                'data': []
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error fetching postal towns: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@user_bp.route('/submit_form/<module_code>', methods=['POST'])
@login_required
def submit_form(module_code):
    """Handle form submission."""
    try:
        # Get form data
        form_data = request.form.to_dict()
        
        # Get client type
        client_type_id = form_data.get('client_type')
        if not client_type_id:
            flash('Client type is required', 'error')
            return redirect(url_for('user.dynamic_form', module_code=module_code))
        
        # Get the module
        module = Module.query.filter_by(code=module_code).first_or_404()
        
        # Create new submission
        submission = FormSubmission(
            module_id=module.id,
            client_type_id=client_type_id,
            form_data=form_data,
            created_by=current_user.id,
            status='pending'
        )
        
        # If this is a direct client registration (CLM02), mark it as approved and converted
        if module_code == 'CLM02':
            submission.status = 'approved'
            submission.is_converted = True
        
        db.session.add(submission)
        db.session.commit()
        
        flash('Form submitted successfully!', 'success')
        return redirect(url_for('user.manage_module', module_code=module_code))
        
    except Exception as e:
        print(f"Error submitting form: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        flash(f'Error submitting form: {str(e)}', 'error')
        return redirect(url_for('user.dynamic_form', module_code=module_code))

@user_bp.route('/manage/<module_code>')
@login_required
def manage_module(module_code):
    """Manage submissions for a specific module."""
    try:
        # Debug logs
        print(f"Accessing manage_module with module_code: {module_code}")
        
        module = Module.query.filter_by(code=module_code).first_or_404()
        print(f"Found module: {module.name}")
        
        # Get all client types for filtering
        client_types = ClientType.query.filter_by(status=True).all()
        print(f"Found {len(client_types)} client types")
        
        # Get all active products
        products = Product.query.filter_by(status='Active').all()
        print(f"Found {len(products)} active products")
        
        # Get selected client type from query params
        selected_type = request.args.get('client_type', 'all')
        print(f"Selected client type: {selected_type}")
        
        # Base query with explicit joins
        try:
            if module_code == 'CLM02':  # Clients module
                # For CLM02, get all converted prospects regardless of original module
                submissions = db.session.query(FormSubmission).\
                    join(ClientType, FormSubmission.client_type_id == ClientType.id).\
                    filter(FormSubmission.is_converted == True)
            else:
                # For other modules, filter by module and conversion status
                submissions = db.session.query(FormSubmission).\
                    join(Module, FormSubmission.module_id == Module.id).\
                    join(ClientType, FormSubmission.client_type_id == ClientType.id).\
                    filter(Module.code == module_code)
                
                if module_code == 'CLM01':  # Prospects module
                    submissions = submissions.filter(FormSubmission.is_converted == False)
            
            # Apply client type filter if specified
            if selected_type != 'all':
                submissions = submissions.filter(ClientType.client_code == selected_type)
            
            # Execute query
            submissions = submissions.order_by(FormSubmission.created_at.desc()).all()
            print(f"Found {len(submissions)} submissions")
            print("Submission details:")
            for sub in submissions:
                print(f"ID: {sub.id}, Status: {sub.status}, Converted: {sub.is_converted}")
            
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            print(f"Full traceback: {traceback.format_exc()}")
            raise
        
        return render_template('user/manage_module.html',
                             module=module,
                             submissions=submissions,
                             client_types=client_types,
                             products=products,
                             selected_type=selected_type)
                             
    except Exception as e:
        print(f"Error in manage_module: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        flash('An error occurred while loading the module. Error: ' + str(e), 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/api/submission/<int:submission_id>')
@login_required
def get_submission(submission_id):
    """Get submission details."""
    submission = FormSubmission.query.get_or_404(submission_id)
    return jsonify({
        'id': submission.id,
        'status': submission.status,
        'form_data': submission.form_data,
        'created_at': submission.created_at.strftime('%Y-%m-%d %H:%M')
    })

@user_bp.route('/delete_submission/<int:submission_id>', methods=['POST'])
@login_required
def delete_submission(submission_id):
    """Delete a submission."""
    try:
        submission = FormSubmission.query.get_or_404(submission_id)
        db.session.delete(submission)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@user_bp.route('/edit_submission/<int:submission_id>')
@login_required
def edit_submission(submission_id):
    """Edit a submission."""
    submission = FormSubmission.query.get_or_404(submission_id)
    return redirect(url_for('user.dynamic_form', 
                          module_code=submission.module.code,
                          submission_id=submission.id))

@user_bp.route('/prospect/<int:submission_id>')
@login_required
@csrf.exempt
def view_prospect(submission_id):
    """View prospect details."""
    try:
        submission = FormSubmission.query.get_or_404(submission_id)
        products = Product.query.filter_by(status='Active').all()
        client_types = ClientType.query.filter_by(status=True).all()
        
        # Get module sections with fields
        sections = FormSection.query.filter_by(
            module_id=submission.module.id,
            is_active=True
        ).order_by(FormSection.order).all()

        # Process fields to ensure proper client type restrictions
        individual_fields = ['first_name', 'middle_name', 'last_name', 'gender', 'id_type', 'serial_number']
        print("Form Data:", submission.form_data)
        print("ID Type from form data:", submission.form_data.get('id_type'))
        for section in sections:
            for field in section.fields:
                # Set client type restrictions for individual fields
                if field.field_name in individual_fields:
                    field.client_type_restrictions = [1]  # 1 is the ID for Individual Client
                
                # Special handling for gender field
                if field.field_name == 'gender':
                    field.field_type = 'radio'
                    field.options = [
                        {'value': 'Male', 'label': 'Male'},
                        {'value': 'Female', 'label': 'Female'}
                    ]

        # Get purpose of visit field options
        purpose_field = FormField.query.filter_by(
            module_id=submission.module.id,
            field_name='purpose_of_visit'
        ).first()
        
        # Default purpose options if none exist in database
        default_purpose_options = [
            {'value': 'loan_inquiry', 'label': 'Loan Inquiry'},
            {'value': 'product_inquiry', 'label': 'Product Inquiry'},
            {'value': 'account_opening', 'label': 'Account Opening'},
            {'value': 'financial_advisory', 'label': 'Financial Advisory'},
            {'value': 'other', 'label': 'Other'}
        ]
        
        purpose_options = purpose_field.options if purpose_field and purpose_field.options else default_purpose_options
        print("Purpose Options:", purpose_options)
        print("Selected Purpose:", submission.form_data.get('purpose_of_visit'))
        
        # ID types configuration
        ID_TYPES = [
            {'value': 'National ID', 'label': 'National ID'},
            {'value': 'Passport', 'label': 'Passport'},
            {'value': 'Alien ID', 'label': 'Alien ID'},
            {'value': 'Military ID', 'label': 'Military ID'}
        ]
        
        print("ID Types:", ID_TYPES)
        print("Form Data:", submission.form_data)
        print("ID Type from form data:", submission.form_data.get('id_type'))
        
        return render_template('user/view_prospect.html',
                             submission=submission,
                             sections=sections,
                             products=products,
                             client_types=client_types,
                             id_types=ID_TYPES,
                             counties=[],
                             purpose_options=purpose_options)
    except Exception as e:
        flash(f'Error viewing prospect: {str(e)}', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/prospect/<int:submission_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_prospect(submission_id):
    """Edit a prospect details."""
    try:
        submission = FormSubmission.query.get_or_404(submission_id)
        products = Product.query.filter_by(status='Active').all()
        client_types = ClientType.query.filter_by(status=True).all()
        
        # Get module sections with fields
        sections = FormSection.query.filter_by(
            module_id=submission.module.id,
            is_active=True
        ).order_by(FormSection.order).all()

        # Process fields to ensure proper client type restrictions
        individual_fields = ['first_name', 'middle_name', 'last_name', 'gender', 'id_type', 'serial_number']
        print("Form Data:", submission.form_data)
        print("ID Type from form data:", submission.form_data.get('id_type'))
        for section in sections:
            for field in section.fields:
                # Set client type restrictions for individual fields
                if field.field_name in individual_fields:
                    field.client_type_restrictions = [1]  # 1 is the ID for Individual Client
                
                # Special handling for gender field
                if field.field_name == 'gender':
                    field.field_type = 'radio'
                    field.options = [
                        {'value': 'Male', 'label': 'Male'},
                        {'value': 'Female', 'label': 'Female'}
                    ]
                    print(f"Gender value in database: {submission.form_data.get('gender')}")

        # Get purpose of visit field options
        purpose_field = FormField.query.filter_by(
            module_id=submission.module.id,
            field_name='purpose_of_visit'
        ).first()
        
        # Default purpose options if none exist in database
        default_purpose_options = [
            {'value': 'loan_inquiry', 'label': 'Loan Inquiry'},
            {'value': 'product_inquiry', 'label': 'Product Inquiry'},
            {'value': 'account_opening', 'label': 'Account Opening'},
            {'value': 'financial_advisory', 'label': 'Financial Advisory'},
            {'value': 'other', 'label': 'Other'}
        ]
        
        purpose_options = purpose_field.options if purpose_field and purpose_field.options else default_purpose_options
        print("Purpose Options:", purpose_options)
        print("Selected Purpose:", submission.form_data.get('purpose_of_visit'))
        
        # ID types configuration
        ID_TYPES = [
            {'value': 'National ID', 'label': 'National ID'},
            {'value': 'Passport', 'label': 'Passport'},
            {'value': 'Alien ID', 'label': 'Alien ID'},
            {'value': 'Military ID', 'label': 'Military ID'}
        ]
        
        print("ID Types:", ID_TYPES)
        print("Form Data:", submission.form_data)
        print("ID Type from form data:", submission.form_data.get('id_type'))
        
        # Postal towns list
        POSTAL_TOWNS = [
            'Baringo', 'Bomet', 'Bondo', 'Bungoma', 'Busia', 'Butere',
            'Chogoria', 'Chuka', 'Dandora', 'Eastleigh', 'Eldama Ravine', 'Eldoret', 
            'Emali', 'Embu', 'Garissa', 'Gatundu', 'Gede', 'Gilgil', 'Githunguri',
            'Hola', 'Homabay', 'Industrial Area', 'Isiolo', 'Kabarnet', 'Kajiado',
            'Kakamega', 'Kakuma', 'Kaloleni', 'Kandara', 'Kangema', 'Kangundo', 'Karen',
            'Karatina', 'Kericho', 'Keroka', 'Kerugoya', 'Kiambu', 'Kibwezi', 'Kilifi',
            'Kimilili', 'Kinango', 'Kipkelion', 'Kisii', 'Kisumu', 'Kitale', 'Kitengela',
            'Kitui', 'Kwale', 'Lamu', 'Langata', 'Lare', 'Limuru', 'Lodwar', 'Lokichoggio',
            'Londiani', 'Luanda', 'Lugari', 'Machakos', 'Makindu', 'Malaba', 'Malindi',
            'Maragoli', 'Maralal', 'Mariakani', 'Maseno', 'Maua', 'Mbale', 'Meru',
            'Migori', 'Mombasa', 'Moyale', 'Mpeketoni', 'Mtito Andei', 'Muhoroni',
            'Mumias', 'Muranga', 'Mwatate', 'Mwingi', 'Nairobi GPO', 'Naivasha',
            'Nakuru', 'Namanga', 'Nandi Hills', 'Nanyuki', 'Narok', 'Ngong',
            'Nyahururu', 'Nyamira', 'Nyeri', 'Olenguruone', 'Oyugis', 'Parklands',
            'Rongo', 'Ruiru', 'Sagana', 'Sarit Centre', 'Shimoni', 'Siaya', 'Sidindi',
            'Suba', 'Taveta', 'Thika', 'Timau', 'Ukunda', 'Vihiga', 'Voi', 'Wajir',
            'Watamu', 'Webuye', 'Westlands', 'Witu', 'Wote', 'Wundanyi', 'Yala'
        ]
        
        if request.method == 'POST':
            # Update submission data
            form_data = request.form.to_dict()
            submission.form_data = form_data
            submission.status = request.form.get('status', submission.status)
            submission.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Prospect updated successfully', 'success')
            return redirect(url_for('user.manage_module', module_code=submission.module.code))
            
        return render_template('user/edit_prospect.html', 
                             submission=submission,
                             products=products,
                             client_types=client_types,
                             sections=sections,
                             counties=[],
                             postal_towns=sorted(POSTAL_TOWNS),
                             ID_TYPES=ID_TYPES,
                             purpose_options=purpose_options)
    except Exception as e:
        flash(f'Error editing prospect: {str(e)}', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/prospect/<int:submission_id>/delete')
@login_required
def delete_prospect(submission_id):
    """Delete a prospect."""
    try:
        submission = FormSubmission.query.get_or_404(submission_id)
        module_code = submission.module.code
        
        db.session.delete(submission)
        db.session.commit()
        
        flash('Prospect deleted successfully', 'success')
        return redirect(url_for('user.manage_module', module_code=module_code))
    except Exception as e:
        flash(f'Error deleting prospect: {str(e)}', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/convert_to_client/<submission_id>', methods=['GET', 'POST'])
@login_required
def convert_to_client(submission_id):
    """Convert an approved prospect to a client."""
    try:
        # Get the submission
        submission = FormSubmission.query.get_or_404(submission_id)
        
        # Get CLM02 module
        clm02_module = Module.query.filter_by(code='CLM02').first_or_404()
        
        if request.method == 'GET':
            # Check if the submission is approved
            if submission.status != 'approved':
                flash('Only approved prospects can be converted to clients', 'error')
                return redirect(url_for('user.manage_module', module_code='CLM01'))
                
            # Check if already converted
            if submission.is_converted:
                flash('This prospect has already been converted to a client', 'error')
                return redirect(url_for('user.manage_module', module_code='CLM01'))
            
            # Get CLM02 sections with fields
            sections = FormSection.query.filter_by(
                module_id=clm02_module.id,
                is_active=True
            ).order_by(FormSection.order).all()
            
            # Get client types and products
            client_types = ClientType.query.filter_by(status=True).all()
            products = Product.query.filter_by(status='Active').all()

            # Pre-fill form data from the prospect submission
            form_data = submission.form_data
            
            # Render the conversion form
            return render_template('user/convert_form.html',
                                submission=submission,
                                module=clm02_module,
                                sections=sections,
                                client_types=client_types,
                                products=products,
                                counties=[],
                                form_data=form_data)
        
        elif request.method == 'POST':
            # Check if the submission is approved
            if submission.status != 'approved':
                return jsonify({
                    'success': False,
                    'message': 'Only approved prospects can be converted to clients'
                }), 400
                
            # Check if already converted
            if submission.is_converted:
                return jsonify({
                    'success': False,
                    'message': 'This prospect has already been converted to a client'
                }), 400
            
            # Get form data
            form_data = request.form.to_dict()
            
            # Update the submission with CLM02 data and mark as converted
            submission.form_data.update(form_data)  # Merge new form data with existing data
            submission.is_converted = True
            submission.updated_at = datetime.utcnow()
            
            # Commit the changes
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Successfully converted prospect to client'
            })
            
    except Exception as e:
        print(f"Error converting prospect to client: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        if request.method == 'POST':
            return jsonify({
                'success': False,
                'message': f'Error converting prospect to client: {str(e)}'
            }), 500
        else:
            flash(f'Error loading conversion form: {str(e)}', 'error')
            return redirect(url_for('user.manage_module', module_code='CLM01'))

@user_bp.route('/register_client/<submission_id>', methods=['GET', 'POST'])
@login_required
def register_client(submission_id):
    """Register a client with CLM02 form data."""
    try:
        # Get the submission
        submission = FormSubmission.query.get_or_404(submission_id)
        print(f"Found submission: {submission.id}")
        
        # Get CLM02 module
        clm02_module = Module.query.filter_by(code='CLM02').first_or_404()
        print(f"Found CLM02 module: {clm02_module.id} - {clm02_module.name}")
        
        if request.method == 'GET':
            # Get CLM02 sections with fields
            sections = FormSection.query.filter_by(
                module_id=clm02_module.id
            ).order_by(FormSection.order).all()
            
            print(f"\nFound {len(sections)} sections:")
            for section in sections:
                print(f"\nSection: {section.name} (Order: {section.order})")
                print(f"Client Type Restrictions: {section.client_type_restrictions}")
                print("Fields:")
                for field in section.fields:
                    print(f"- {field.field_label} ({field.field_type})")
                    print(f"  Required: {field.is_required}")
                    print(f"  Client Types: {field.client_type_restrictions}")
            
            # Get client types and products
            client_types = ClientType.query.filter_by(status=True).all()
            products = Product.query.filter_by(status='Active').all()
            
            print(f"\nFound {len(client_types)} client types:")
            for ct in client_types:
                print(f"- {ct.client_name} (ID: {ct.id})")
            
            print(f"\nFound {len(products)} products:")
            for product in products:
                print(f"- {product.name} (ID: {product.id})")
            
            # Pre-fill form data from the existing submission
            form_data = submission.form_data
            print(f"\nForm data: {form_data}")
            
            # Get client type from form data
            client_type = form_data.get('client_type', '')
            print(f"Client type: {client_type}")
            
            # Render the registration form
            return render_template('user/register_form.html',
                                submission=submission,
                                module=clm02_module,
                                sections=sections,
                                client_types=client_types,
                                products=products,
                                counties=[],
                                form_data=form_data,
                                client_type=client_type)
        
        elif request.method == 'POST':
            # Get form data
            form_data = request.form.to_dict()
            
            # Update the submission with CLM02 data
            submission.form_data.update(form_data)  # Merge new form data with existing data
            submission.updated_at = datetime.utcnow()
            
            # Commit the changes
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Successfully registered client information'
            })
            
    except Exception as e:
        print(f"Error registering client: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        if request.method == 'POST':
            return jsonify({
                'success': False,
                'message': f'Error registering client: {str(e)}'
            }), 500
        else:
            flash(f'Error loading registration form: {str(e)}', 'error')
            return redirect(url_for('user.manage_module', module_code='CLM02'))

@user_bp.route('/api/clients/search', methods=['GET'])
@login_required
def search_clients():
    """Search for clients/members"""
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    
    current_app.logger.info(f"Client search request - Query: {query}, Page: {page}")
    
    if not query or len(query) < 2:
        return jsonify({
            'items': [],
            'has_more': False
        })
    
    try:
        # Call mock core banking API
        api_url = current_app.config['CORE_BANKING_API_URL']
        response = requests.get(
            f"{api_url}/members/search",
            params={
                'search_term': query,
                'page': page,
                'limit': 10
            },
            headers={
                'Authorization': f"Bearer {current_app.config['CORE_BANKING_API_KEY']}"
            }
        )
        
        current_app.logger.info(f"Core banking API response status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            current_app.logger.info(f"Core banking API response data: {data}")
            
            # Transform the response to match Select2 format
            items = [{
                'id': str(member['id']),
                'text': f"{member.get('full_name', '')} ({member.get('member_no', '')})",
                'member_no': member.get('member_no', '')
            } for member in data.get('members', [])]
            
            return jsonify({
                'items': items,
                'has_more': data.get('has_more', False)
            })
        else:
            current_app.logger.error(f"Core banking API error: {response.status_code} - {response.text}")
            return jsonify({
                'error': 'Failed to fetch members',
                'items': [],
                'has_more': False
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error searching members: {str(e)}")
        return jsonify({
            'error': 'Failed to search members',
            'items': [],
            'has_more': False
        }), 500

@user_bp.route('/correspondence')
@login_required
def correspondence():
    return render_template('user/correspondence.html')

@user_bp.route('/api/communications', methods=['GET'])
@login_required
def get_communications():
    """Get communication history with optional filters"""
    from models.correspondence import Correspondence
    
    member_id = request.args.get('member_id', type=int)
    loan_id = request.args.get('loan_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sync = request.args.get('sync', 'true').lower() == 'true'
    
    # Convert date strings to datetime if provided
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    try:
        communications = Correspondence.get_communications(
            member_id=member_id,
            loan_id=loan_id,
            start_date=start_date,
            end_date=end_date,
            sync_first=sync
        )
        
        return jsonify({
            'status': 'success',
            'data': [comm.to_dict() for comm in communications]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching communications: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch communications'
        }), 500

@user_bp.route('/api/communications/sync', methods=['POST'])
@login_required
def sync_communications():
    """Force sync communications from core banking"""
    from models.correspondence import Correspondence
    
    member_id = request.json.get('member_id', type=int)
    loan_id = request.json.get('loan_id', type=int)
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    
    # Convert date strings to datetime if provided
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    try:
        synced_records = Correspondence.sync_from_core_banking(
            member_id=member_id,
            loan_id=loan_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully synced {len(synced_records)} new communications',
            'data': [comm.to_dict() for comm in synced_records]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error syncing communications: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to sync communications'
        }), 500

@user_bp.route('/api/correspondence/<client_id>')
@login_required
def get_correspondence(client_id):
    """Get correspondence for a client."""
    # Call mock core banking API
    response = requests.get(f'http://localhost:5003/api/correspondence/{client_id}')
    
    if response.ok:
        data = response.json()
        return jsonify({
            'correspondence': [{
                'id': item['id'],
                'type': item['type'],
                'content': item['content'],
                'created_at': item['date'],
                'sent_by': 'System Admin'  # Mock sent_by since it's not in the mock data
            } for item in data['items']]
        })
    else:
        return jsonify({'error': 'Failed to fetch correspondence'}), 500

@user_bp.route('/manage-calendar')
@login_required
def manage_calendar():
    return render_template('user/manage_calendar.html')

@user_bp.route('/api/calendar/events', methods=['GET'])
@login_required
@csrf.exempt
def get_calendar_events():
    try:
        # Get query parameters for filtering
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        client_id = request.args.get('client_id')
        loan_id = request.args.get('loan_id')

        # Build the query
        query = CalendarEvent.query.filter_by(created_by_id=current_user.id)

        # Apply filters if provided
        if start_date and end_date:
            query = query.filter(
                CalendarEvent.start_time >= datetime.fromisoformat(start_date),
                CalendarEvent.start_time <= datetime.fromisoformat(end_date)
            )
        if client_id:
            query = query.filter_by(client_id=client_id)
        if loan_id:
            query = query.filter_by(loan_id=loan_id)

        # Get all events
        events = query.order_by(CalendarEvent.start_time).all()
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/api/calendar/events', methods=['POST'])
@login_required
@csrf.exempt
def create_calendar_event():
    try:
        data = request.json
        event = CalendarEvent.create_event(data, current_user.id)
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/api/calendar/events/<int:event_id>', methods=['PUT'])
@login_required
@csrf.exempt
def update_calendar_event(event_id):
    try:
        event = CalendarEvent.query.get_or_404(event_id)
        
        # Check if the user has permission to update this event
        if event.created_by_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.json
        event.update_event(data)
        return jsonify(event.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/api/calendar/events/<int:event_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_calendar_event(event_id):
    try:
        event = CalendarEvent.query.get_or_404(event_id)
        
        # Check if the user has permission to delete this event
        if event.created_by_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        event.delete_event()
        return jsonify({'message': 'Event deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reports')
@login_required
def reports():
    # TODO: Implement reports page
    return render_template('user/reports.html')

@user_bp.route('/post-disbursement')
@login_required
def post_disbursement():
    current_app.logger.info("Starting post_disbursement route")
    
    # Define default values for overdue loans
    default_overdue_loans = {
        'NORMAL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '0-30 days'},
        'WATCH': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '31-90 days'},
        'SUBSTANDARD': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '91-180 days'},
        'DOUBTFUL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '181-360 days'},
        'LOSS': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '>360 days'}
    }
    
    try:
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        current_app.logger.info(f"Found core banking system: {core_system.name if core_system else None}")
        
        if not core_system:
            flash('No active core banking system configured', 'error')
            return render_template('user/post_disbursement.html', 
                                total_loans=0,
                                total_outstanding=0,
                                total_in_arrears=0,
                                recovery_rate=0,
                                npl_ratio=0,
                                npl_coverage_ratio=0,
                                cost_of_risk=0,
                                par30_ratio=0,
                                total_provisions=0,
                                classification_data={
                                    'labels': [],
                                    'counts': [],
                                    'amounts': []
                                },
                                loan_data=[],
                                overdue_loans=default_overdue_loans,
                                last_sync=None,
                                error='No active core banking system configured')

        # Get loan grading endpoint
        loan_grading_endpoint = CoreBankingEndpoint.query.filter_by(
            system_id=core_system.id,
            name='loan_grading',
            is_active=True
        ).first()
        current_app.logger.info(f"Found loan grading endpoint: {loan_grading_endpoint.name if loan_grading_endpoint else None}")

        if not loan_grading_endpoint:
            flash('Loan grading endpoint not configured', 'error')
            return render_template('user/post_disbursement.html',
                                total_loans=0,
                                total_outstanding=0,
                                total_in_arrears=0,
                                recovery_rate=0,
                                npl_ratio=0,
                                npl_coverage_ratio=0,
                                cost_of_risk=0,
                                par30_ratio=0,
                                total_provisions=0,
                                classification_data={
                                    'labels': [],
                                    'counts': [],
                                    'amounts': []
                                },
                                loan_data=[],
                                overdue_loans=default_overdue_loans,
                                last_sync=None,
                                error='Loan grading endpoint not configured')

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError):
            auth_credentials = {'username': 'root', 'password': ''}
            
        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }
        current_app.logger.info(f"Connecting to database: {core_system.database_name}")
        
        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # List tables to check the correct table name
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        current_app.logger.info(f"Available tables: {tables}")
        
        # Check table schema
        cursor.execute("DESCRIBE LoanLedgerEntries")
        columns = cursor.fetchall()
        current_app.logger.info(f"Table schema: {columns}")
        
        # Check LoanApplications schema
        cursor.execute("DESCRIBE LoanApplications")
        loan_columns = cursor.fetchall()
        current_app.logger.info(f"LoanApplications schema: {loan_columns}")
        
        # Check Members schema
        cursor.execute("DESCRIBE Members")
        member_columns = cursor.fetchall()
        current_app.logger.info(f"Members schema: {member_columns}")
        
        # Check Users schema
        cursor.execute("DESCRIBE Users")
        user_columns = cursor.fetchall()
        current_app.logger.info(f"Users schema: {user_columns}")
        
        # Build query from endpoint configuration
        endpoint_params = json.loads(loan_grading_endpoint.parameters)
        current_app.logger.info("Endpoint parameters loaded")
        
        # Start with base table
        query = """
            SELECT 
                l.LoanID,
                l.OutstandingBalance,
                l.ArrearsAmount,
                l.ArrearsDays,
                la.LoanNo,
                la.LoanAmount,
                ld.LoanStatus
            FROM LoanLedgerEntries l
            JOIN (
                SELECT LoanID, MAX(LedgerID) as latest_id
                FROM LoanLedgerEntries
                GROUP BY LoanID
            ) latest ON l.LoanID = latest.LoanID AND l.LedgerID = latest.latest_id
            JOIN LoanDisbursements ld ON l.LoanID = ld.LoanAppID
            JOIN LoanApplications la ON ld.LoanAppID = la.LoanAppID
            WHERE ld.LoanStatus = 'Active'
            ORDER BY l.LoanID
        """
            
        current_app.logger.info(f"Executing query: {query}")
        cursor.execute(query)
        loan_data = cursor.fetchall()
        current_app.logger.info(f"Found {len(loan_data)} active loans")
        
        # Initialize loan classification counters with proper float values
        overdue_loans = {
            'NORMAL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '0-30 days'},
            'WATCH': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '31-90 days'},
            'SUBSTANDARD': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '91-180 days'},
            'DOUBTFUL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '181-360 days'},
            'LOSS': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '>360 days'}
        }

        # Process loan data
        total_outstanding = float(0)
        total_in_arrears = float(0)
        
        # Debug: Print all loans before processing
        current_app.logger.info("Raw loan data from database:")
        for loan in loan_data:
            current_app.logger.info(f"Loan {loan['LoanID']} - LoanNo: {loan['LoanNo']}, Balance: {loan['OutstandingBalance']}, Arrears: {loan['ArrearsAmount']}, Days: {loan['ArrearsDays']}")
        
        for loan in loan_data:
            try:
                # Extract values from loan ledger entries with proper error handling
                loan_id = loan.get('LoanID', 'Unknown')
                loan_no = loan.get('LoanNo', 'Unknown')
                outstanding_balance = float(loan.get('OutstandingBalance', 0))
                arrears_amount = float(loan.get('ArrearsAmount', 0))
                arrears_days = int(loan.get('ArrearsDays', 0))
                
                current_app.logger.info(f"Processing Loan {loan_id} (No: {loan_no}): Balance={outstanding_balance}, Arrears={arrears_amount}, Days={arrears_days}")
                
                # Update totals
                total_outstanding += outstanding_balance
                total_in_arrears += arrears_amount
                
                # Classify loan based on arrears days
                if arrears_days <= 30:
                    category = 'NORMAL'
                elif 31 <= arrears_days <= 90:
                    category = 'WATCH'
                elif 91 <= arrears_days <= 180:
                    category = 'SUBSTANDARD'
                elif 181 <= arrears_days <= 360:
                    category = 'DOUBTFUL'
                else:
                    category = 'LOSS'
                
                # Update classification counters
                overdue_loans[category]['count'] += 1
                overdue_loans[category]['amount'] += outstanding_balance
                
                current_app.logger.info(f"Classified loan {loan_id} as {category}")
            except Exception as e:
                current_app.logger.error(f"Error processing loan {loan.get('LoanID', 'Unknown')}: {str(e)}")
                continue

        # Log classification totals
        current_app.logger.info("\nFinal classification totals:")
        for category, data in overdue_loans.items():
            current_app.logger.info(f"{category}: Count={data['count']}, Amount={data['amount']}")

        # Calculate percentages for each category
        total_amount = sum(cat['amount'] for cat in overdue_loans.values())
        if total_amount > 0:
            for category in overdue_loans:
                overdue_loans[category]['percentage'] = (overdue_loans[category]['amount'] / total_amount * 100)
                current_app.logger.info(f"{category} percentage: {overdue_loans[category]['percentage']}%")
        else:
            for category in overdue_loans:
                overdue_loans[category]['percentage'] = float(0)
        
        # Calculate metrics
        # Recovery Rate = (Outstanding - Arrears) / Outstanding
        try:
            recovery_rate = ((total_outstanding - total_in_arrears) / total_outstanding * 100) if total_outstanding > 0 else float(0)
        except:
            recovery_rate = float(0)
        
        # NPL Amount (Non-Performing Loans = Substandard + Doubtful + Loss)
        npl_amount = float(overdue_loans['SUBSTANDARD']['amount'] + 
                         overdue_loans['DOUBTFUL']['amount'] + 
                         overdue_loans['LOSS']['amount'])
        
        # NPL Ratio = NPL Amount / Total Outstanding
        try:
            npl_ratio = (npl_amount / total_outstanding * 100) if total_outstanding > 0 else float(0)
        except:
            npl_ratio = float(0)
        
        # Provision rates for each category
        provision_rates = {
            'NORMAL': 0.01,      # 1%
            'WATCH': 0.05,       # 5%
            'SUBSTANDARD': 0.25, # 25%
            'DOUBTFUL': 0.50,    # 50%
            'LOSS': 1.00         # 100%
        }
        
        # Calculate total provisions
        total_provisions = float(sum(overdue_loans[category]['amount'] * rate 
                             for category, rate in provision_rates.items()))
        
        # NPL Coverage Ratio = Total Provisions / NPL Amount
        try:
            npl_coverage_ratio = (total_provisions / npl_amount * 100) if npl_amount > 0 else float(0)
        except:
            npl_coverage_ratio = float(0)
        
        # Cost of Risk = Total Provisions / Total Outstanding
        try:
            cost_of_risk = (total_provisions / total_outstanding * 100) if total_outstanding > 0 else float(0)
        except:
            cost_of_risk = float(0)
        
        # PAR30 (Portfolio at Risk > 30 days)
        par30_amount = float(sum(overdue_loans[grade]['amount'] 
                         for grade in ['WATCH', 'SUBSTANDARD', 'DOUBTFUL', 'LOSS']))
        try:
            par30_ratio = (par30_amount / total_outstanding * 100) if total_outstanding > 0 else float(0)
        except:
            par30_ratio = float(0)

        # Prepare chart data
        classification_data = {
            'labels': [
                f"NORMAL ({overdue_loans['NORMAL']['description']})",
                f"WATCH ({overdue_loans['WATCH']['description']})",
                f"SUBSTANDARD ({overdue_loans['SUBSTANDARD']['description']})",
                f"DOUBTFUL ({overdue_loans['DOUBTFUL']['description']})",
                f"LOSS ({overdue_loans['LOSS']['description']})"
            ],
            'counts': [
                overdue_loans['NORMAL']['count'],
                overdue_loans['WATCH']['count'],
                overdue_loans['SUBSTANDARD']['count'],
                overdue_loans['DOUBTFUL']['count'],
                overdue_loans['LOSS']['count']
            ],
            'amounts': [
                float(overdue_loans['NORMAL']['amount']),
                float(overdue_loans['WATCH']['amount']),
                float(overdue_loans['SUBSTANDARD']['amount']),
                float(overdue_loans['DOUBTFUL']['amount']),
                float(overdue_loans['LOSS']['amount'])
            ]
        }

        cursor.close()
        conn.close()

        return render_template(
            'user/post_disbursement.html',
            total_loans=len(loan_data),
            total_outstanding=float(total_outstanding),
            total_in_arrears=float(total_in_arrears),
            recovery_rate=float(round(recovery_rate, 2)),
            npl_ratio=float(round(npl_ratio, 2)),
            npl_coverage_ratio=float(round(npl_coverage_ratio, 2)),
            cost_of_risk=float(round(cost_of_risk, 2)),
            par30_ratio=float(round(par30_ratio, 2)),
            total_provisions=float(total_provisions),
            classification_data=classification_data,
            loan_data=loan_data,
            overdue_loans=overdue_loans,
            last_sync=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=None
        )

    except Exception as e:
        current_app.logger.error(f"Error in post disbursement endpoint: {str(e)}")
        flash(f'Error fetching post disbursement data: {str(e)}', 'error')
        
        # Initialize default values for error case with proper float formatting
        default_overdue_loans = {
            'NORMAL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '0-30 days'},
            'WATCH': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '31-90 days'},
            'SUBSTANDARD': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '91-180 days'},
            'DOUBTFUL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '181-360 days'},
            'LOSS': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '>360 days'}
        }
        
        default_values = {
            'total_loans': float(0),
            'total_outstanding': float(0),
            'total_in_arrears': float(0),
            'recovery_rate': float(0),
            'npl_ratio': float(0),
            'npl_coverage_ratio': float(0),
            'cost_of_risk': float(0),
            'par30_ratio': float(0),
            'total_provisions': float(0),
            'classification_data': {
                'labels': [],
                'counts': [],
                'amounts': []
            },
            'loan_data': [],
            'overdue_loans': default_overdue_loans,
            'last_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        }
        
        return render_template('user/post_disbursement.html', **default_values)

@user_bp.route('/analytics', methods=['GET'])
@login_required
def analytics():
    from datetime import datetime
    
    # Get all correspondence data
    correspondence_data = Correspondence.query.all()
    
    # Create sorted version for recent items display
    valid_correspondence = [c for c in correspondence_data if c.delivery_time is not None]
    sorted_correspondence = sorted(valid_correspondence, key=lambda x: x.delivery_time, reverse=True)
    
    # Count by type
    type_counts = {
        'sms': len([c for c in correspondence_data if c.type == 'sms']),
        'email': len([c for c in correspondence_data if c.type == 'email']),
        'call': len([c for c in correspondence_data if c.type == 'call']),
        'letter': len([c for c in correspondence_data if c.type == 'letter']),
        'visit': len([c for c in correspondence_data if c.type == 'visit'])
    }
    
    # Count by status
    status_counts = {
        'pending': len([c for c in correspondence_data if c.status == 'pending']),
        'completed': len([c for c in correspondence_data if c.status == 'completed'])
    }
    
    # Calculate call statistics
    total_calls = type_counts['call']
    successful_calls = len([c for c in correspondence_data if c.type == 'call' and c.call_outcome == 'Answered'])
    unsuccessful_calls = len([c for c in correspondence_data if c.type == 'call' and c.call_outcome in ['No Answer', 'Voicemail']])
    
    # Calculate average call duration
    call_durations = [c.call_duration for c in correspondence_data if c.type == 'call' and c.call_duration is not None]
    average_duration = sum(call_durations) / len(call_durations) if call_durations else 0
    
    # Overall statistics
    total_correspondences = len(correspondence_data)
    pending_correspondences = status_counts['pending']
    completed_correspondences = status_counts['completed']
    failed_deliveries = len([c for c in correspondence_data if c.delivery_status == 'Failed'])
    
    # Pagination
    records_per_page = 10
    total_records = len(correspondence_data)
    total_pages = max((total_records + records_per_page - 1) // records_per_page, 1)  # At least 1 page
    current_page = request.args.get('page', 1, type=int)
    current_page = max(1, min(current_page, total_pages))  # Ensure page is in valid range
    
    return render_template('user/analytics.html',
                         data=sorted_correspondence,
                         type_counts=type_counts,
                         status_counts=status_counts,
                         total_correspondences=total_correspondences,
                         pending_correspondences=pending_correspondences,
                         completed_correspondences=completed_correspondences,
                         failed_deliveries=failed_deliveries,
                         total_calls=total_calls,
                         successful_calls=successful_calls,
                         unsuccessful_calls=unsuccessful_calls,
                         average_duration=average_duration,
                         sms_count=type_counts['sms'],
                         email_count=type_counts['email'],
                         call_count=type_counts['call'],
                         letter_count=type_counts['letter'],
                         visit_count=type_counts['visit'],
                         total_pages=total_pages,
                         current_page=current_page,
                         datetime=datetime)

@user_bp.route('/collection-schedule')
@login_required
def collection_schedule():
    """Render the collection schedule page."""
    return render_template('user/collection_schedule.html')

@user_bp.route('/guarantors')
@login_required
def guarantors_list():
    """Display list of all guarantors"""
    return render_template('user/guarantors_list.html')

@user_bp.route('/guarantors/<customer_no>')
@login_required
def customer_guarantors(customer_no):
    """Display guarantors for a specific customer"""
    # Get customer info from mock core banking
    try:
        customer_response = requests.get(f'http://localhost:5003/api/clients/{customer_no}')
        customer = customer_response.json() if customer_response.status_code == 200 else None
        if not customer:
            flash('Customer not found', 'error')
            return redirect(url_for('user.guarantors_list'))
    except Exception as e:
        current_app.logger.error(f"Error fetching customer: {str(e)}")
        flash('Error fetching customer information', 'error')
        return redirect(url_for('user.guarantors_list'))

    guarantors = GuarantorService.get_customer_guarantors(customer_no)
    return render_template('user/customer_guarantors.html', 
                         guarantors=guarantors, 
                         customer=customer,
                         customer_no=customer_no)

@user_bp.route('/api/guarantors/sync/<customer_no>', methods=['POST'])
@login_required
def sync_guarantors(customer_no):
    """Sync guarantors from core banking system"""
    success = GuarantorService.sync_guarantors(customer_no)
    if success:
        return jsonify({'message': 'Guarantors synced successfully'}), 200
    return jsonify({'error': 'Failed to sync guarantors'}), 500

@user_bp.route('/guarantors/<guarantor_no>/details')
@login_required
def guarantor_details(guarantor_no):
    """Display detailed information about a specific guarantor"""
    try:
        # Get guarantor details from mock core banking
        response = requests.get('http://localhost:5003/api/guarantors/search')
        if response.status_code == 200:
            guarantors = response.json()
            guarantor = next((g for g in guarantors if g['id_no'] == guarantor_no), None)
            if guarantor:
                return render_template('user/guarantor_detail.html', 
                                    guarantor=guarantor)
        
        flash('Guarantor not found', 'error')
        return redirect(url_for('user.guarantors_list'))
    except Exception as e:
        current_app.logger.error(f"Error fetching guarantor details: {str(e)}")
        flash('Error fetching guarantor details', 'error')
        return redirect(url_for('user.guarantors_list'))

@user_bp.route('/api/guarantors/<guarantor_no>/status', methods=['POST'])
@login_required
def update_guarantor_status(guarantor_no):
    """Update guarantor status"""
    data = request.get_json()
    success = GuarantorService.update_status(guarantor_no, data['status'], data['reason'])
    
    if success:
        return jsonify({'message': 'Status updated successfully'})
    return jsonify({'error': 'Failed to update status'}), 400

@user_bp.route('/api/guarantors/<guarantor_no>/export', methods=['GET'])
@login_required
def export_guarantor_details(guarantor_no):
    """Export guarantor details as PDF"""
    pdf_data = GuarantorService.generate_pdf_report(guarantor_no)
    if pdf_data:
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'guarantor_{guarantor_no}_details.pdf'
        )
    return jsonify({'error': 'Failed to generate PDF'}), 400

@user_bp.route('/api/guarantors', methods=['POST'])
@login_required
def create_guarantor():
    """Create a new guarantor"""
    data = request.get_json()
    guarantor = GuarantorService.create_guarantor(data)
    
    if guarantor:
        return jsonify({'message': 'Guarantor created successfully', 'guarantor': guarantor.to_dict()})
    return jsonify({'error': 'Failed to create guarantor'}), 400

@user_bp.route('/api/guarantors/<guarantor_no>', methods=['PUT'])
@login_required
def update_guarantor(guarantor_no):
    """Update guarantor information"""
    data = request.get_json()
    success = GuarantorService.update_guarantor(guarantor_no, data)
    
    if success:
        return jsonify({'message': 'Guarantor updated successfully'})
    return jsonify({'error': 'Failed to update guarantor'}), 400

@user_bp.route('/api/customers/<customer_id>/guarantors/export', methods=['GET'])
@login_required
def export_customer_guarantors(customer_id):
    """Export customer's guarantors list as Excel"""
    excel_data = GuarantorService.generate_excel_report(customer_id)
    if excel_data:
        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'customer_{customer_id}_guarantors.xlsx'
        )
    return jsonify({'error': 'Failed to generate Excel report'}), 400



@user_bp.route('/api/guarantors', methods=['GET'])
@login_required
def get_guarantors():
    conn = None
    cursor = None
    try:
        # Ensure user is authenticated
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401

        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')

        # Get active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 500

        # Get database configuration from core banking system
        db_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': core_system.auth_credentials_dict.get('username', 'root'),
            'password': core_system.auth_credentials_dict.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        try:
            # Establish database connection
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Build the query
            query = """
                SELECT 
                    g.GuarantorID,
                    g.LoanAppID,
                    g.GuarantorMemberID,
                    g.GuaranteedAmount,
                    g.DateAdded,
                    g.Status,
                    m.NationalID,
                    m.FirstName,
                    m.MiddleName,
                    m.LastName,
                    m.MemberNo,
                    m.MemberID,
                    l.LoanNo,
                    l.MemberID as BorrowerID,
                    bm.MemberNo as BorrowerMemberNo,
                    bm.FirstName as BorrowerFirstName,
                    bm.MiddleName as BorrowerMiddleName,
                    bm.LastName as BorrowerLastName
                FROM guarantors g
                JOIN members m ON g.GuarantorMemberID = m.MemberID
                JOIN LoanApplications l ON g.LoanAppID = l.LoanAppID
                JOIN members bm ON l.MemberID = bm.MemberID
                WHERE 1=1
            """
            
            params = []
            
            # Apply search filter if provided
            if search:
                query += """ 
                    AND (
                        m.NationalID LIKE %s 
                        OR CONCAT(m.FirstName, ' ', IFNULL(m.MiddleName, ''), ' ', m.LastName) LIKE %s
                        OR m.NationalID LIKE %s
                    )
                """
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])

            # Apply status filter if provided
            if status:
                query += " AND g.Status = %s"
                params.append(status)

            # Add ordering
            query += " ORDER BY g.DateAdded DESC"

            # Add pagination
            query += " LIMIT %s OFFSET %s"
            offset = (page - 1) * per_page
            params.extend([per_page, offset])

            # Execute the main query
            cursor.execute(query, params)
            guarantors = cursor.fetchall()

            # Get total count for pagination
            count_query = """
                SELECT COUNT(*) as total 
                FROM guarantors g
                JOIN members m ON g.GuarantorMemberID = m.MemberID
                JOIN LoanApplications l ON g.LoanAppID = l.LoanAppID
                WHERE 1=1
            """
            count_params = []
            
            if search:
                count_query += """ 
                    AND (
                        m.NationalID LIKE %s 
                        OR CONCAT(m.FirstName, ' ', IFNULL(m.MiddleName, ''), ' ', m.LastName) LIKE %s
                        OR m.NationalID LIKE %s
                    )
                """
                count_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

            if status:
                count_query += " AND g.Status = %s"
                count_params.append(status)

            cursor.execute(count_query, count_params)
            total = cursor.fetchone()['total']

            # Prepare response
            guarantors_list = []
            for g in guarantors:
                guarantor_data = {
                    'guarantor_id': g['GuarantorID'],
                    'loan_app_id': g['LoanAppID'],
                    'loan_no': g['LoanNo'],
                    'guarantor_member_id': g['GuarantorMemberID'],
                    'member_no': g['MemberID'],
                    'guarantor_name': f"{g['FirstName']} {g['MiddleName'] or ''} {g['LastName']}".strip(),
                    'id_number': g['NationalID'],
                    'guaranteed_amount': float(g['GuaranteedAmount']),
                    'date_added': g['DateAdded'].isoformat() if g['DateAdded'] else None,
                    'status': g['Status'],
                    'borrower_member_no': g['BorrowerMemberNo'],
                    'borrower_name': f"{g['BorrowerFirstName']} {g['BorrowerMiddleName'] or ''} {g['BorrowerLastName']}".strip()
                }
                guarantors_list.append(guarantor_data)

            response = {
                'guarantors': guarantors_list,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'current_page': page,
                'per_page': per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }

            return jsonify(response), 200

        except mysql.connector.Error as e:
            current_app.logger.error(f"Database error in get_guarantors: {str(e)}")
            return jsonify({'error': 'Database error occurred'}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    except Exception as e:
        current_app.logger.error(f"Error in get_guarantors: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@user_bp.route('/api/guarantors/sync', methods=['POST'])
@login_required
def sync_all_guarantors():
    """Sync all guarantors from core banking system"""
    try:
        # Get all clients
        clients = Client.query.all()
        success_count = 0
        
        # Sync guarantors for each client
        for client in clients:
            if GuarantorService.sync_guarantors(client.customer_id):
                success_count += 1
        
        if success_count > 0:
            return jsonify({'message': f'Successfully synced guarantors for {success_count} clients'})
        return jsonify({'error': 'No guarantors were synced'}), 400
    except Exception as e:
        current_app.logger.error(f"Error syncing all guarantors: {str(e)}")
        return jsonify({'error': 'Failed to sync guarantors'}), 500

@user_bp.route('/notifications/create', methods=['GET'])
@login_required
def create_notification():
    """Display the notification creation form"""
    return render_template('user/create_notification.html')

@user_bp.route('/api/metrics')
@login_required
def get_metrics():
    """Get updated metrics for the dashboard."""
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get loan data using the same query as post_disbursement
        query = """
            SELECT 
                l.LoanID,
                l.OutstandingBalance,
                l.ArrearsAmount,
                l.ArrearsDays,
                la.LoanNo,
                la.LoanAmount,
                ld.LoanStatus
            FROM LoanLedgerEntries l
            JOIN (
                SELECT LoanID, MAX(LedgerID) as latest_id
                FROM LoanLedgerEntries
                GROUP BY LoanID
            ) latest ON l.LoanID = latest.LoanID AND l.LedgerID = latest.latest_id
            JOIN LoanDisbursements ld ON l.LoanID = ld.LoanAppID
            JOIN LoanApplications la ON ld.LoanAppID = la.LoanAppID
            WHERE ld.LoanStatus = 'Active'
            ORDER BY l.LoanID
        """
        
        cursor.execute(query)
        loan_data = cursor.fetchall()
        
        # Initialize loan classification counters
        overdue_loans = {
            'NORMAL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '0-30 days'},
            'WATCH': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '31-90 days'},
            'SUBSTANDARD': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '91-180 days'},
            'DOUBTFUL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '181-360 days'},
            'LOSS': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '>360 days'}
        }

        # Process loan data
        total_outstanding = float(0)
        total_in_arrears = float(0)
        
        for loan in loan_data:
            try:
                # Extract values from loan ledger entries with proper error handling
                loan_id = loan.get('LoanID', 'Unknown')
                loan_no = loan.get('LoanNo', 'Unknown')
                outstanding_balance = float(loan.get('OutstandingBalance', 0))
                arrears_amount = float(loan.get('ArrearsAmount', 0))
                arrears_days = int(loan.get('ArrearsDays', 0))
                
                # Update totals
                total_outstanding += outstanding_balance
                total_in_arrears += arrears_amount
                
                # Classify loan based on arrears days
                if arrears_days <= 30:
                    category = 'NORMAL'
                elif 31 <= arrears_days <= 90:
                    category = 'WATCH'
                elif 91 <= arrears_days <= 180:
                    category = 'SUBSTANDARD'
                elif 181 <= arrears_days <= 360:
                    category = 'DOUBTFUL'
                else:
                    category = 'LOSS'
                
                # Update classification counters
                overdue_loans[category]['count'] += 1
                overdue_loans[category]['amount'] += outstanding_balance
                
            except Exception as e:
                current_app.logger.error(f"Error processing loan {loan.get('LoanID', 'Unknown')}: {str(e)}")
                continue

        # Calculate percentages
        total_amount = sum(cat['amount'] for cat in overdue_loans.values())
        if total_amount > 0:
            for category in overdue_loans:
                overdue_loans[category]['percentage'] = (overdue_loans[category]['amount'] / total_amount * 100)
        
        # Calculate NPL amount and ratio
        npl_amount = float(overdue_loans['SUBSTANDARD']['amount'] + 
                         overdue_loans['DOUBTFUL']['amount'] + 
                         overdue_loans['LOSS']['amount'])
        npl_ratio = (npl_amount / total_outstanding * 100) if total_outstanding > 0 else float(0)
        
        # Calculate recovery rate
        recovery_rate = ((total_outstanding - total_in_arrears) / total_outstanding * 100) if total_outstanding > 0 else float(0)
        
        # Calculate provisions
        total_provisions = float(sum(overdue_loans[category]['amount'] * rate 
            for category, rate in {
                'NORMAL': 0.01,      # 1%
                'WATCH': 0.05,       # 5%
                'SUBSTANDARD': 0.25, # 25%
                'DOUBTFUL': 0.50,    # 50%
                'LOSS': 1.00         # 100%
            }.items()))
        
        # Calculate NPL coverage ratio
        npl_coverage_ratio = (total_provisions / npl_amount * 100) if npl_amount > 0 else float(0)
        
        # Calculate cost of risk
        cost_of_risk = (total_provisions / total_outstanding * 100) if total_outstanding > 0 else float(0)
        
        # Calculate PAR30
        par30_amount = float(sum(overdue_loans[grade]['amount'] 
                         for grade in ['WATCH', 'SUBSTANDARD', 'DOUBTFUL', 'LOSS']))
        par30_ratio = (par30_amount / total_outstanding * 100) if total_outstanding > 0 else float(0)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'metrics': {
                'total_loans': len(loan_data),
                'total_outstanding': float(total_outstanding),
                'total_in_arrears': float(total_in_arrears),
                'recovery_rate': float(round(recovery_rate, 2)),
                'npl_ratio': float(round(npl_ratio, 2)),
                'npl_coverage_ratio': float(round(npl_coverage_ratio, 2)),
                'cost_of_risk': float(round(cost_of_risk, 2)),
                'par30_ratio': float(round(par30_ratio, 2)),
                'total_provisions': float(total_provisions),
                'overdue_loans': overdue_loans
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch metrics',
            'details': str(e)
        }), 500

@user_bp.route('/get_detailed_loans', methods=['GET'])
@login_required
def get_detailed_loans():
    try:
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 400

        # Get loan details endpoint
        loan_details_endpoint = CoreBankingEndpoint.query.filter_by(
            system_id=core_system.id,
            name='loan_details',
            is_active=True
        ).first()

        if not loan_details_endpoint:
            return jsonify({'error': 'Loan details endpoint not configured'}), 400

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError):
            auth_credentials = {'username': 'root', 'password': ''}
            
        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username'),
            'password': auth_credentials.get('password'),
            'database': core_system.database_name
        }

        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # List tables to check the correct table name
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        current_app.logger.info(f"Available tables: {tables}")
        
        # Check table schema
        cursor.execute("DESCRIBE LoanCommunicationLog")
        columns = cursor.fetchall()
        current_app.logger.info(f"Table schema: {columns}")
        
        # Check LoanApplications schema
        cursor.execute("DESCRIBE LoanApplications")
        loan_columns = cursor.fetchall()
        current_app.logger.info(f"LoanApplications schema: {loan_columns}")
        
        # Check Members schema
        cursor.execute("DESCRIBE Members")
        member_columns = cursor.fetchall()
        current_app.logger.info(f"Members schema: {member_columns}")
        
        # Check Users schema
        cursor.execute("DESCRIBE Users")
        user_columns = cursor.fetchall()
        current_app.logger.info(f"Users schema: {user_columns}")
        
        # Build query from endpoint configuration
        endpoint_params = json.loads(loan_details_endpoint.parameters)
        
        # Construct the query
        fields = ", ".join(endpoint_params['fields'])
        tables = endpoint_params['tables'][0]
        joins = " ".join([f"JOIN {join['table']} ON {join['on']}" for join in endpoint_params['joins']])
        filters = " AND ".join([f"{filter_info['field']} = '{filter_info['value']}'" 
                              for filter_info in endpoint_params['filters'].values()])

        query = f"""
            SELECT {fields}
            FROM {tables}
            JOIN (
                SELECT LoanID, MAX(LedgerID) as latest_id
                FROM LoanLedgerEntries
                GROUP BY LoanID
            ) latest ON LoanLedgerEntries.LoanID = latest.LoanID 
                AND LoanLedgerEntries.LedgerID = latest.latest_id
            {joins}
            WHERE {filters}
            ORDER BY LoanLedgerEntries.LoanID
        """

        cursor.execute(query)
        loan_data = cursor.fetchall()

        # Format dates for JSON serialization and ensure list format
        formatted_data = []
        for loan in loan_data:
            loan_dict = dict(loan)  # Convert row proxy to dictionary
            if loan_dict.get('DisbursementDate'):
                loan_dict['DisbursementDate'] = loan_dict['DisbursementDate'].strftime('%Y-%m-%d')
            if loan_dict.get('MaturityDate'):
                loan_dict['MaturityDate'] = loan_dict['MaturityDate'].strftime('%Y-%m-%d')
            formatted_data.append(loan_dict)

        return jsonify({'data': formatted_data})

    except Exception as e:
        current_app.logger.error(f"Error fetching detailed loan data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@user_bp.route('/loans/communications', methods=['GET'])
@login_required
def get_loan_communications():
    """Get communication history with pagination and filters"""
    try:
        # Get filter parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        member_id = request.args.get('member_id')
        loan_id = request.args.get('loan_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        comm_type = request.args.get('type')

        current_app.logger.info(f"Fetching communications with filters: member_id={member_id}, loan_id={loan_id}, start_date={start_date}, end_date={end_date}, type={comm_type}")

        # Get core banking system details
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            raise Exception("No active core banking system configured")

        # Get auth credentials
        auth_creds = core_system.auth_credentials_dict

        # Connect to core banking database
        conn = mysql.connector.connect(
            host=core_system.base_url,
            port=core_system.port or 3306,
            user=auth_creds.get('username'),
            password=auth_creds.get('password'),
            database=core_system.database_name
        )
        
        cursor = conn.cursor(dictionary=True)

        # List tables to check the correct table name
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        current_app.logger.info(f"Available tables: {tables}")
        
        # Check table schema
        cursor.execute("DESCRIBE LoanCommunicationLog")
        columns = cursor.fetchall()
        current_app.logger.info(f"Table schema: {columns}")
        
        # Check LoanApplications schema
        cursor.execute("DESCRIBE LoanApplications")
        loan_columns = cursor.fetchall()
        current_app.logger.info(f"LoanApplications schema: {loan_columns}")
        
        # Check Members schema
        cursor.execute("DESCRIBE Members")
        member_columns = cursor.fetchall()
        current_app.logger.info(f"Members schema: {member_columns}")
        
        # Check Users schema
        cursor.execute("DESCRIBE Users")
        user_columns = cursor.fetchall()
        current_app.logger.info(f"Users schema: {user_columns}")
        
        # Build base query
        query = """
            SELECT 
                lcl.LogID as id,
                la.LoanNo as loan_no,
                m.FullName as client_name,
                lcl.CommunicationType as comm_type,
                lcl.MessageContent as message,
                lcl.DeliveryStatus as status,
                lcl.SentDate as created_at,
                lcl.ResponseReceived as delivery_status,
                u.FullName as sent_by
            FROM LoanCommunicationLog lcl
            JOIN LoanApplications la ON la.LoanAppID = lcl.LoanID
            JOIN Members m ON m.MemberID = lcl.MemberID
            JOIN Users u ON u.UserID = lcl.SentBy
        """
        conditions = []
        
        # Add filters
        if member_id:
            conditions.append(f"lcl.MemberID = '{member_id}'")
        
        if loan_id:
            conditions.append(f"lcl.LoanID = '{loan_id}'")
        
        if start_date:
            conditions.append(f"DATE(lcl.SentDate) >= '{start_date}'")
        
        if end_date:
            conditions.append(f"DATE(lcl.SentDate) <= '{end_date}'")
        
        if comm_type:
            conditions.append(f"lcl.CommunicationType = '{comm_type}'")
        
        # Add WHERE clause if conditions exist
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        # Add ordering
        query += " ORDER BY lcl.SentDate DESC"
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
        cursor.execute(count_query)
        total = cursor.fetchone()['total']
        current_app.logger.info(f"Total count: {total}")
        
        # Add pagination
        query += f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"
        
        # Execute final query
        cursor.execute(query)
        communications = cursor.fetchall()
        current_app.logger.info(f"Retrieved {len(communications)} records")
        
        # Format results
        formatted_comms = []
        for comm in communications:
            formatted_comms.append({
                'id': comm['id'],
                'member_name': comm['client_name'],
                'member_no': member_id if member_id else '',
                'loan_no': comm['loan_no'],
                'type': comm['comm_type'].lower() if comm['comm_type'] else '',
                'message': comm['message'],
                'status': comm['status'].lower() if comm['status'] else '',
                'created_at': comm['created_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(comm['created_at'], datetime) else comm['created_at'],
                'response': comm['delivery_status'],
                'sent_by': comm['sent_by']
            })
        
        response_data = {
            'communications': formatted_comms,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
        current_app.logger.info(f"Returning response: {response_data}")
        
        cursor.close()
        conn.close()
        
        return jsonify(response_data)
            
    except Exception as e:
        current_app.logger.error(f"Error fetching core banking communications: {str(e)}")
        return jsonify({
            'error': str(e),
            'communications': [],
            'total': 0,
            'page': 1,
            'per_page': 10,
            'total_pages': 0
        }), 500

@user_bp.route('/clients/<int:client_id>/loans', methods=['GET'])
@login_required
def get_client_loans(client_id):
    """Get loans for a specific client"""
    try:
        # Build query
        query = db.session.query(
            Loan.id,
            Loan.account_no,
            LoanProduct.name.label('product_name')
        ).join(
            LoanProduct, Loan.product_id == LoanProduct.id
        ).filter(
            Loan.member_id == client_id
        ).order_by(
            Loan.created_at.desc()
        )
        
        loans = query.all()
        
        return jsonify({
            'loans': [{
                'id': loan.id,
                'account_no': loan.account_no,
                'product_name': loan.product_name
            } for loan in loans]
        })
            
    except Exception as e:
        current_app.logger.error(f"Error fetching client loans: {str(e)}")
        return jsonify({
            'error': str(e),
            'loans': []
        }), 500

@user_bp.route('/api/metrics')
@login_required
def api_get_metrics():
    """Get updated metrics for the dashboard."""
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get loan data using the same query as post_disbursement
        query = """
            SELECT 
                l.LoanID,
                l.OutstandingBalance,
                l.ArrearsAmount,
                l.ArrearsDays,
                la.LoanNo,
                la.LoanAmount,
                ld.LoanStatus
            FROM LoanLedgerEntries l
            JOIN (
                SELECT LoanID, MAX(LedgerID) as latest_id
                FROM LoanLedgerEntries
                GROUP BY LoanID
            ) latest ON l.LoanID = latest.LoanID AND l.LedgerID = latest.latest_id
            JOIN LoanDisbursements ld ON l.LoanID = ld.LoanAppID
            JOIN LoanApplications la ON ld.LoanAppID = la.LoanAppID
            WHERE ld.LoanStatus = 'Active'
            ORDER BY l.LoanID
        """
        
        cursor.execute(query)
        loan_data = cursor.fetchall()
        
        # Initialize loan classification counters
        overdue_loans = {
            'NORMAL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '0-30 days'},
            'WATCH': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '31-90 days'},
            'SUBSTANDARD': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '91-180 days'},
            'DOUBTFUL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '181-360 days'},
            'LOSS': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '>360 days'}
        }

        # Process loan data
        total_outstanding = float(0)
        total_in_arrears = float(0)
        
        for loan in loan_data:
            try:
                # Extract values from loan ledger entries with proper error handling
                loan_id = loan.get('LoanID', 'Unknown')
                loan_no = loan.get('LoanNo', 'Unknown')
                outstanding_balance = float(loan.get('OutstandingBalance', 0))
                arrears_amount = float(loan.get('ArrearsAmount', 0))
                arrears_days = int(loan.get('ArrearsDays', 0))
                
                # Update totals
                total_outstanding += outstanding_balance
                total_in_arrears += arrears_amount
                
                # Classify loan based on arrears days
                if arrears_days <= 30:
                    category = 'NORMAL'
                elif 31 <= arrears_days <= 90:
                    category = 'WATCH'
                elif 91 <= arrears_days <= 180:
                    category = 'SUBSTANDARD'
                elif 181 <= arrears_days <= 360:
                    category = 'DOUBTFUL'
                else:
                    category = 'LOSS'
                
                # Update classification counters
                overdue_loans[category]['count'] += 1
                overdue_loans[category]['amount'] += outstanding_balance
                
            except Exception as e:
                current_app.logger.error(f"Error processing loan {loan.get('LoanID', 'Unknown')}: {str(e)}")
                continue

        # Calculate percentages
        total_amount = sum(cat['amount'] for cat in overdue_loans.values())
        if total_amount > 0:
            for category in overdue_loans:
                overdue_loans[category]['percentage'] = (overdue_loans[category]['amount'] / total_amount * 100)
        
        # Calculate NPL amount and ratio
        npl_amount = float(overdue_loans['SUBSTANDARD']['amount'] + 
                         overdue_loans['DOUBTFUL']['amount'] + 
                         overdue_loans['LOSS']['amount'])
        npl_ratio = (npl_amount / total_outstanding * 100) if total_outstanding > 0 else float(0)
        
        # Calculate recovery rate
        recovery_rate = ((total_outstanding - total_in_arrears) / total_outstanding * 100) if total_outstanding > 0 else float(0)
        
        # Calculate provisions
        total_provisions = float(sum(overdue_loans[category]['amount'] * rate 
            for category, rate in {
                'NORMAL': 0.01,      # 1%
                'WATCH': 0.05,       # 5%
                'SUBSTANDARD': 0.25, # 25%
                'DOUBTFUL': 0.50,    # 50%
                'LOSS': 1.00         # 100%
            }.items()))
        
        # Calculate NPL coverage ratio
        npl_coverage_ratio = (total_provisions / npl_amount * 100) if npl_amount > 0 else float(0)
        
        # Calculate cost of risk
        cost_of_risk = (total_provisions / total_outstanding * 100) if total_outstanding > 0 else float(0)
        
        # Calculate PAR30
        par30_amount = float(sum(overdue_loans[grade]['amount'] 
                         for grade in ['WATCH', 'SUBSTANDARD', 'DOUBTFUL', 'LOSS']))
        par30_ratio = (par30_amount / total_outstanding * 100) if total_outstanding > 0 else float(0)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'metrics': {
                'total_loans': len(loan_data),
                'total_outstanding': float(total_outstanding),
                'total_in_arrears': float(total_in_arrears),
                'recovery_rate': float(round(recovery_rate, 2)),
                'npl_ratio': float(round(npl_ratio, 2)),
                'npl_coverage_ratio': float(round(npl_coverage_ratio, 2)),
                'cost_of_risk': float(round(cost_of_risk, 2)),
                'par30_ratio': float(round(par30_ratio, 2)),
                'total_provisions': float(total_provisions),
                'overdue_loans': overdue_loans
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch metrics',
            'details': str(e)
        }), 500

@user_bp.route('/loan-rescheduling')
@login_required
def loan_rescheduling():
    """Render the loan rescheduling page"""
    try:
        return render_template('user/loan_rescheduling.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering loan rescheduling page: {str(e)}")
        flash('An error occurred while loading the loan rescheduling page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/refinancing')
@login_required
def refinancing():
    """Render the refinancing page"""
    try:
        return render_template('user/refinancing.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering refinancing page: {str(e)}")
        flash('An error occurred while loading the refinancing page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/settlement-plans')
@login_required
def settlement_plans():
    """Render the settlement plans page"""
    try:
        return render_template('user/settlement_plans.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering settlement plans page: {str(e)}")
        flash('An error occurred while loading the settlement plans page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/demand-letters')
@login_required
def demand_letters():
    """Render the demand letters page"""
    try:
        return render_template('user/demand_letters.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering demand letters page: {str(e)}")
        flash('An error occurred while loading the demand letters page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/crb-reports')
@login_required
def crb_reports():
    """Render the CRB reports page"""
    try:
        return render_template('user/crb_reports.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering CRB reports page: {str(e)}")
        flash('An error occurred while loading the CRB reports page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/legal-cases')
@login_required
def legal_cases():
    """Render the legal cases page"""
    try:
        return render_template('user/legal_cases.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering legal cases page: {str(e)}")
        flash('An error occurred while loading the legal cases page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/auction-process')
@login_required
def auction_process():
    """Render the auction process page"""
    try:
        return render_template('user/auction_process.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering auction process page: {str(e)}")
        flash('An error occurred while loading the auction process page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/field-visits')
@login_required
def field_visits():
    """Render the field visits page"""
    try:
        return render_template('user/field_visits.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering field visits page: {str(e)}")
        flash('An error occurred while loading the field visits page', 'error')
        return redirect(url_for('user.dashboard'))
