import requests
import re
import sqlparse
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import mysql.connector
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
from decimal import Decimal
import traceback
import os
import json
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_, text, MetaData, Table
import time
from flask import current_app
from routes.collection_schedule import collection_schedule_bp
from routes.crb import crb_bp
from services.collection_schedule_service import CollectionScheduleService
import io
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint
from forms.demand_letter_forms import DemandLetterForm
from forms.letter_template_forms import LetterTypeForm
from models.letter_template import LetterType, DemandLetter
from models.legal_case import LegalCase
from models.auction import Auction
from models.loan_reschedule import LoanReschedule
from models.loan_refinance import RefinanceApplication

user_bp = Blueprint('user', __name__)

# Register collection schedule blueprint without additional prefix
user_bp.register_blueprint(collection_schedule_bp)
user_bp.register_blueprint(crb_bp)

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
def guarantors():
    """Display guarantors list page"""
    return render_template('user/guarantors_list.html')

@user_bp.route('/api/guarantors/sync/<customer_no>', methods=['POST'])
@login_required
def sync_guarantors(customer_no):
    """Sync guarantors from core banking system"""
    success = GuarantorService.sync_guarantors(customer_no)
    if success:
        return jsonify({'message': 'Guarantors synced successfully'}), 200
    return jsonify({'error': 'Failed to sync guarantors'}), 500

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
                FROM Guarantors g
                JOIN Members m ON g.GuarantorMemberID = m.MemberID
                JOIN LoanApplications l ON g.LoanAppID = l.LoanAppID
                JOIN Members bm ON l.MemberID = bm.MemberID
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
                FROM Guarantors g
                JOIN Members m ON g.GuarantorMemberID = m.MemberID
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
                    'member_no': g['MemberNo'],  # Fixed: Changed from MemberID to MemberNo
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
        # Get database configuration for the core banking database
        db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'sacco_db'  # Use core_banking database
        }

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
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
                                         'NORMAL': 0.01,  # 1%
                                         'WATCH': 0.05,  # 5%
                                         'SUBSTANDARD': 0.25,  # 25%
                                         'DOUBTFUL': 0.50,  # 50%
                                         'LOSS': 1.00  # 100%
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
    except mysql.connector.Error as e:
        current_app.logger.error(f"Database error in get_metrics: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
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
            user=auth_creds.get('username', 'root'),
            password=auth_creds.get('password', ''),
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
        # Get filter parameters from the request
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')

        # Build the query with filters
        query = LoanReschedule.query

        if status and status != 'All':
            query = query.filter_by(status=status)

        if start_date:
            query = query.filter(LoanReschedule.request_date >= start_date)

        if end_date:
            query = query.filter(LoanReschedule.request_date <= end_date)

        if search:
            query = query.filter(or_(
                LoanReschedule.member_id.ilike(f"%{search}%"),
                LoanReschedule.loan_id.ilike(f"%{search}%")
            ))

        # Fetch loan rescheduling requests from the database
        loan_reschedules = query.all()
        return render_template('user/loan_rescheduling.html', loan_reschedules=loan_reschedules)
    except Exception as e:
        current_app.logger.error(f"Error rendering loan rescheduling page: {str(e)}")
        flash('An error occurred while loading the loan rescheduling page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/refinancing')
@login_required
def refinancing():
    """Render the refinancing page"""
    try:
        # Query the database for all refinancing applications
        refinancing_applications = RefinanceApplication.query.all()

        # Render the template with the refinancing applications data
        return render_template('user/refinancing.html', refinancing_applications=refinancing_applications)
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

@user_bp.route('/demand-letters', methods=['GET', 'POST'])
@login_required
def demand_letters():
    """Manage demand letters"""
    form = DemandLetterForm()
    
    # Populate letter types
    letter_types = LetterType.query.filter_by(is_active=True).all()
    form.letter_type_id.choices = [(lt.id, lt.name) for lt in letter_types]
    
    # Reset letter template choices to prevent validation error
    form.letter_template_id.choices = []
    
    if form.validate_on_submit():
        try:
            # Extract member details from the form
            member_id = form.member_id.data
            
            # You might want to add a method to fetch full member details from the API
            # For now, we'll use the ID as the name
            new_demand_letter = DemandLetter(
                member_id=str(form.member_id.data),  # ID from external API
                member_name=form.member_name.data,  # Name from hidden field
                member_number=form.member_number.data,  # Member number from hidden field
                letter_type_id=form.letter_type_id.data,
                letter_template_id=form.letter_template_id.data,
                amount_outstanding=form.amount_outstanding.data,
                letter_content=form.letter_content.data,
                status='Draft',
                created_by=current_user.id,  # Assuming current_user is the logged-in staff
                sent_at=None  # Not sent yet
            )
            
            db.session.add(new_demand_letter)
            db.session.commit()
            
            flash('Demand letter created successfully', 'success')
            return redirect(url_for('user.demand_letters'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating demand letter: {str(e)}")
            flash('Failed to create demand letter', 'error')
    
    # Get existing demand letters
    demand_letters = DemandLetter.query.filter_by(
        created_by=current_user.id
    ).order_by(DemandLetter.created_at.desc()).all()
    
    return render_template('user/demand_letters.html', 
                           form=form, 
                           demand_letters=demand_letters)



@user_bp.route('/api/letter-templates', methods=['GET'])
@login_required
def get_letter_templates():
    """Get letter templates for a specific letter type"""
    letter_type_id = request.args.get('letter_type_id')
    
    if not letter_type_id:
        return jsonify({'templates': []}), 400
    
    try:
        templates = LetterTemplate.query.filter_by(
            letter_type_id=int(letter_type_id), 
            is_active=True
        ).all()
        
        return jsonify({
            'templates': [
                {
                    'id': template.id, 
                    'name': template.name
                } for template in templates
            ]
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching letter templates: {str(e)}")
        return jsonify({'templates': []}), 500

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
    """Render the legal cases page with all legal cases and statistics"""
    try:
        # Fetch all legal cases, ordered by most recent first
        legal_cases = LegalCase.query.order_by(LegalCase.created_at.desc()).all()
        
        # Calculate statistics
        active_cases = LegalCase.query.filter_by(status='Active').count()
        resolved_cases = LegalCase.query.filter_by(status='Closed').count()
        
        # Calculate upcoming hearings (cases with hearing dates in the future)
        from datetime import datetime
        upcoming_hearings = LegalCase.query.filter(
            LegalCase.next_hearing_date >= datetime.now(),
            LegalCase.status != 'Closed'
        ).count()
        
        # Calculate total amount in litigation
        from sqlalchemy import func
        total_amount = db.session.query(func.sum(LegalCase.amount_claimed))\
            .filter(LegalCase.status != 'Closed')\
            .scalar() or 0
        
        # Format amount for display
        if total_amount >= 1_000_000:
            amount_display = f"KES {total_amount/1_000_000:.1f}M"
        elif total_amount >= 1_000:
            amount_display = f"KES {total_amount/1_000:.1f}K"
        else:
            amount_display = f"KES {total_amount:,.0f}"

        return render_template('user/legal_cases.html',
                           legal_cases=legal_cases,
                           active_cases=active_cases,
                           resolved_cases=resolved_cases,
                           upcoming_hearings=upcoming_hearings,
                           amount_in_litigation=amount_display)
    except Exception as e:
        current_app.logger.error(f"Error rendering legal cases page: {str(e)}")
        flash('An error occurred while loading the legal cases page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/auction-process')
@login_required
def auction_process():
    """Render the auction process page"""
    try:
        # Fetch all auctions, ordered by most recent first
        auctions = Auction.query.order_by(Auction.created_at.desc()).all()
        
        # Calculate statistics
        pending_auctions = Auction.query.filter_by(status='Scheduled').count()
        completed_auctions = Auction.query.filter_by(status='Completed').count()
        properties_listed = Auction.query.count()
        
        # Calculate total recovery amount from completed auctions
        from sqlalchemy import func
        total_recovery = db.session.query(func.sum(Auction.reserve_price))\
            .filter(Auction.status == 'Completed')\
            .scalar() or 0
        
        return render_template('user/auction_process.html',
                             auctions=auctions,
                             pending_auctions=pending_auctions,
                             completed_auctions=completed_auctions,
                             properties_listed=properties_listed,
                             total_recovery=total_recovery)
    except Exception as e:
        current_app.logger.error(f"Error rendering auction process page: {str(e)}")
        flash('An error occurred while loading the auction process page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/create_auction', methods=['POST'])
@login_required
def create_auction():
    """Create a new auction"""
    try:
        # Get form data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['loan_id', 'property_description', 'valuation_amount', 
                          'reserve_price', 'auction_date', 'auction_venue']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Convert dates to datetime objects
        from datetime import datetime
        auction_date = datetime.strptime(data['auction_date'], '%Y-%m-%dT%H:%M')
        advertisement_date = datetime.strptime(data['advertisement_date'], '%Y-%m-%d') if data.get('advertisement_date') else None
        
        # Create new auction
        new_auction = Auction(
            loan_id=data['loan_id'],
            client_name=data['client_name'],
            property_type=data['property_type'],
            property_description=data['property_description'],
            valuation_amount=data['valuation_amount'],
            reserve_price=data['reserve_price'],
            auction_date=auction_date,
            auction_venue=data['auction_venue'],
            status=data.get('status'),
            auctioneer_name=data.get('auctioneer_name'),
            auctioneer_contact=data.get('auctioneer_contact'),
            advertisement_date=advertisement_date,
            advertisement_medium=data.get('advertisement_medium'),
            notes=data.get('notes')
        )
        
        db.session.add(new_auction)
        db.session.commit()
        
        return jsonify({'message': 'Auction created successfully', 'id': new_auction.id})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating auction: {str(e)}")
        return jsonify({'error': 'An error occurred while creating the auction'}), 500

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

@user_bp.route('/api/guarantor/<int:guarantor_id>/communications', methods=['GET'])
@login_required
def get_guarantor_communications(guarantor_id):
    """Get communications for a guarantor"""
    try:
        # Get active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 500

        # Get database configuration
        db_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': core_system.auth_credentials_dict.get('username', 'root'),
            'password': core_system.auth_credentials_dict.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        # Connect to core banking database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get communications
        query = """
            SELECT c.*, u.Username as CreatedByUser
            FROM GuarantorCommunications c
            JOIN Users u ON c.CreatedBy = u.UserID
            WHERE c.GuarantorID = %s
            ORDER BY c.CreatedAt DESC
        """
        
        cursor.execute(query, (guarantor_id,))
        communications = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({'communications': communications})

    except Exception as e:
        current_app.logger.error(f"Error in get_guarantor_communications: {str(e)}")
        return jsonify({'error': 'Failed to fetch communications'}), 500

@user_bp.route('/api/guarantor/<int:guarantor_id>/communications', methods=['POST'])
@login_required
def create_guarantor_communication(guarantor_id):
    """Create a new communication for a guarantor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['type', 'message', 'status']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Get active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 500

        # Get database configuration
        db_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': core_system.auth_credentials_dict.get('username', 'root'),
            'password': core_system.auth_credentials_dict.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        # Connect to core banking database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Build query based on communication type
        base_fields = ['GuarantorID', 'Type', 'Message', 'Status', 'CreatedBy']
        base_values = [guarantor_id, data['type'], data['message'], data['status'], current_user.id]
        
        additional_fields = []
        additional_values = []
        
        if data['type'] in ['sms', 'email']:
            additional_fields.append('Recipient')
            additional_values.append(data.get('recipient'))
        elif data['type'] == 'call':
            additional_fields.extend(['CallDuration', 'CallOutcome'])
            additional_values.extend([data.get('call_duration'), data.get('call_outcome')])
        elif data['type'] == 'visit':
            additional_fields.extend(['Location', 'VisitPurpose', 'VisitOutcome'])
            additional_values.extend([
                data.get('location'),
                data.get('visit_purpose'),
                data.get('visit_outcome')
            ])
        
        # Combine fields and values
        all_fields = base_fields + additional_fields
        all_values = base_values + additional_values
        
        # Create the INSERT query
        placeholders = ', '.join(['%s'] * len(all_fields))
        query = f"""
            INSERT INTO GuarantorCommunications 
            ({', '.join(all_fields)})
            VALUES ({placeholders})
        """
        
        cursor.execute(query, all_values)
        conn.commit()
        
        new_id = cursor.lastrowid
        
        # Fetch the newly created communication
        select_query = """
            SELECT c.*, u.Username as CreatedByUser
            FROM GuarantorCommunications c
            JOIN Users u ON c.CreatedBy = u.UserID
            WHERE c.CommunicationID = %s
        """
        cursor.execute(select_query, (new_id,))
        new_communication = cursor.fetchone()
        
        cursor.close()
        conn.close()

        return jsonify({'communication': new_communication})

    except Exception as e:
        current_app.logger.error(f"Error in create_guarantor_communication: {str(e)}")
        return jsonify({'error': 'Failed to create communication'}), 500

@user_bp.route('/api/guarantor/communications/<int:communication_id>', methods=['GET'])
@login_required
def get_communication(communication_id):
    """Get a specific communication"""
    try:
        # Get active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 500

        # Get database configuration
        db_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': core_system.auth_credentials_dict.get('username', 'root'),
            'password': core_system.auth_credentials_dict.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        # Connect to core banking database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get communication
        query = """
            SELECT c.*, u.Username as CreatedByUser
            FROM GuarantorCommunications c
            JOIN Users u ON c.CreatedBy = u.UserID
            WHERE c.CommunicationID = %s
        """
        cursor.execute(query, (communication_id,))
        communication = cursor.fetchone()

        cursor.close()
        conn.close()

        if not communication:
            return jsonify({'error': 'Communication not found'}), 404

        return jsonify(communication)

    except Exception as e:
        current_app.logger.error(f"Error in get_communication: {str(e)}")
        return jsonify({'error': 'Failed to fetch communication'}), 500

@user_bp.route('/api/guarantor/communications/<int:communication_id>/read', methods=['POST'])
@login_required
def mark_communication_read(communication_id):
    """Mark a communication as read"""
    try:
        # Get active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 500

        # Get database configuration
        db_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': core_system.auth_credentials_dict.get('username', 'root'),
            'password': core_system.auth_credentials_dict.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        # Connect to core banking database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Update communication status
        query = """
            UPDATE GuarantorCommunications
            SET Status = 'delivered'
            WHERE CommunicationID = %s
        """
        cursor.execute(query, (communication_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Error in mark_communication_read: {str(e)}")
        return jsonify({'error': 'Failed to mark communication as read'}), 500

@user_bp.route('/reports/guarantor-claims')
@login_required
def guarantor_claims_report():
    return render_template('user/reports/guarantor_claims.html')

@user_bp.route('/api/reports/guarantor-claims/data', methods=['POST'])
@login_required
def get_guarantor_claims_data():
    filters = request.get_json()
    # TODO: Implement data fetching logic
    # This is sample data for demonstration
    data = {
        'dashboard': {
            'totalClaims': 150,
            'totalAmount': 750000,
            'settledClaims': 85,
            'successRate': 56.67
        },
        'items': [
            {
                'claimId': 'GC001',
                'customerName': 'John Doe',
                'guarantorName': 'Jane Smith',
                'claimAmount': 5000,
                'filingDate': '2025-01-15',
                'status': 'pending',
                'settlementAmount': 0
            }
            # Add more sample items as needed
        ],
        'pagination': {
            'page': 1,
            'start': 1,
            'end': 10,
            'total': 150,
            'totalPages': 15
        }
    }
    return jsonify(data)

@user_bp.route('/api/reports/guarantor-claims/download', methods=['POST'])
@login_required
def download_guarantor_claims():
    filters = request.get_json()
    # TODO: Implement Excel generation logic
    # For now, return a sample Excel file
    return send_file(
        'path/to/generated/excel',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='guarantor_claims_report.xlsx'
    )

@user_bp.route('/reports/collection')
@login_required
def collection_report():
    return render_template('user/reports/collection_report.html')

@user_bp.route('/reports/communication-logs')
@login_required
def communication_logs():
    return render_template('user/reports/communication_logs.html')

@user_bp.route('/reports/legal-status')
@login_required
def legal_status():
    return render_template('user/reports/legal_status.html')

@user_bp.route('/reports/recovery-analytics')
@login_required
def recovery_analytics():
    return render_template('user/reports/recovery_analytics.html')

# API endpoints for report data
@user_bp.route('/api/reports/collection/data', methods=['POST'])
@login_required
def collection_report_data():
    filters = request.json
    # TODO: Implement data fetching logic
    return jsonify({
        'items': [],
        'pagination': {
            'total': 0,
            'page': 1,
            'per_page': 10
        }
    })

@user_bp.route('/api/reports/collection/download', methods=['POST'])
@login_required
def collection_report_download():
    filters = request.json
    # TODO: Implement Excel generation logic
    return send_file(
        'path_to_generated_file',
        as_attachment=True,
        download_name='collection_report.xlsx'
    )

@user_bp.route('/api/reports/communication/data', methods=['POST'])
@login_required
def communication_logs_data():
    filters = request.json
    # TODO: Implement data fetching logic
    return jsonify({
        'items': [],
        'pagination': {
            'total': 0,
            'page': 1,
            'per_page': 10
        }
    })

@user_bp.route('/api/reports/communication/download', methods=['POST'])
@login_required
def communication_logs_download():
    filters = request.json
    # TODO: Implement Excel generation logic
    return send_file(
        'path_to_generated_file',
        as_attachment=True,
        download_name='communication_logs.xlsx'
    )

@user_bp.route('/api/reports/legal/data', methods=['POST'])
@login_required
def legal_status_data():
    filters = request.json
    # TODO: Implement data fetching logic
    return jsonify({
        'items': [],
        'pagination': {
            'total': 0,
            'page': 1,
            'per_page': 10
        }
    })

@user_bp.route('/api/reports/legal/download', methods=['POST'])
@login_required
def legal_status_download():
    filters = request.json
    # TODO: Implement Excel generation logic
    return send_file(
        'path_to_generated_file',
        as_attachment=True,
        download_name='legal_status_report.xlsx'
    )

@user_bp.route('/api/reports/recovery/data', methods=['POST'])
@login_required
def recovery_analytics_data():
    filters = request.json
    # TODO: Implement data fetching logic
    return jsonify({
        'items': [],
        'pagination': {
            'total': 0,
            'page': 1,
            'per_page': 10
        },
        'dashboard': {
            'totalRecovery': 0,
            'recoveryRate': 0,
            'activeCases': 0,
            'avgRecoveryTime': 0
        },
        'charts': {
            'trendData': {
                'labels': [],
                'datasets': []
            },
            'distributionData': {
                'labels': [],
                'datasets': []
            }
        }
    })

@user_bp.route('/api/reports/recovery/download', methods=['POST'])
@login_required
def recovery_analytics_download():
    filters = request.json
    # TODO: Implement Excel generation logic
    return send_file(
        'path_to_generated_file',
        as_attachment=True,
        download_name='recovery_analytics.xlsx'
    )

@user_bp.route('/api/guarantor-claims/create', methods=['POST'])
@login_required
def create_guarantor_claim():
    try:
        # Get form data
        customer_name = request.form.get('customerName')
        loan_id = request.form.get('loanId')
        guarantor_name = request.form.get('guarantorName')
        claim_amount = request.form.get('claimAmount')
        description = request.form.get('description')
        
        # Handle file uploads
        documents = request.files.getlist('documents')
        
        # TODO: Validate data
        if not all([customer_name, loan_id, guarantor_name, claim_amount, description]):
            return jsonify({'error': 'All fields are required'}), 400
            
        # TODO: Save documents to appropriate storage
        
        # TODO: Create claim in database
        # For now, return success response
        return jsonify({
            'message': 'Claim created successfully',
            'claimId': 'GC' + str(int(time.time()))  # Temporary ID generation
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating guarantor claim: {str(e)}")
        return jsonify({'error': 'Failed to create claim'}), 500

@user_bp.route('/create_demand_letter', methods=['POST'])
@login_required
@csrf.exempt  # Remove this in production and handle CSRF properly
def create_demand_letter():
    """
    Create a new demand letter based on form submission
    """
    try:
        # Create form instance and populate with request data
        form = DemandLetterForm(request.form)
        
        # Import models dynamically
        from models.letter_template import LetterTemplate, LetterType, DemandLetter
        
        # Custom validation for select fields
        errors = {}
        
        # Validate member selection
        if not request.form.get('member_id'):
            errors['member_id'] = ['Please select a member']
        
        # Validate loan selection
        if not request.form.get('loan_id'):
            errors['loan_id'] = ['Please select a loan account']
        
        # Validate letter type selection
        if not request.form.get('letter_type_id'):
            errors['letter_type_id'] = ['Please select a letter type']
        
        # Validate letter template selection
        if not request.form.get('letter_template_id'):
            errors['letter_template_id'] = ['Please select a letter template']
        
        # Validate amount outstanding
        try:
            amount = float(request.form.get('amount_outstanding', 0))
            if amount <= 0:
                errors['amount_outstanding'] = ['Amount must be a positive number']
        except (ValueError, TypeError):
            errors['amount_outstanding'] = ['Invalid amount entered']
        
        # If there are any errors from custom validation
        if errors:
            current_app.logger.error(f"Form validation failed: {errors}")
            return jsonify({
                'status': 'error',
                'message': 'Form validation failed',
                'errors': errors
            }), 400
        
        # Validate form data
        if not form.validate():
            # Return form validation errors
            form_errors = {}
            for field, field_errors in form.errors.items():
                form_errors[field] = field_errors
            
            current_app.logger.error(f"Form validation failed: {form_errors}")
            
            return jsonify({
                'status': 'error',
                'message': 'Form validation failed',
                'errors': form_errors
            }), 400
        
        # Extract member details from form or request
        member_id = str(request.form.get('member_id'))
        member_name = request.form.get('member_name') or ''
        member_number = request.form.get('member_number') or member_name
        
        # Create demand letter
        demand_letter = DemandLetter(
            member_id=member_id,
            member_name=member_name,
            member_number=member_number,
            loan_id=str(request.form.get('loan_id')),
            letter_type_id=form.letter_type_id.data,
            letter_template_id=form.letter_template_id.data,
            amount_outstanding=form.amount_outstanding.data,
            letter_content=form.letter_content.data,
            status='Draft',
            created_by=current_user.id,  # Assuming current_user is the logged-in staff
            sent_at=None  # Not sent yet
        )
        
        # Add and commit to database
        db.session.add(demand_letter)
        db.session.commit()
        
        # Optional: Log the action
        current_app.logger.info(f"Demand Letter created for member {member_name} by {current_user.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'Demand letter created successfully',
            'demand_letter_id': demand_letter.id
        }), 201
    
    except Exception as e:
        # Rollback the session in case of error
        db.session.rollback()
        
        # Log the full error
        current_app.logger.error(f"Error creating demand letter: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred while creating the demand letter',
            'error': str(e)
        }), 500

@user_bp.route('/create_legal_case', methods=['POST'])
@login_required
def create_legal_case():
    """Create a new legal case"""
    try:
        # Get form data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['loan_id', 'case_number', 'court_name', 'case_type', 
                           'filing_date', 'status', 'plaintiff', 'defendant', 
                           'amount_claimed']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Convert dates to datetime objects
        filing_date = datetime.strptime(data['filing_date'], '%Y-%m-%d')
        next_hearing_date = datetime.strptime(data['next_hearing_date'], '%Y-%m-%d') if data.get('next_hearing_date') else None
        
        # Create new legal case
        new_case = LegalCase(
            loan_id=data['loan_id'],
            case_number=data['case_number'],
            court_name=data['court_name'],
            case_type=data['case_type'],
            filing_date=filing_date,
            status=data['status'],
            plaintiff=data['plaintiff'],
            defendant=data['defendant'],
            amount_claimed=float(data['amount_claimed']),
            lawyer_name=data.get('lawyer_name', ''),
            lawyer_contact=data.get('lawyer_contact', ''),
            description=data.get('description', ''),
            next_hearing_date=next_hearing_date
        )
        
        # Add and commit to database
        db.session.add(new_case)
        db.session.commit()
        
        return jsonify({
            'message': 'Legal case created successfully', 
            'case_id': new_case.id
        }), 201
    
    except ValueError as ve:
        current_app.logger.error(f"Value error creating legal case: {str(ve)}")
        return jsonify({'error': 'Invalid date format'}), 400
    
    except Exception as e:
        current_app.logger.error(f"Error creating legal case: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating the legal case'}), 500
@user_bp.route('/legal-cases/<int:case_id>')
@login_required
def get_legal_case(case_id):
    try:
        # Get database configuration - using loan_system database directly
        db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'loan_system'  # Use loan_system database instead of sacco_db
        }

        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get legal case details - use the correct case for table name
        query = """
            SELECT * FROM legal_cases WHERE id = %s
        """
        
        cursor.execute(query, (case_id,))
        case = cursor.fetchone()

        if not case:
            return jsonify({'error': 'Case not found'}), 404

        # Convert decimal to float for JSON serialization
        if case.get('amount_claimed'):
            case['amount_claimed'] = float(case['amount_claimed'])

        # Format dates for JSON
        if case.get('filing_date'):
            case['filing_date'] = case['filing_date'].isoformat()
        if case.get('next_hearing_date'):
            case['next_hearing_date'] = case['next_hearing_date'].isoformat()

        # Add empty history array since we don't have the history table yet
        case['history'] = []

        cursor.close()
        conn.close()

        return jsonify(case)

    except mysql.connector.Error as e:
        current_app.logger.error(f"Database error in get_legal_case: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        current_app.logger.error(f"Error in get_legal_case: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@user_bp.route('/add_case_history', methods=['POST'])
@login_required
def add_case_history():
    try:
        # Validate CSRF token
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token or not csrf.validate_csrf(csrf_token):
            return jsonify({'error': 'Invalid CSRF token'}), 400

        case_id = request.form.get('case_id')
        action = request.form.get('action')
        action_date = request.form.get('action_date')
        notes = request.form.get('notes')
        
        if not all([case_id, action, action_date]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Insert case history
        cursor.execute('''
            INSERT INTO case_history (case_id, action, action_date, notes, created_by)
            VALUES (%s, %s, %s, %s, %s)
        ''', (case_id, action, action_date, notes, current_user.id))
        
        case_history_id = cursor.lastrowid

        # Handle file attachments
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'case_attachments')
            os.makedirs(upload_dir, exist_ok=True)

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_dir, f"{case_history_id}_{filename}")
                    file.save(file_path)
                    
                    # Save file info to database
                    cursor.execute('''
                        INSERT INTO case_attachments 
                        (case_history_id, file_name, file_path, file_type, file_size)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (
                        case_history_id,
                        filename,
                        file_path,
                        file.content_type,
                        os.path.getsize(file_path)
                    ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Case history added successfully'}), 200

    except Exception as e:
        current_app.logger.error(f"Error adding case history: {str(e)}")
        return jsonify({'error': 'Failed to add case history'}), 500

@user_bp.route('/auction/<int:auction_id>')
@login_required
def get_auction_details(auction_id):
    try:
        auction = Auction.query.get_or_404(auction_id)
        
        # Get attachments
        attachments = [{
            'file_name': attachment.file_name,
            'file_path': attachment.file_path
        } for attachment in auction.attachments]
        
        return jsonify({
            'id': auction.id,
            'loan_id': auction.loan_id,
            'client_name': auction.client_name,
            'property_description': auction.property_description,
            'property_type': auction.property_type,
            'valuation_amount': float(auction.valuation_amount),
            'reserve_price': float(auction.reserve_price),
            'auction_date': auction.auction_date.isoformat(),
            'auction_venue': auction.auction_venue,
            'auctioneer_name': auction.auctioneer_name,
            'auctioneer_contact': auction.auctioneer_contact,
            'advertisement_date': auction.advertisement_date.isoformat() if auction.advertisement_date else None,
            'advertisement_medium': auction.advertisement_medium,
            'status': auction.status,
            'notes': auction.notes,
            'attachments': attachments
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/update_auction/<int:auction_id>', methods=['PUT'])
@login_required
def update_auction(auction_id):
    """Update an existing auction"""
    try:
        auction = Auction.query.get_or_404(auction_id)
        data = request.get_json()

        # Validate required fields (same as create)
        required_fields = ['loan_id', 'property_description', 'valuation_amount',
                          'reserve_price', 'auction_date', 'auction_venue']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400

        # Convert dates to datetime objects (same format as create)
        from datetime import datetime
        auction_date = datetime.strptime(data['auction_date'], '%Y-%m-%dT%H:%M')
        advertisement_date = datetime.strptime(data['advertisement_date'], '%Y-%m-%d') if data.get('advertisement_date') else None

        # Update auction fields (mirror create endpoint structure)
        auction.loan_id = data['loan_id']
        auction.client_name = data.get('client_name', auction.client_name)
        auction.property_type = data.get('property_type', auction.property_type)
        auction.property_description = data['property_description']
        auction.valuation_amount = data['valuation_amount']
        auction.reserve_price = data['reserve_price']
        auction.auction_date = auction_date
        auction.auction_venue = data['auction_venue']
        auction.status = data.get('status', auction.status)
        auction.auctioneer_name = data.get('auctioneer_name', auction.auctioneer_name)
        auction.auctioneer_contact = data.get('auctioneer_contact', auction.auctioneer_contact)
        auction.advertisement_date = advertisement_date
        auction.advertisement_medium = data.get('advertisement_medium', auction.advertisement_medium)
        auction.notes = data.get('notes', auction.notes)

        db.session.commit()
        
        return jsonify({'message': 'Auction updated successfully', 'id': auction.id})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating auction: {str(e)}")
        return jsonify({'error': 'An error occurred while updating the auction'}), 500

        from datetime import datetime
from flask import jsonify, request, current_app
from flask_login import login_required

@user_bp.route('/create_loan_reschedule', methods=['POST'])
@login_required
def create_loan_reschedule():
    try:
        # CSRF validation
        if not validate_csrf(request.form.get('csrf_token')):
            return jsonify({'error': 'Invalid CSRF token'}), 403

        # Validate required fields
        required_fields = [
            'member_name',
            'loan_id',
            'original_term',
            'proposed_term',
            'request_date',
            'proposed_start_date'
        ]

        for field in required_fields:
            if not request.form.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400

        # Convert dates
        try:
            request_date = datetime.strptime(request.form['request_date'], '%Y-%m-%d')
            proposed_start_date = datetime.strptime(request.form['proposed_start_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        # Handle file upload
        file_path = None
        if 'supporting_documents' in request.files:
            file = request.files['supporting_documents']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'reschedule_docs',
                    str(current_user.id)
                )
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

        # Create new request
        new_request = LoanReschedule(
            member_name=request.form['member_name'],
            member_id=request.form['member_id'],
            loan_id=request.form['loan_id'],
            original_term=int(request.form['original_term']),
            proposed_term=int(request.form['proposed_term']),
            request_date=request_date,
            proposed_start_date=proposed_start_date,
            reason=request.form.get('reason', ''),
            supporting_documents=file_path,
            status='Pending',
            created_by=current_user.id,
            created_at=datetime.now()
        )

        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            'message': 'Request created successfully',
            'request_id': new_request.id
        }), 201

    except ValueError as ve:
        current_app.logger.error(f"Value error: {str(ve)}")
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Server error processing request'}), 500

def validate_csrf(token):
    """Validate CSRF token using Flask-WTF"""
    try:
        csrf.protect()
        return True
    except ValidationError:
        return False

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/loan-rescheduling/<int:request_id>/edit', methods=['GET'])
@login_required
def edit_loan_reschedule(request_id):
    try:
        request = LoanReschedule.query.get_or_404(request_id)
        return jsonify({
            'id': request.id,
            'member_id': request.member_id,
            'loan_id': request.loan_id,
            'original_term': request.original_term,
            'proposed_term': request.proposed_term,
            'request_date': request.request_date.strftime('%Y-%m-%d'),
            'proposed_start_date': request.proposed_start_date.strftime('%Y-%m-%d'),
            'reason': request.reason
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching loan rescheduling request: {str(e)}")
        return jsonify({'error': 'Error fetching request data'}), 500

@user_bp.route('/edit_loan_reschedule', methods=['POST'])
@login_required
def update_loan_reschedule():
    try:
        # CSRF validation
        if not validate_csrf(request.form.get('csrf_token')):
            return jsonify({'error': 'Invalid CSRF token'}), 403

        # Validate required fields
        required_fields = [
            'request_id',
            'member_id',
            'loan_id',
            'original_term',
            'proposed_term',
            'request_date',
            'proposed_start_date'
        ]
        for field in required_fields:
            if not request.form.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400

        # Convert dates
        try:
            request_date = datetime.strptime(request.form['request_date'], '%Y-%m-%d')
            proposed_start_date = datetime.strptime(request.form['proposed_start_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        # Handle file upload
        file_path = None
        if 'supporting_documents' in request.files:
            file = request.files['supporting_documents']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'reschedule_docs',
                    str(current_user.id)
                )
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

        # Update the request
        request_id = request.form['request_id']
        loan_reschedule_request = LoanReschedule.query.get_or_404(request_id)

        loan_reschedule_request.member_id = request.form['member_id']
        loan_reschedule_request.loan_id = request.form['loan_id']
        loan_reschedule_request.original_term = int(request.form['original_term'])
        loan_reschedule_request.proposed_term = int(request.form['proposed_term'])
        loan_reschedule_request.request_date = request_date
        loan_reschedule_request.proposed_start_date = proposed_start_date
        loan_reschedule_request.reason = request.form.get('reason', '')
        loan_reschedule_request.supporting_documents = file_path
        loan_reschedule_request.status = 'Pending'
        loan_reschedule_request.created_by = current_user.id
        loan_reschedule_request.created_at = datetime.now()

        db.session.commit()

        return jsonify({
            'message': 'Request updated successfully',
            'request_id': loan_reschedule_request.id
        }), 200

    except ValueError as ve:
        current_app.logger.error(f"Value error: {str(ve)}")
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Server error processing request'}), 500

def validate_csrf(token):
    """Validate CSRF token using Flask-WTF"""
    try:
        csrf.protect()
        return True
    except ValidationError:
        return False

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/create_refinance_application', methods=['POST'])
@login_required
def create_refinance_application():
    try:
        # CSRF validation
        if not validate_csrf(request.form.get('csrf_token')):
            return jsonify({'error': 'Invalid CSRF token'}), 403

        # Validate required fields
        required_fields = [
            'member_id',
            'member_name',
            'loan_id',
            'current_balance',
            'requested_amount',
            'new_term',
            'application_date'
        ]
        for field in required_fields:
            if not request.form.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400

        # Convert dates
        try:
            application_date = datetime.strptime(request.form['application_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        # Handle file upload
        file_path = None
        if 'supporting_documents' in request.files:
            file = request.files['supporting_documents']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'refinance_docs',
                    str(current_user.id)
                )
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

        # Create new refinancing application
        new_application = RefinanceApplication(
            member_id=request.form['member_id'],
            member_name=request.form['member_name'],
            loan_id=request.form['loan_id'],
            current_balance=float(request.form['current_balance']),
            requested_amount=float(request.form['requested_amount']),
            new_term=int(request.form['new_term']),
            application_date=application_date,
            application_notes=request.form.get('application_notes', ''),
            supporting_documents=file_path,
            status='Pending',
            created_by=current_user.id,
            created_at=datetime.now()
        )
        db.session.add(new_application)
        db.session.commit()

        return jsonify({
            'message': 'Application created successfully',
            'application_id': new_application.id
        }), 201

    except ValueError as ve:
        current_app.logger.error(f"Value error: {str(ve)}")
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Server error processing request'}), 500



# Define your Mistral API key and endpoint
MISTRAL_API_KEY = 'W2DXJoMj9Sbjj9jFEBFVvr5x6CaMH8sM'
MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions'
MODEL_NAME = 'mistral-small-latest'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sacco_db'
}

def get_table_schema():
    """Fetch column names and data types dynamically from all tables in the database."""
    table_schema = {}

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Fetch all tables in the current database
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s", (db_config['database'],))
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")  # Backticks to handle special characters
            columns = {row[0]: row[1] for row in cursor.fetchall()}
            table_schema[table] = columns

    except Exception as e:
        current_app.logger.error(f"Error fetching table schema: {str(e)}")
        return {}

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    return table_schema

def get_table_relationships():
    """Fetch foreign key relationships from the database."""
    relationships = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
            SELECT 
                TABLE_NAME, 
                COLUMN_NAME, 
                REFERENCED_TABLE_NAME, 
                REFERENCED_COLUMN_NAME 
            FROM 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE 
                TABLE_SCHEMA = %s 
                AND REFERENCED_TABLE_NAME IS NOT NULL;
        """
        cursor.execute(query, (db_config['database'],))
        rows = cursor.fetchall()

        for row in rows:
            relationships.append({
                'source_table': row[0],
                'source_column': row[1],
                'target_table': row[2],
                'target_column': row[3]
            })

    except Exception as e:
        current_app.logger.error(f"Error fetching table relationships: {str(e)}")
        return []

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    return relationships

def generate_system_prompt():
    """Dynamically generate the system prompt with all tables, columns, and relationships."""
    table_schema = get_table_schema()
    relationships = get_table_relationships()
    
    # Format table information with clear column listing
    table_info = []
    for table, columns in table_schema.items():
        col_list = "\n    ".join([f"- {col} ({dtype})" for col, dtype in columns.items()])
        table_info.append(f"Table {table}:\n    {col_list}")
    table_str = "\n\n".join(table_info)
    
    # Format relationships
    relationship_info = []
    for rel in relationships:
        rel_desc = f"- {rel['source_table']}.{rel['source_column']} → {rel['target_table']}.{rel['target_column']}"
        relationship_info.append(rel_desc)
    relationship_str = "\n".join(relationship_info) if relationship_info else "No explicit relationships found."
    
    system_prompt = f"""You are a helpful assistant for a post disbursement management system. Follow these rules:

1. Generate SAFE SQL SELECT queries for database requests.
2. Use ONLY these tables and columns (EXACT names, case-sensitive):
{table_str}

3. Critical Column Rules:
   - Never assume column existence - verify against the tables above
   - Use columns ONLY in their specified tables
   - Date columns: Use 'YYYY-MM-DD' format
   - String values: Enclose in single quotes ('active')
   - Numeric values: No quotes

4. JOIN Instructions:
{relationship_str}
   - Use proper JOIN types based on relationship needs

5. Validation Requirements:
   - Query must start with SELECT
   - Prohibited commands: INSERT, UPDATE, DELETE, DROP, etc.
   - Use COUNT(DISTINCT column) for accurate counts

6. Error Prevention:
   - Double-check column/table names before generating SQL
   - If unsure about a column, don't include it"""
    
    return system_prompt

def call_mistral_api(user_input):
    """Call Mistral API and return a response."""
    headers = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Generate dynamic system prompt with table schema
    SYSTEM_PROMPT = generate_system_prompt()

    data = {
        'model': MODEL_NAME,
        'messages': [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        'max_tokens': 400,  # Increased to accommodate longer queries
        'temperature': 0.3
    }

    response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        api_response = response.json()
        if 'choices' in api_response and api_response['choices']:
            return api_response['choices'][0]['message']['content'].strip()
        else:
            current_app.logger.error("Mistral API returned an empty response")
            return None
    else:
        current_app.logger.error(f"Mistral API error: {response.status_code} - {response.text}")
        return None

def clean_sql_response(response):
    """Remove Markdown code blocks from AI response."""
    return re.sub(r"```sql|```", "", response).strip()

def is_valid_sql(query):
    """Validate SQL query against database schema including column checks."""
    query = query.upper().strip()
    query = query.split(";")[0]  # Remove trailing comments

    # Check for forbidden SQL commands
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "--"]
    if any(keyword in query for keyword in forbidden):
        return False

    # Must start with SELECT
    if not query.startswith("SELECT"):
        return False

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Get all tables in the database
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s", 
                      (db_config['database'],))
        valid_tables = {row[0].upper() for row in cursor.fetchall()}

        # Get column schema
        table_columns = {}
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s
        """, (db_config['database'],))
        for table, column in cursor.fetchall():
            table_upper = table.upper()
            if table_upper not in table_columns:
                table_columns[table_upper] = set()
            table_columns[table_upper].add(column.upper())

        # Parse query for tables and columns
        parsed = sqlparse.parse(query)
        used_tables = set()
        used_columns = set()

        for statement in parsed:
            for token in statement.tokens:
                if isinstance(token, sqlparse.sql.From):
                    for identifier in token.get_identifiers():
                        used_tables.add(identifier.get_real_name().upper())
                if isinstance(token, sqlparse.sql.Identifier):
                    name = token.get_real_name().upper()
                    if '.' in name:
                        table_part, col_part = name.split('.', 1)
                        used_tables.add(table_part)
                        used_columns.add((table_part, col_part))
                    else:
                        used_columns.add((None, name))

        # Validate tables
        for table in used_tables:
            if table not in valid_tables:
                return False

        # Validate columns
        for table_part, col_part in used_columns:
            if table_part:  # Qualified column
                if table_part not in table_columns:
                    return False
                if col_part not in table_columns[table_part]:
                    return False
            else:  # Unqualified column
                found = False
                for table in used_tables:
                    if col_part in table_columns.get(table, set()):
                        found = True
                        break
                if not found:
                    return False

        return True

    except Exception as e:
        current_app.logger.error(f"SQL validation error: {str(e)}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def execute_sql_query(query, params=None):
    """Execute a valid SQL query and return formatted results."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Use parameterized queries for WHERE conditions
        cursor.execute(query, params or ())
        result = cursor.fetchall()

        # Convert Decimal and datetime values
        formatted = [
            {key: (value.isoformat() if isinstance(value, datetime) else float(value) if isinstance(value, Decimal) else value)
             for key, value in row.items()}
            for row in result
        ]

        return formatted

    except Exception as e:
        current_app.logger.error(f"SQL Execution Error: {str(e)}")
        return None

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# ... (previous imports and configuration remain the same)

def generate_natural_response(user_input, query_result):
    """Generate a natural language response from SQL query results using Mistral."""
    headers = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json'
    }

    system_prompt = """You are a helpful assistant that explains database results in natural language. Follow these rules:
1. Always respond in complete, friendly sentences
2. Never mention SQL, column names, or technical details
3. Use numbers directly from the data without formatting
4. For counts, use phrases like "You currently have X..." or "There are X..."
5. For financial amounts, add appropriate currency symbols
6. For dates, use natural formatting (e.g., 'January 5th, 2024')
7. Keep responses concise but informative"""

    user_content = f"""Original question: {user_input}
Database results: {json.dumps(query_result, default=str)}
Please provide a helpful response:"""

    data = {
        'model': MODEL_NAME,
        'messages': [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        'temperature': 0.2,
        'max_tokens': 150
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            api_response = response.json()
            if api_response.get('choices'):
                return api_response['choices'][0]['message']['content'].strip()
        return f"Here's your data: {query_result}"  # Fallback response
    except Exception as e:
        current_app.logger.error(f"Natural response error: {str(e)}")
        return f"Here are your results: {query_result}"

@user_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat request and execute SQL queries if needed."""
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400

    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Get AI-generated SQL response
        raw_response = call_mistral_api(user_input)
        if not raw_response:
            return jsonify({'error': 'Failed to get AI response'}), 500

        cleaned_response = clean_sql_response(raw_response)

        if "SELECT" in cleaned_response.upper() and cleaned_response.upper().startswith("SELECT"):
            if is_valid_sql(cleaned_response):
                params = []
                db_response = execute_sql_query(cleaned_response, params)
                if db_response is not None:
                    # Generate natural language response
                    natural_response = generate_natural_response(user_input, db_response)
                    return jsonify({'type': 'message', 'content': natural_response})
                else:
                    return jsonify({'error': 'SQL query execution failed'}), 500
            else:
                return jsonify({'error': 'Invalid SQL query generated'}), 400

        # Return original AI response if not SQL
        return jsonify({'type': 'message', 'content': raw_response})

    except Exception as e:
        current_app.logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500