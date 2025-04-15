import requests
import re
import sqlparse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import mysql.connector
from datetime import datetime, timedelta
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
from models.post_disbursement_modules import ExpectedStructure, ActualStructure, PostDisbursementModule
from functools import lru_cache

# Global helper function to add visible_modules to template parameters
def render_with_modules(template, **kwargs):
    visible_modules = PostDisbursementModule.query.filter_by(hidden=False).order_by(PostDisbursementModule.order).all()
    kwargs['visible_modules'] = visible_modules
    return render_template(template, **kwargs)

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
    
    return render_with_modules('user/dashboard.html',
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
        return render_with_modules('user/dynamic_form.html',
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
        
        return render_with_modules('user/manage_module.html',
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
        
        return render_with_modules('user/view_prospect.html',
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
            
        return render_with_modules('user/edit_prospect.html', 
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
            return render_with_modules('user/convert_form.html',
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
            return render_with_modules('user/register_form.html',
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
    return render_with_modules('user/correspondence.html')

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
    return render_with_modules('user/manage_calendar.html')

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
    return render_with_modules('user/reports.html')



@user_bp.route('/post-disbursement')
@login_required
def post_disbursement():
    current_app.logger.info("Starting post_disbursement route")

    # Use the global render_with_modules function
    
    # Statically define the module ID
    module_id = 1  # Replace with the desired module ID

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
        if not core_system:
            flash('No active core banking system configured', 'error')
            return render_with_modules('user/post_disbursement.html',
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

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
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

        try:
            conn = mysql.connector.connect(**core_banking_config)
            cursor = conn.cursor(dictionary=True)
        except mysql.connector.Error as e:
            current_app.logger.error(f"Error connecting to database: {str(e)}")
            flash(f'Error connecting to database: {str(e)}', 'error')
            return render_with_modules('user/post_disbursement.html',
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
                                   error=f'Error connecting to database: {str(e)}')

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    # Retrieve expected and actual columns as lists
                    expected_columns = expected.columns  # e.g., ['LoanID', 'LedgerID', ...]
                    actual_columns = actual.columns       # e.g., ['loan_id', 'ledger_id', ...]
                    
                    # Create a dictionary mapping expected to actual columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict  # Now a dictionary
                    }
                    current_app.logger.info(f"Retrieved mapping: {mapping}")
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Mapping Data: {mapping}")
        except Exception as e:
            flash(f'Error retrieving mapping data: {str(e)}', 'error')
            return render_with_modules('user/post_disbursement.html',
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
                                   error=f'Error retrieving mapping data: {str(e)}')

        def build_dynamic_query(mapping):
            try:
                # Access the mapping correctly using string keys
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})

                # Ensure that the necessary columns are present in the mapping
                if not all(key in ll["columns"] for key in ["LoanID", "LedgerID", "OutstandingBalance", "ArrearsAmount", "ArrearsDays"]):
                    raise KeyError("Missing columns in LoanLedgerEntries mapping")

                if not all(key in ld["columns"] for key in ["LoanAppID", "LoanStatus"]):
                    raise KeyError("Missing columns in LoanDisbursements mapping")

                if not all(key in la["columns"] for key in ["LoanAppID", "LoanNo", "LoanAmount"]):
                    raise KeyError("Missing columns in LoanApplications mapping")

                query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    l.{ll["columns"]["ArrearsAmount"]} AS ArrearsAmount,
                    l.{ll["columns"]["ArrearsDays"]} AS ArrearsDays,
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus
                FROM {ll["actual_table_name"]} l
                JOIN (
                    SELECT {ll["columns"]["LoanID"]} AS LoanID,
                        MAX({ll["columns"]["LedgerID"]}) AS latest_id
                    FROM {ll["actual_table_name"]}
                    GROUP BY {ll["columns"]["LoanID"]}
                ) latest
                    ON l.{ll["columns"]["LoanID"]} = latest.LoanID
                    AND l.{ll["columns"]["LedgerID"]} = latest.latest_id
                JOIN {ld["actual_table_name"]} ld
                    ON l.{ll["columns"]["LoanID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {la["actual_table_name"]} la
                    ON ld.{ld["columns"]["LoanAppID"]} = la.{la["columns"]["LoanAppID"]}
                WHERE ld.{ld["columns"]["LoanStatus"]} = 'Active'
                ORDER BY l.{ll["columns"]["LoanID"]}
                """
                current_app.logger.info(f"Built query: {query}")
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise
        def build_dynamic_query(mapping):
            try:
                # Ensure mapping is a dictionary
                if not isinstance(mapping, dict):
                    raise ValueError("Mapping should be a dictionary")

                # Access the mapping correctly using string keys
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})

                # Ensure that the necessary columns are present in the mapping
                required_ll_columns = ["LoanID", "LedgerID", "OutstandingBalance", "ArrearsAmount", "ArrearsDays"]
                required_ld_columns = ["LoanAppID", "LoanStatus"]
                required_la_columns = ["LoanAppID", "LoanNo", "LoanAmount"]

                if not all(column in ll.get("columns", []) for column in required_ll_columns):
                    raise KeyError(f"Missing columns in LoanLedgerEntries mapping: {required_ll_columns}")

                if not all(column in ld.get("columns", []) for column in required_ld_columns):
                    raise KeyError(f"Missing columns in LoanDisbursements mapping: {required_ld_columns}")

                if not all(column in la.get("columns", []) for column in required_la_columns):
                    raise KeyError(f"Missing columns in LoanApplications mapping: {required_la_columns}")

                query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    l.{ll["columns"]["ArrearsAmount"]} AS ArrearsAmount,
                    l.{ll["columns"]["ArrearsDays"]} AS ArrearsDays,
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus
                FROM {ll["actual_table_name"]} l
                JOIN (
                    SELECT {ll["columns"]["LoanID"]} AS LoanID,
                        MAX({ll["columns"]["LedgerID"]}) AS latest_id
                    FROM {ll["actual_table_name"]}
                    GROUP BY {ll["columns"]["LoanID"]}
                ) latest
                    ON l.{ll["columns"]["LoanID"]} = latest.LoanID
                    AND l.{ll["columns"]["LedgerID"]} = latest.latest_id
                JOIN {ld["actual_table_name"]} ld
                    ON l.{ll["columns"]["LoanID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {la["actual_table_name"]} la
                    ON ld.{ld["columns"]["LoanAppID"]} = la.{la["columns"]["LoanAppID"]}
                WHERE ld.{ld["columns"]["LoanStatus"]} = 'Active'
                ORDER BY l.{ll["columns"]["LoanID"]}
                """
                current_app.logger.info(f"Built query: {query}")
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise



        try:
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            loan_data = cursor.fetchall()
            current_app.logger.info(f"Fetched Loan Data: {loan_data}")
        except Exception as e:
            flash(f'Error executing query: {str(e)}', 'error')
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
                                   error=f'Error executing query: {str(e)}')

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

        for loan in loan_data:
            try:
                loan_id = loan.get('LoanID', 'Unknown')
                loan_no = loan.get('LoanNo', 'Unknown')
                outstanding_balance = float(loan.get('OutstandingBalance', 0))
                arrears_amount = float(loan.get('ArrearsAmount', 0))
                arrears_days = int(loan.get('ArrearsDays', 0))

                current_app.logger.info(f"Processing Loan {loan_id} (No: {loan_no}): Balance={outstanding_balance}, Arrears={arrears_amount}, Days={arrears_days}")

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

                overdue_loans[category]['count'] += 1
                overdue_loans[category]['amount'] += outstanding_balance

                current_app.logger.info(f"Classified loan {loan_id} as {category}")
            except Exception as e:
                current_app.logger.error(f"Error processing loan {loan.get('LoanID', 'Unknown')}: {str(e)}")
                continue

        current_app.logger.info(f"Overdue Loans Data: {overdue_loans}")

        total_amount = sum(cat['amount'] for cat in overdue_loans.values())
        if total_amount > 0:
            for category in overdue_loans:
                overdue_loans[category]['percentage'] = (overdue_loans[category]['amount'] / total_amount * 100)
        else:
            for category in overdue_loans:
                overdue_loans[category]['percentage'] = float(0)

        recovery_rate = ((total_outstanding - total_in_arrears) / total_outstanding * 100) if total_outstanding > 0 else float(0)
        npl_amount = float(overdue_loans['SUBSTANDARD']['amount'] + overdue_loans['DOUBTFUL']['amount'] + overdue_loans['LOSS']['amount'])
        npl_ratio = (npl_amount / total_outstanding * 100) if total_outstanding > 0 else float(0)

        provision_rates = {
            'NORMAL': 0.01,
            'WATCH': 0.05,
            'SUBSTANDARD': 0.25,
            'DOUBTFUL': 0.50,
            'LOSS': 1.00
        }

        total_provisions = float(sum(overdue_loans[category]['amount'] * rate for category, rate in provision_rates.items()))
        npl_coverage_ratio = (total_provisions / npl_amount * 100) if npl_amount > 0 else float(0)
        cost_of_risk = (total_provisions / total_outstanding * 100) if total_outstanding > 0 else float(0)

        par30_amount = float(sum(overdue_loans[grade]['amount'] for grade in ['WATCH', 'SUBSTANDARD', 'DOUBTFUL', 'LOSS']))
        par30_ratio = (par30_amount / total_outstanding * 100) if total_outstanding > 0 else float(0)

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

        current_app.logger.info(f"Classification Data: {classification_data}")

        cursor.close()
        conn.close()

        return render_with_modules(
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

        return render_with_modules('user/post_disbursement.html', **default_values)
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
    
    return render_with_modules('user/analytics.html',
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
    return render_with_modules('user/collection_schedule.html')

@user_bp.route('/guarantors')
@login_required
def guarantors():
    """Display guarantors list page"""
    return render_with_modules('user/guarantors_list.html')

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
    return render_with_modules('user/create_notification.html')

@user_bp.route('/api/metrics')
@login_required
def get_metrics():
    """Get updated metrics for the dashboard."""
    try:
        # Statically define the module ID
        module_id = 1  # Replace with the desired module ID

        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 400

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    # Retrieve expected and actual columns as lists
                    expected_columns = expected.columns  # e.g., ['LoanID', 'LedgerID', ...]
                    actual_columns = actual.columns       # e.g., ['loan_id', 'ledger_id', ...]
                    
                    # Create a dictionary mapping expected to actual columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict  # Now a dictionary
                    }
                    current_app.logger.info(f"Retrieved mapping: {mapping}")
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Mapping Data: {mapping}")
        except Exception as e:
            return jsonify({'error': f'Error retrieving mapping data: {str(e)}'}), 500

        # Build dynamic query
        def build_dynamic_query(mapping):
            try:
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})

                # Ensure that the necessary columns are present in the mapping
                required_ll_columns = ["LoanID", "LedgerID", "OutstandingBalance", "ArrearsAmount", "ArrearsDays"]
                required_ld_columns = ["LoanAppID", "LoanStatus"]
                required_la_columns = ["LoanAppID", "LoanNo", "LoanAmount"]

                if not all(column in ll.get("columns", []) for column in required_ll_columns):
                    raise KeyError(f"Missing columns in LoanLedgerEntries mapping: {required_ll_columns}")

                if not all(column in ld.get("columns", []) for column in required_ld_columns):
                    raise KeyError(f"Missing columns in LoanDisbursements mapping: {required_ld_columns}")

                if not all(column in la.get("columns", []) for column in required_la_columns):
                    raise KeyError(f"Missing columns in LoanApplications mapping: {required_la_columns}")

                query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    l.{ll["columns"]["ArrearsAmount"]} AS ArrearsAmount,
                    l.{ll["columns"]["ArrearsDays"]} AS ArrearsDays,
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus
                FROM {ll["actual_table_name"]} l
                JOIN (
                    SELECT {ll["columns"]["LoanID"]} AS LoanID,
                        MAX({ll["columns"]["LedgerID"]}) AS latest_id
                    FROM {ll["actual_table_name"]}
                    GROUP BY {ll["columns"]["LoanID"]}
                ) latest
                    ON l.{ll["columns"]["LoanID"]} = latest.LoanID
                    AND l.{ll["columns"]["LedgerID"]} = latest.latest_id
                JOIN {ld["actual_table_name"]} ld
                    ON l.{ll["columns"]["LoanID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {la["actual_table_name"]} la
                    ON ld.{ld["columns"]["LoanAppID"]} = la.{la["columns"]["LoanAppID"]}
                WHERE ld.{ld["columns"]["LoanStatus"]} = 'Active'
                ORDER BY l.{ll["columns"]["LoanID"]}
                """
                current_app.logger.info(f"Built query: {query}")
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        try:
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            loan_data = cursor.fetchall()
            current_app.logger.info(f"Fetched Loan Data: {loan_data}")
        except Exception as e:
            return jsonify({'error': f'Error executing query: {str(e)}'}), 500

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
                loan_id = loan.get('LoanID', 'Unknown')
                loan_no = loan.get('LoanNo', 'Unknown')
                outstanding_balance = float(loan.get('OutstandingBalance', 0))
                arrears_amount = float(loan.get('ArrearsAmount', 0))
                arrears_days = int(loan.get('ArrearsDays', 0))

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
        # Statically define the module ID
        module_id = 1  # Replace with the desired module ID

        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 400

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    # Retrieve expected and actual columns as lists
                    expected_columns = expected.columns  # e.g., ['LoanID', 'LedgerID', ...]
                    actual_columns = actual.columns       # e.g., ['loan_id', 'ledger_id', ...]
                    
                    # Create a dictionary mapping expected to actual columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict  # Now a dictionary
                    }
                    current_app.logger.info(f"Retrieved mapping: {mapping}")
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Mapping Data: {mapping}")
        except Exception as e:
            return jsonify({'error': f'Error retrieving mapping data: {str(e)}'}), 500

        # Build dynamic query
        def build_dynamic_query(mapping):
            try:
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})
                m = mapping.get("Members", {}) 
        
                # Ensure that the necessary columns are present in the mapping
                required_ll_columns = ["LoanID", "LedgerID", "OutstandingBalance", "ArrearsAmount", "ArrearsDays"]
                required_ld_columns = ["LoanAppID", "LoanStatus"]
                required_la_columns = ["LoanAppID", "LoanNo", "LoanAmount", "MemberID"]  # Added MemberID
                required_m_columns = ["MemberID", "FirstName", "LastName"]
        
                if not all(column in ll.get("columns", []) for column in required_ll_columns):
                    raise KeyError(f"Missing columns in LoanLedgerEntries mapping: {required_ll_columns}")
        
                if not all(column in ld.get("columns", []) for column in required_ld_columns):
                    raise KeyError(f"Missing columns in LoanDisbursements mapping: {required_ld_columns}")
        
                if not all(column in la.get("columns", []) for column in required_la_columns):
                    raise KeyError(f"Missing columns in LoanApplications mapping: {required_la_columns}")
        
                if not all(column in m.get("columns", []) for column in required_m_columns):
                    raise KeyError(f"Missing columns in Members mapping: {required_m_columns}")
        
                query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    l.{ll["columns"]["ArrearsAmount"]} AS ArrearsAmount,
                    l.{ll["columns"]["ArrearsDays"]} AS ArrearsDays,
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus,
                    CONCAT(m.{m["columns"]["FirstName"]}, ' ', m.{m["columns"]["LastName"]}) AS CustomerName
                FROM {ll["actual_table_name"]} l
                JOIN (
                    SELECT {ll["columns"]["LoanID"]} AS LoanID,
                        MAX({ll["columns"]["LedgerID"]}) AS latest_id
                    FROM {ll["actual_table_name"]}
                    GROUP BY {ll["columns"]["LoanID"]}
                ) latest ON l.{ll["columns"]["LoanID"]} = latest.LoanID AND l.{ll["columns"]["LedgerID"]} = latest.latest_id
                JOIN {la["actual_table_name"]} la ON l.{ll["columns"]["LoanID"]} = la.{la["columns"]["LoanAppID"]}
                JOIN {ld["actual_table_name"]} ld ON la.{la["columns"]["LoanAppID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {m["actual_table_name"]} m ON la.{la["columns"]["MemberID"]} = m.{m["columns"]["MemberID"]}
                WHERE ld.{ld["columns"]["LoanStatus"]} = 'Active'
                ORDER BY l.{ll["columns"]["LoanID"]}
                """
                current_app.logger.info(f"Built query: {query}")
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        try:
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            loan_data = cursor.fetchall()
            current_app.logger.info(f"Fetched Loan Data: {loan_data}")
        except Exception as e:
            return jsonify({'error': f'Error executing query: {str(e)}'}), 500

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


@user_bp.route('/reminders/loans', methods=['GET'])
@login_required
def get_reminder_loans():
    conn = None
    cursor = None
    
    try:
        current_app.logger.info("Starting get_reminder_loans function")
        
        # Use module ID 8 as specified
        module_id = 8
        current_app.logger.info(f"Using module_id: {module_id}")

        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            current_app.logger.error("No active core banking system found")
            return jsonify({'error': 'No active core banking system configured'}), 400
        
        current_app.logger.info(f"Found active core banking system: {core_system.name if hasattr(core_system, 'name') else 'Unknown'}")

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
            current_app.logger.info("Successfully decoded auth credentials")
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}
            current_app.logger.info("Using default auth credentials")

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }
        
        current_app.logger.info(f"Database connection config: host={core_banking_config['host']}, port={core_banking_config['port']}, user={core_banking_config['user']}, database={core_banking_config['database']}")

        try:
            conn = mysql.connector.connect(**core_banking_config)
            cursor = conn.cursor(dictionary=True)
            current_app.logger.info(f"Successfully connected to database: {core_banking_config['database']}")
            
            # Test basic connectivity
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            current_app.logger.info(f"Basic connectivity test: {result}")
        except Exception as e:
            current_app.logger.error(f"Database connection failed: {str(e)}")
            return jsonify({'error': f'Failed to connect to database: {str(e)}'}), 500

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    # Retrieve expected and actual columns as lists
                    expected_columns = expected.columns  # e.g., ['LoanID', 'LedgerID', ...]
                    actual_columns = actual.columns       # e.g., ['loan_id', 'ledger_id', ...]
                    
                    # Create a dictionary mapping expected to actual columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict  # Now a dictionary
                    }
                    current_app.logger.info(f"Retrieved mapping: {mapping}")
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        # Get mapping data for module 8
        try:
            current_app.logger.info(f"Retrieving mapping for module_id: {module_id}")
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Retrieved mapping data: {mapping}")
            
            # Validate mapping structure
            if not mapping:
                current_app.logger.error("Mapping data is empty")
                return jsonify({'error': 'No mapping data found for the specified module'}), 500
                
            required_tables = ["LoanLedgerEntries", "LoanDisbursements", "LoanApplications", "Members"]
            missing_tables = [table for table in required_tables if table not in mapping]
            if missing_tables:
                current_app.logger.error(f"Missing required tables in mapping: {missing_tables}")
                return jsonify({'error': f'Missing required tables in mapping: {missing_tables}'}), 500
                
        except Exception as e:
            current_app.logger.error(f"Error retrieving mapping: {str(e)}")
            return jsonify({'error': f'Error retrieving database mappings: {str(e)}'}), 500

        # Build dynamic query
        def build_dynamic_query(mapping):
            try:
                current_app.logger.info("Starting to build dynamic query")
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})
                mb = mapping.get("Members", {})
                
                # Log table names for debugging
                current_app.logger.info(f"Actual table names: LoanLedgerEntries={ll.get('actual_table_name', 'N/A')}, "
                                       f"LoanDisbursements={ld.get('actual_table_name', 'N/A')}, "
                                       f"LoanApplications={la.get('actual_table_name', 'N/A')}, "
                                       f"Members={mb.get('actual_table_name', 'N/A')}")
                
                # Update required columns based on actual structure
                required_ll_columns = ["LedgerID", "LoanID", "MemberID", "OutstandingBalance", "RepaymentDueDate", 
                                      "ArrearsAmount", "ArrearsDays", "PenaltyAmount"]
                required_ld_columns = ["LoanAppID", "LoanStatus"]
                required_la_columns = ["LoanAppID", "MemberID", "LoanNo", "LoanAmount"]
                required_mb_columns = ["MemberID", "FirstName", "LastName", "Email", "PhoneNumber"]
                
                # Validate columns exist in mappings
                if not all(column in ll.get("columns", {}) for column in required_ll_columns):
                    missing = [col for col in required_ll_columns if col not in ll.get("columns", {})]
                    current_app.logger.error(f"Missing columns in LoanLedgerEntries mapping: {missing}")
                    raise KeyError(f"Missing columns in LoanLedgerEntries mapping: {missing}")
                
                if not all(column in ld.get("columns", {}) for column in required_ld_columns):
                    missing = [col for col in required_ld_columns if col not in ld.get("columns", {})]
                    current_app.logger.error(f"Missing columns in LoanDisbursements mapping: {missing}")
                    raise KeyError(f"Missing columns in LoanDisbursements mapping: {missing}")
                
                if not all(column in la.get("columns", {}) for column in required_la_columns):
                    missing = [col for col in required_la_columns if col not in la.get("columns", {})]
                    current_app.logger.error(f"Missing columns in LoanApplications mapping: {missing}")
                    raise KeyError(f"Missing columns in LoanApplications mapping: {missing}")
                    
                if not all(column in mb.get("columns", {}) for column in required_mb_columns):
                    missing = [col for col in required_mb_columns if col not in mb.get("columns", {})]
                    current_app.logger.error(f"Missing columns in Members mapping: {missing}")
                    raise KeyError(f"Missing columns in Members mapping: {missing}")
                
                current_app.logger.info("All required columns validated successfully")
                
                # Updated query with the new structure
                query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["MemberID"]} AS ClientID,  
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    l.{ll["columns"]["ArrearsAmount"]} AS ArrearsAmount,
                    l.{ll["columns"]["ArrearsDays"]} AS ArrearsDays,
                    l.{ll["columns"]["OutstandingBalance"]} AS InstallmentAmount,  -- Using OutstandingBalance as InstallmentAmount
                    l.{ll["columns"]["RepaymentDueDate"]} AS NextInstallmentDate,  -- Using RepaymentDueDate as NextInstallmentDate
                    m.{mb["columns"]["FirstName"]} AS FirstName,
                    m.{mb["columns"]["LastName"]} AS LastName,
                    m.{mb["columns"]["Email"]} AS Email,
                    m.{mb["columns"]["PhoneNumber"]} AS Phone,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus
                FROM {ll["actual_table_name"]} l
                JOIN (
                    SELECT {ll["columns"]["LoanID"]} AS LoanID,
                        MAX({ll["columns"]["LedgerID"]}) AS latest_id
                    FROM {ll["actual_table_name"]}
                    GROUP BY {ll["columns"]["LoanID"]}
                ) latest
                    ON l.{ll["columns"]["LoanID"]} = latest.LoanID
                    AND l.{ll["columns"]["LedgerID"]} = latest.latest_id
                JOIN {ld["actual_table_name"]} ld
                    ON l.{ll["columns"]["LoanID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {la["actual_table_name"]} la
                    ON ld.{ld["columns"]["LoanAppID"]} = la.{la["columns"]["LoanAppID"]}
                JOIN {mb["actual_table_name"]} m
                    ON l.{ll["columns"]["MemberID"]} = m.{mb["columns"]["MemberID"]}
                WHERE ld.{ld["columns"]["LoanStatus"]} = 'Active'
                ORDER BY l.{ll["columns"]["LoanID"]}
                """
                current_app.logger.info(f"Built query: {query}")
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        # Execute query and get data
        try:
            current_app.logger.info("About to build and execute query")
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            loan_data = cursor.fetchall()
            current_app.logger.info(f"Fetched {len(loan_data)} loan records")
            
            # Log a sample of the data
            if loan_data:
                sample = loan_data[0]
                current_app.logger.info(f"Sample loan data: {sample}")
                current_app.logger.info(f"Sample keys: {list(sample.keys())}")
            else:
                current_app.logger.warning("No loan data returned from query")
        except Exception as e:
            current_app.logger.error(f"Error executing query: {str(e)}")
            return jsonify({'error': f'Error executing database query: {str(e)}'}), 500

        # Helper function for safe date parsing
        def parse_date(date_str):
            """Safe date parser with error handling"""
            try:
                if isinstance(date_str, datetime):
                    return date_str.date()
                elif isinstance(date_str, str) and date_str:
                    return parse(date_str).date()
                return None
            except Exception as e:
                current_app.logger.warning(f"Date parsing error for '{date_str}': {str(e)}")
                return None

        # Format dates for JSON serialization
        try:
            current_app.logger.info("Formatting dates for JSON serialization")
            for loan in loan_data:
                # Convert date objects to strings
                if 'NextInstallmentDate' in loan and loan['NextInstallmentDate']:
                    if not isinstance(loan['NextInstallmentDate'], str):
                        loan['NextInstallmentDate'] = loan['NextInstallmentDate'].strftime('%Y-%m-%d')
                    # Add DueDate field for display in UI
                    loan['DueDate'] = loan['NextInstallmentDate']
            current_app.logger.info("Date formatting completed")
        except Exception as e:
            current_app.logger.error(f"Error formatting dates: {str(e)}")
            return jsonify({'error': f'Error formatting dates: {str(e)}'}), 500

        # Categorize loans with improved logic
        try:
            current_app.logger.info("Starting loan categorization with improved logic")
            upcoming_installments = []
            overdue_loans = []
            delinquent_accounts = []
            high_risk_loans = []

            today = datetime.now().date()
            current_app.logger.info(f"Today's date for comparison: {today}")

            # Log the total number of loans before categorization
            current_app.logger.info(f"Total loans before categorization: {len(loan_data)}")
            
            # Create a detailed breakdown of arrears days for analysis
            arrears_breakdown = {
                '>=60': 0,
                '30-59': 0,
                '1-29': 0,
                '<=0': 0,
                'invalid': 0
            }
            
            for loan in loan_data:
                try:
                    loan_id = loan.get('LoanID', 'Unknown')
                    # Safely get ArrearsDays with proper validation
                    arrears_days_raw = loan.get('ArrearsDays')
                    outstanding_balance = loan.get('OutstandingBalance', 0)
                    
                    # Log raw values for debugging
                    current_app.logger.info(f"Processing loan {loan_id}: Raw ArrearsDays={arrears_days_raw}, Type={type(arrears_days_raw)}, OutstandingBalance={outstanding_balance}")
                    
                    # Skip loans without ArrearsDays data
                    if arrears_days_raw is None:
                        current_app.logger.warning(f"Loan {loan_id} missing ArrearsDays, skipping")
                        arrears_breakdown['invalid'] += 1
                        continue
                        
                    # Convert to integer safely
                    try:
                        # Ensure we handle string values properly
                        arrears_days = int(float(str(arrears_days_raw).strip() or '0'))
                        current_app.logger.info(f"Loan {loan_id} has ArrearsDays: {arrears_days}")
                    except (ValueError, TypeError) as e:
                        current_app.logger.warning(f"Invalid ArrearsDays value for loan {loan_id}: {arrears_days_raw}, Error: {str(e)}")
                        arrears_breakdown['invalid'] += 1
                        continue
                    
                    # Update arrears breakdown
                    if arrears_days >= 60:
                        arrears_breakdown['>=60'] += 1
                    elif arrears_days >= 30:
                        arrears_breakdown['30-59'] += 1
                    elif arrears_days > 0:
                        arrears_breakdown['1-29'] += 1
                    else:
                        arrears_breakdown['<=0'] += 1
                    
                    # Categorize based on arrears days with fixed boundary conditions
                    if arrears_days >= 60:  # Changed from > to >=
                        # High risk: 60+ days late
                        high_risk_loans.append(loan)
                        current_app.logger.info(f"Loan {loan_id} categorized as high risk with {arrears_days} days")
                    elif arrears_days >= 30:  # Changed from > to >=
                        # Delinquent: 30-59 days late
                        delinquent_accounts.append(loan)
                        current_app.logger.info(f"Loan {loan_id} categorized as delinquent with {arrears_days} days")
                    elif arrears_days > 0:
                        # Overdue: 1-29 days late
                        overdue_loans.append(loan)
                        current_app.logger.info(f"Loan {loan_id} categorized as overdue with {arrears_days} days")
                    else:
                        # Not late, check if it's upcoming (due within 7 days)
                        if 'NextInstallmentDate' in loan and loan['NextInstallmentDate']:
                            try:
                                # Parse the next installment date
                                next_date = parse_date(loan['NextInstallmentDate'])
                                if next_date:
                                    # Calculate days until next installment
                                    days_until = (next_date - today).days
                                    current_app.logger.info(f"Loan {loan_id} has {days_until} days until next installment")
                                    
                                    # Add to upcoming if due within a week and in the future
                                    if 0 <= days_until <= 7:
                                        upcoming_installments.append(loan)
                                        current_app.logger.info(f"Loan {loan_id} categorized as upcoming")
                            except Exception as e:
                                current_app.logger.warning(f"Invalid NextInstallmentDate for loan {loan_id}: {loan.get('NextInstallmentDate')}. Error: {str(e)}")
                                continue
                except Exception as e:
                    current_app.logger.error(f"Error categorizing loan {loan.get('LoanID', 'Unknown')}: {str(e)}")
                    continue
                    
            # Log the arrears breakdown
            current_app.logger.info(f"Arrears days breakdown: {arrears_breakdown}")
            current_app.logger.info(f"Categorization results: {len(high_risk_loans)} high risk, {len(delinquent_accounts)} delinquent, {len(overdue_loans)} overdue, {len(upcoming_installments)} upcoming")
            
            # Calculate financial exposures
            def sum_balance(loans):
                try:
                    return round(sum(float(loan.get('OutstandingBalance', 0)) for loan in loans), 2)
                except Exception as e:
                    current_app.logger.error(f"Error calculating balance sum: {str(e)}")
                    return 0
                    
            high_risk_exposure = sum_balance(high_risk_loans)
            delinquent_exposure = sum_balance(delinquent_accounts)
            overdue_exposure = sum_balance(overdue_loans)
            upcoming_exposure = sum_balance(upcoming_installments)
            
            current_app.logger.info(f"Categorization complete: {len(upcoming_installments)} upcoming, {len(overdue_loans)} overdue, {len(delinquent_accounts)} delinquent, {len(high_risk_loans)} high risk")
            current_app.logger.info(f"Financial exposure: high_risk=${high_risk_exposure}, delinquent=${delinquent_exposure}, overdue=${overdue_exposure}, upcoming=${upcoming_exposure}")
        except Exception as e:
            current_app.logger.error(f"Error in loan categorization: {str(e)}")
            return jsonify({'error': f'Error categorizing loans: {str(e)}'}), 500
        
        # Return categorized data with exposure amounts and raw data for debugging
        try:
            current_app.logger.info("Preparing JSON response with exposure data and raw data for debugging")
            
            # Log raw data for debugging
            current_app.logger.info(f"Raw loan data (first 5 entries):")
            for i, loan in enumerate(loan_data[:5]):
                current_app.logger.info(f"Raw loan #{i+1}: ID={loan.get('LoanID')}, ArrearsDays={loan.get('ArrearsDays')}, OutstandingBalance={loan.get('OutstandingBalance')}")
            
            # Check for duplicate loan IDs
            loan_ids = {}
            for loan in loan_data:
                loan_id = loan.get('LoanID')
                if loan_id in loan_ids:
                    loan_ids[loan_id] += 1
                else:
                    loan_ids[loan_id] = 1
            
            duplicate_loans = {loan_id: count for loan_id, count in loan_ids.items() if count > 1}
            current_app.logger.info(f"Found {len(duplicate_loans)} loan IDs with multiple entries: {duplicate_loans}")
            
            response_data = {
                'upcoming_installments': upcoming_installments,
                'overdue_loans': overdue_loans,
                'delinquent_accounts': delinquent_accounts,
                'high_risk_loans': high_risk_loans,
                'exposure': {
                    'high_risk': high_risk_exposure,
                    'delinquent': delinquent_exposure,
                    'overdue': overdue_exposure,
                    'upcoming': upcoming_exposure
                },
                'counts': {
                    'upcoming_installments': len(upcoming_installments),
                    'overdue_loans': len(overdue_loans),
                    'delinquent_accounts': len(delinquent_accounts),
                    'high_risk_loans': len(high_risk_loans)
                },
                'raw_data': loan_data  # Include raw data for debugging
            }
            current_app.logger.info("JSON response prepared successfully")
            return jsonify(response_data)
        except Exception as e:
            current_app.logger.error(f"Error preparing JSON response: {str(e)}")
            return jsonify({'error': f'Error preparing response: {str(e)}'}), 500
    
    except Exception as e:
        current_app.logger.error(f"Error processing reminder loans: {str(e)}")
        return jsonify({'error': f'Error processing loan reminders: {str(e)}'}), 500
    
    finally:
        # Clean up database resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        current_app.logger.info("Database resources cleaned up")

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
        return render_with_modules('user/loan_rescheduling.html', loan_reschedules=loan_reschedules)
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
        return render_with_modules('user/refinancing.html', refinancing_applications=refinancing_applications)
    except Exception as e:
        current_app.logger.error(f"Error rendering refinancing page: {str(e)}")
        flash('An error occurred while loading the refinancing page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/settlement-plans')
@login_required
def settlement_plans():
    """Render the settlement plans page"""
    try:
        return render_with_modules('user/settlement_plans.html')
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
    
    return render_with_modules('user/demand_letters.html', 
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
        return render_with_modules('user/crb_reports.html')
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

        return render_with_modules('user/legal_cases.html',
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
        
        return render_with_modules('user/auction_process.html',
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
        return render_with_modules('user/field_visits.html')
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
    return render_with_modules('user/reports/guarantor_claims.html')

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
    return render_with_modules('user/reports/collection_report.html')

@user_bp.route('/reports/communication-logs')
@login_required
def communication_logs():
    return render_with_modules('user/reports/communication_logs.html')

@user_bp.route('/reports/legal-status')
@login_required
def legal_status():
    return render_with_modules('user/reports/legal_status.html')

@user_bp.route('/reports/recovery-analytics')
@login_required
def recovery_analytics():
    return render_with_modules('user/reports/recovery_analytics.html')

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





# Mistral API configuration
MISTRAL_API_KEY = 'W2DXJoMj9Sbjj9jFEBFVvr5x6CaMH8sM'
MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions'
MODEL_NAME = 'mistral-small-latest'

# Database configuration
databases = {
    'primary': {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'sacco_db',
    },
    'secondary': {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'loan_system',
    }
}

# Schema cache with expiration (4 hours)
SCHEMA_CACHE_TTL = 14400  # seconds
_schema_cache = {
    'table_schema': None,
    'relationships': None,
    'last_updated': 0
}

def extract_database_preference(user_input):
    """Extract database preference from user input."""
    user_input_lower = user_input.lower()
    
    # Check for explicit database mentions
    if "sacco_db" in user_input_lower or "sacco database" in user_input_lower:
        return "primary"
    elif "loan_system" in user_input_lower or "loan database" in user_input_lower:
        return "secondary"
    
    # More generalized pattern matching
    db_patterns = {
        'primary': ['sacco', 'member', 'members'],
        'secondary': ['loan', 'loans', 'loan system']
    }
    
    for db_name, patterns in db_patterns.items():
        for pattern in patterns:
            if pattern in user_input_lower:
                return db_name
    
    # Default to primary if no preference detected
    return None


def get_db_engine(database='primary'):
    """Get SQLAlchemy engine for specified database."""
    config = databases.get(database)
    if not config:
        raise ValueError(f"Database '{database}' not configured")
    return create_engine(
        f"{config['dialect']}+{config['driver']}://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
    )

def is_cache_valid():
    """Check if schema cache is still valid."""
    return (time.time() - _schema_cache['last_updated']) < SCHEMA_CACHE_TTL and \
           _schema_cache['table_schema'] is not None and \
           _schema_cache['relationships'] is not None

def get_table_schema(force_refresh=False):
    """Fetch schema from all configured databases with caching."""
    if not force_refresh and is_cache_valid():
        return _schema_cache['table_schema']
    
    table_schema = {}
    max_retries = 3
    
    for db_name in databases:
        engine = get_db_engine(db_name)
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                inspector = inspect(engine)
                db_label = databases[db_name]['database']
                for table in inspector.get_table_names():
                    columns = inspector.get_columns(table)
                    full_table_name = f"{db_label}.{table}"
                    table_schema[full_table_name] = {
                        col['name']: str(col['type']) for col in columns
                    }
                # Success, exit retry loop
                break
            except SQLAlchemyError as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff
                current_app.logger.warning(
                    f"Schema error ({db_name}), attempt {retry_count}/{max_retries}: {str(e)}. "
                    f"Retrying in {wait_time}s."
                )
                time.sleep(wait_time)
            finally:
                engine.dispose()
    
    # Only update cache if we found tables
    if table_schema:
        _schema_cache['table_schema'] = table_schema
        _schema_cache['last_updated'] = time.time()
    
    return table_schema

def get_table_relationships(force_refresh=False):
    """Fetch relationships across all databases with caching."""
    if not force_refresh and is_cache_valid():
        return _schema_cache['relationships']
    
    relationships = []
    max_retries = 3
    
    for db_name in databases:
        engine = get_db_engine(db_name)
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                inspector = inspect(engine)
                db_label = databases[db_name]['database']
                for table in inspector.get_table_names():
                    for fk in inspector.get_foreign_keys(table):
                        if fk['referred_columns']:  # Check if not empty
                            relationships.append({
                                'source_table': f"{db_label}.{table}",
                                'source_column': fk['constrained_columns'][0] if fk['constrained_columns'] else '',
                                'target_table': f"{db_label}.{fk['referred_table']}",
                                'target_column': fk['referred_columns'][0] if fk['referred_columns'] else ''
                            })
                # Success, exit retry loop
                break
            except SQLAlchemyError as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff
                current_app.logger.warning(
                    f"Relationships error ({db_name}), attempt {retry_count}/{max_retries}: {str(e)}. "
                    f"Retrying in {wait_time}s."
                )
                time.sleep(wait_time)
            finally:
                engine.dispose()
    
    # Only update cache if we found relationships
    if relationships:
        _schema_cache['relationships'] = relationships
        _schema_cache['last_updated'] = time.time()
    
    return relationships

def validate_schema_completeness():
    """Check if schema discovery found a reasonable number of tables."""
    schema = get_table_schema()
    if not schema or len(schema) < 1:
        current_app.logger.error("Schema discovery failed: No tables found")
        return False
    
    # Check each configured database
    for db_name, config in databases.items():
        db_label = config['database']
        db_tables = [t for t in schema.keys() if t.startswith(f"{db_label}.")]
        if not db_tables:
            current_app.logger.error(f"Schema discovery issue: No tables found for {db_label}")
            return False
    
    return True

def generate_system_prompt(preferred_db=None):
    """Generate prompt with multi-database schema, optionally focusing on a specific database."""
    # Ensure schema is valid
    if not validate_schema_completeness():
        # Force refresh schema if validation fails
        get_table_schema(force_refresh=True)
        get_table_relationships(force_refresh=True)
        
        # Check again after refresh
        if not validate_schema_completeness():
            current_app.logger.error("Critical error: Schema discovery failed even after refresh")
            # Return a minimal prompt
            return """
            You are a SQL assistant. The database schema couldn't be fully loaded.
            Please respond with general guidance but note that specific column details
            may be unavailable. If the user asks for SQL, explain that schema information
            is currently limited.
            """
    
    schema = get_table_schema()
    relationships = get_table_relationships()

    # Format tables with optional focus on preferred database
    table_info = []
    
    for table, cols in schema.items():
        # Extract the database name from the table's full name
        db_name = table.split('.')[0]
        
        # If there's a preferred database, prioritize those tables
        db_config = next((config for name, config in databases.items() 
                          if config['database'] == db_name), None)
        
        if preferred_db and db_config:
            db_key = next((key for key, val in databases.items() 
                          if val['database'] == db_name), None)
            
            # Skip tables not in preferred database
            if db_key != preferred_db:
                continue
                
        col_list = "\n    ".join([f"- {name} ({dtype})" for name, dtype in cols.items()])
        table_info.append(f"Table {table}:\n    {col_list}")

    # Format relationships, focusing on preferred database if specified
    rel_info = []
    for r in relationships:
        source_db = r['source_table'].split('.')[0]
        target_db = r['target_table'].split('.')[0]
        
        # Skip relationships not involving preferred database
        if preferred_db:
            db_name = databases[preferred_db]['database']
            if db_name not in [source_db, target_db]:
                continue
                
        rel_info.append(
            f"- {r['source_table']}.{r['source_column']} → {r['target_table']}.{r['target_column']}"
        )

    # Pre-format sections
    formatted_table_section = "\n\n".join(table_info)
    formatted_rel_section = '\n'.join(rel_info) if rel_info else '- No relationships found'

    # Database focus note
    focus_note = ""
    if preferred_db:
        db_name = databases[preferred_db]['database']
        focus_note = f"\n\nFOCUS ON DATABASE: {db_name}\nThe user wants to query the {db_name} database specifically. Prioritize tables from this database."

    # Enhanced prompt
    system_prompt = f"""
You are a multi-database SQL assistant. Follow these rules precisely:

1. Database Schema (ALWAYS include database prefix with tables):
{formatted_table_section}

2. Database Relationships:
{formatted_rel_section}{focus_note}

3. Critical Requirements:
   - ALWAYS prefix tables with their database name (e.g., sacco_db.members)
   - Use database1.table1 JOIN database2.table2 syntax for cross-database queries
   - Always verify database prefixes match configured names
   - For every query, double-check that all tables referenced exist in the schema
   - Always use SELECT queries only, never modification queries

4. Response Format:
   - Always put SQL queries inside ```sql and ``` tags
   - Make SQL the PRIMARY content of your response
   - After the SQL, provide a brief explanation (no more than 2 sentences)
   - NEVER say "Here's a SQL query that..." - just provide the SQL directly

5. Error Prevention:
   - Always include all necessary JOINs
   - Always check column names against the schema
   - Use aliases for clarity when joining tables
   - Verify that tables exist before referencing them

Example good response:
```sql
SELECT sacco_db.members.name, loan_system.loans.amount 
FROM sacco_db.members 
JOIN loan_system.loans ON sacco_db.members.id = loan_system.loans.member_id
WHERE sacco_db.members.status = 'active'
```
This query retrieves active members with their loan amounts.
"""
    return system_prompt

def call_mistral_api(user_input, preferred_db=None):
    """Call Mistral API with improved error handling and retries."""
    headers = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Generate dynamic system prompt with table schema, considering preferred database
    system_prompt = generate_system_prompt(preferred_db)

    # Modify user input to clarify the database focus if preferred_db is specified
    enhanced_input = user_input
    if preferred_db:
        db_name = databases[preferred_db]['database']
        enhanced_input = f"For the {db_name} database: {user_input}"
        
    # Add a note about table naming conventions based on actual schema
    schema = get_table_schema()
    table_examples = []
    
    # Extract actual table names to use as examples
    for table_name in schema.keys():
        # Get just the table part without the database prefix
        table_only = table_name.split('.')[-1] if '.' in table_name else table_name
        table_examples.append(table_only)
    
    # Take up to 5 examples
    example_tables = ', '.join([f"'{table}'" for table in table_examples[:5]])
    
    # Add naming convention guidance to the prompt
    enhanced_input = f"{enhanced_input}\n\nIMPORTANT: Use the EXACT table and column names as they appear in the schema. Examples of actual table names: {example_tables}."

    data = {
        'model': MODEL_NAME,
        'messages': [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Convert this to SQL (respond with SQL code only): {enhanced_input}"}
        ],
        'max_tokens': 600,
        'temperature': 0.2
    }

    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.post(MISTRAL_API_URL, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                api_response = response.json()
                if 'choices' in api_response and api_response['choices']:
                    return api_response['choices'][0]['message']['content'].strip()
                else:
                    current_app.logger.error("Mistral API returned an empty response")
            else:
                current_app.logger.error(f"Mistral API error: {response.status_code} - {response.text}")
            
            # If we get here, something went wrong
            retry_count += 1
            wait_time = 2 ** retry_count  # Exponential backoff
            if retry_count < max_retries:
                current_app.logger.warning(f"Retrying API call ({retry_count}/{max_retries}) in {wait_time}s")
                time.sleep(wait_time)
            
        except Exception as e:
            current_app.logger.error(f"API request error: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2 ** retry_count)  # Exponential backoff
    
    return None


def clean_sql_response(response):
    """Extract SQL code block from the AI response with improved pattern matching."""
    if not response:
        return ""
        
    # Try to match SQL code blocks with multiple patterns
    patterns = [
        r"```sql\s+(.*?)\s+```",  # Standard SQL code block
        r"```\s+(SELECT.*?)\s+```",  # Generic code block with SELECT
        r"```(SELECT.*?)```",  # No whitespace
        r"SELECT\s+.*?FROM.*?(?:WHERE.*?)?(?:GROUP BY.*?)?(?:HAVING.*?)?(?:ORDER BY.*?)?(?:LIMIT\s+\d+)?(?:;|\n|$)"  # Raw SQL pattern
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1).strip()
            # Ensure it's a SELECT query
            if sql.upper().startswith("SELECT"):
                return sql
    
    # If no SQL found, check if it's a raw SQL query
    if response.strip().upper().startswith("SELECT"):
        # Extract the SQL query up to a natural boundary
        lines = response.strip().split('\n')
        sql_lines = []
        for line in lines:
            sql_lines.append(line)
            if ";" in line:
                break
            if not line.strip() and sql_lines:  # Empty line after content
                break
        
        sql = " ".join(sql_lines).strip()
        # Basic validation to ensure it looks like SQL
        if " FROM " in sql.upper():
            return sql
    
    return ""

def normalize_table_name(table_name):
    """Convert table name to different common formats for fallback attempts."""
    # Original name
    formats = [table_name]
    
    # CamelCase to snake_case (LoanLedgerEntries -> loan_ledger_entries)
    snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', table_name).lower()
    if snake_case != table_name.lower():
        formats.append(snake_case)
    
    # snake_case to CamelCase (loan_ledger_entries -> LoanLedgerEntries)
    if '_' in table_name:
        camel_case = ''.join(word.capitalize() for word in table_name.split('_'))
        formats.append(camel_case)
    
    # Lowercase version
    formats.append(table_name.lower())
    
    # Uppercase first letter
    formats.append(table_name[0].upper() + table_name[1:] if table_name else '')
    
    # Return unique formats
    return list(set(formats))

def is_valid_sql(query, preferred_db=None):
    """Validate SQL with enhanced security checks."""
    if not query:
        return False
        
    query = query.strip().rstrip(';')
    # Remove all known database prefixes from table references
    original_query = query
    for db in databases.values():
        db_name = db['database']
        # Use regex to replace all instances of 'db_name.' with empty string
        query = re.sub(r'\b' + re.escape(db_name) + r'\.', '', query)
    
    if original_query != query:
        current_app.logger.debug(f"SQL before prefix stripping: {original_query}")
        current_app.logger.debug(f"SQL after prefix stripping (validation): {query}")
    q_upper = query.upper()
    
    # Expanded security checks
    forbidden_keywords = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", 
        "RENAME", "GRANT", "REVOKE", "--", "/*", "*/", "EXEC", "EXECUTE",
        "UNION", "INTO OUTFILE", "LOAD_FILE"
    }
    
    if not q_upper.startswith("SELECT"):
        return False
        
    if any(kw in q_upper for kw in forbidden_keywords):
        current_app.logger.warning(f"SQL validation failed: Forbidden keyword detected in: {query}")
        return False

    # Get schema to find actual table names
    schema = get_table_schema()
    actual_tables = {}
    
    # Create a mapping of possible table name variations to actual table names
    for full_table_name in schema.keys():
        table_name = full_table_name.split('.')[-1]  # Remove DB prefix
        for variant in normalize_table_name(table_name):
            actual_tables[variant.lower()] = table_name
    
    # Use the correct database for validation
    engine = get_db_engine(preferred_db if preferred_db else 'primary')
    
    # First try with the original query
    try:
        with engine.connect() as conn:
            conn.execute(text("SET @sql = :query"), {"query": query})
            conn.execute(text("PREPARE stmt FROM @sql"))
            conn.execute(text("DEALLOCATE PREPARE stmt"))
        return True
    except SQLAlchemyError as e:
        error_msg = str(e)
        current_app.logger.debug(f"First validation attempt failed: {error_msg}")
        # If the error is about a table not existing, try to identify and fix the table name
        if "doesn't exist" in error_msg.lower() and "table" in error_msg.lower():
            # Try to extract the problematic table name from the error message
            table_match = re.search(r"Table '.*?\.(.*?)' doesn't exist", error_msg)
            if table_match:
                problem_table = table_match.group(1)
                current_app.logger.debug(f"Problem table identified: {problem_table}")
                
                # Check if we have a mapping for this table name
                if problem_table.lower() in actual_tables:
                    correct_table = actual_tables[problem_table.lower()]
                    current_app.logger.debug(f"Found correct table name: {correct_table}")
                    
                    # Replace the incorrect table name with the correct one
                    fixed_query = re.sub(r'\b' + re.escape(problem_table) + r'\b', correct_table, query)
                    current_app.logger.debug(f"Attempting with fixed query: {fixed_query}")
                    
                    # Try again with the fixed query
                    try:
                        with engine.connect() as conn:
                            conn.execute(text("SET @sql = :query"), {"query": fixed_query})
                            conn.execute(text("PREPARE stmt FROM @sql"))
                            conn.execute(text("DEALLOCATE PREPARE stmt"))
                        return True
                    except SQLAlchemyError as retry_error:
                        current_app.logger.error(f"Retry validation error: {str(retry_error)}")
        
        # Log detailed diagnostics for the final error
        current_app.logger.error(f"Query validation error: {error_msg}")
        
        # More detailed error diagnostics
        if "syntax error" in error_msg.lower():
            current_app.logger.error("SQL syntax error detected")
        elif "unknown column" in error_msg.lower():
            current_app.logger.error("Unknown column referenced in query")
        elif "doesn't exist" in error_msg.lower():
            current_app.logger.error("Table or database doesn't exist")
            
        return False
    
def execute_sql_query(query, params=None, preferred_db=None):
    """Execute query with improved error handling and result processing."""
    if not query:
        return None
        
    # Remove all known database prefixes from table references
    original_query = query
    for db in databases.values():
        db_name = db['database']
        # Use regex to replace all instances of 'db_name.' with empty string
        query = re.sub(r'\b' + re.escape(db_name) + r'\.', '', query)
    
    if original_query != query:
        current_app.logger.debug(f"SQL before prefix stripping: {original_query}")
        current_app.logger.debug(f"SQL after prefix stripping (execution): {query}")

    # Use the preferred database if specified, otherwise use default
    engine = get_db_engine(preferred_db if preferred_db else 'primary')
    start_time = time.time()
    
    try:
        with engine.connect() as conn:
            # Set a reasonable query timeout
            conn.execute(text("SET SESSION MAX_EXECUTION_TIME=10000"))  # 10 seconds
            
            # Execute the query
            result = conn.execute(text(query), params or {})
            
            # Process the results
            column_names = result.keys()
            rows = []
            
            for row in result:
                row_dict = {}
                for idx, col_name in enumerate(column_names):
                    # Handle different data types appropriately
                    value = row[idx]
                    if value is not None:
                        # Convert dates/timestamps to strings
                        if hasattr(value, 'isoformat'):
                            value = value.isoformat()
                    row_dict[col_name] = value
                rows.append(row_dict)
            
            # Log performance metrics
            execution_time = time.time() - start_time
            current_app.logger.info(f"Query executed in {execution_time:.3f}s with {len(rows)} rows returned")
            
            return rows
    except SQLAlchemyError as e:
        current_app.logger.error(f"Query execution failed: {str(e)}")
        return None


def generate_natural_response(user_input, query_result, sql_query):
    """Generate a natural language response with context about the query."""
    headers = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Enhanced system prompt for better responses
    system_prompt = """You are a helpful financial database assistant that explains results clearly. Follow these rules:
1. Respond in complete, friendly sentences that directly answer the user's question
2. NEVER mention SQL syntax or column names directly
3. Translate technical database terms into user-friendly language
4. For numerical results, format large numbers with commas (e.g., 1,234,567) but DO NOT include currency symbols
5. For empty results, explain possible reasons why no data was found
6. Keep responses concise but informative (2-3 sentences maximum)
7. If there are multiple rows, summarize the overall pattern or highlight key findings
8. Avoid technical jargon unless the user specifically asks for technical details
9. ALWAYS be consistent in your response style and tone
10. For financial data, explain what the numbers represent but WITHOUT using currency terms
11. If the query is about a specific person, mention their name in the response
12. NEVER say 'I found X results' - instead provide the actual information"""

    # Add context about the number of results
    result_count = len(query_result) if query_result else 0
    result_preview = str(query_result[:3]) if query_result else "[]"
    
    # Extract key entities from the user's question for better context
    user_question = user_input.strip()
    
    user_content = f"""Original question: {user_question}
SQL query executed: {sql_query}
Number of results: {result_count}
Database results preview: {result_preview}
Full results: {json.dumps(query_result, default=str)}

Please provide a helpful, natural language response to the user's question based on these results.
Format large numbers with commas for readability (e.g., 1,234,567) but DO NOT include currency symbols.
Be specific about what the numbers represent, but avoid currency terminology.
Directly answer the user's question without saying 'I found X results'."""

    data = {
        'model': MODEL_NAME,
        'messages': [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        'temperature': 0.3,
        'max_tokens': 200
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            api_response = response.json()
            if api_response.get('choices'):
                return api_response['choices'][0]['message']['content'].strip()
        # More informative fallback responses
        if query_result:
            # Try to create a more helpful fallback response based on the data
            if len(query_result) == 1 and query_result[0]:
                # For a single result, try to extract meaningful information
                row = query_result[0]
                # Look for common financial fields
                financial_fields = ['amount', 'balance', 'outstanding', 'total', 'sum', 'value']
                name_fields = ['name', 'fullname', 'full_name', 'member', 'customer', 'client']
                
                # Try to find a name in the result
                name_value = None
                for key in row.keys():
                    if any(name_field in key.lower() for name_field in name_fields) and row[key]:
                        name_value = row[key]
                        break
                        
                # Try to find a financial value in the result
                financial_value = None
                for key in row.keys():
                    if any(field in key.lower() for field in financial_fields) and row[key]:
                        financial_value = row[key]
                        break
                        
                if name_value and financial_value:
                    # Format large numbers with commas
                    try:
                        if isinstance(financial_value, (int, float, complex)) or str(financial_value).replace('.', '', 1).isdigit():
                            formatted_value = '{:,}'.format(float(financial_value))
                        else:
                            formatted_value = financial_value
                    except:
                        formatted_value = financial_value
                    return f"{name_value} has a value of {formatted_value}."
                elif financial_value:
                    # Format large numbers with commas
                    try:
                        if isinstance(financial_value, (int, float, complex)) or str(financial_value).replace('.', '', 1).isdigit():
                            formatted_value = '{:,}'.format(float(financial_value))
                        else:
                            formatted_value = financial_value
                    except:
                        formatted_value = financial_value
                    return f"The value is {formatted_value}."
                else:
                    # Generic single result response
                    return f"Found information: {', '.join([f'{k}: {v}' for k, v in row.items() if v])}"
            else:
                # Multiple results fallback
                return f"Found {len(query_result)} records with the requested information."
        return "No data was found matching your criteria. Please check your query or try different search terms."
    except Exception as e:
        current_app.logger.error(f"Natural response error: {str(e)}")
        return "Here are your results." if query_result else "No results found."

@user_bp.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400

    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    # Get database preference from request
    database_hint = request.json.get('database_hint')
    preferred_db = None
    
    # Map the frontend database value to backend database key
    if database_hint:
        if database_hint == 'sacco_db':
            preferred_db = 'primary'
        elif database_hint == 'loan_system':
            preferred_db = 'secondary'

    try:
        # Start with healthcheck for database and schema
        try:
            if not validate_schema_completeness():
                current_app.logger.warning("Schema validation failed, refreshing...")
                get_table_schema(force_refresh=True)
                get_table_relationships(force_refresh=True)
        except Exception as schema_error:
            current_app.logger.error(f"Schema healthcheck failed: {str(schema_error)}")
            # Continue anyway - we'll handle schema issues in the prompt

        # Step 1: Get raw AI response with database preference
        raw_response = call_mistral_api(user_input, preferred_db)
        if not raw_response:
            return jsonify({
                'type': 'error',
                'content': "I'm having trouble connecting to the database. Please try again."
            }), 500

        # Step 2: Extract SQL query from response
        cleaned_sql = clean_sql_response(raw_response)
        
        # Log intermediate results
        current_app.logger.debug(f"Raw AI Response: {raw_response}")
        current_app.logger.debug(f"Extracted SQL: {cleaned_sql}")

        # Step 3: Handle SQL extraction results
        if not cleaned_sql:
            # No SQL found - return the raw response with an explanation
            current_app.logger.warning("No SQL query found in response")
            return jsonify({
                'type': 'message',
                'content': raw_response,
                'note': "No SQL query could be extracted from the response."
            })

        # Step 4: Validate and execute SQL with preferred database
        if not is_valid_sql(cleaned_sql, preferred_db):
            current_app.logger.warning(f"Invalid SQL query: {cleaned_sql}")
            return jsonify({
                'type': 'error',
                'content': "The generated SQL query was invalid. Please try rephrasing your question.",
                'debug_info': {
                    'query': cleaned_sql,
                    'raw_response': raw_response
                }
            }), 400
            
        # Execute the valid SQL with preferred database
        db_response = execute_sql_query(cleaned_sql, None, preferred_db)
        
        # Step 5: Handle query execution results
        if db_response is None:  # Execution error
            # Get the actual table names for better error messages
            schema = get_table_schema()
            actual_tables = [table_name.split('.')[-1] for table_name in schema.keys()]
            
            return jsonify({
                'type': 'error',
                'content': "There was an error executing the database query. Please try again.",
                'debug_info': {
                    'query': cleaned_sql,
                    'available_tables': actual_tables[:10]  # Show first 10 tables for reference
                }
            }), 500
            
        # Step 6: Generate natural language response
        natural_response = generate_natural_response(user_input, db_response, cleaned_sql)
        
        # Step 7: Return comprehensive response
        return jsonify({
            'type': 'data_response',
            'content': natural_response,
            'sql': cleaned_sql,
            'data': db_response,
            'row_count': len(db_response) if db_response else 0
        })

    except Exception as e:
        current_app.logger.error(f"Chat processing error: {str(e)}", exc_info=True)
        return jsonify({
            'type': 'error',
            'content': "An unexpected error occurred while processing your request."
        }), 500
        
@user_bp.route('/overdue_loans', methods=['GET'])
@login_required
def get_overdue_loans():
    try:
        # Statically define the module ID
        module_id = 1  # Replace with the desired module ID

        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 400

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    # Retrieve expected and actual columns as lists
                    expected_columns = expected.columns  # e.g., ['LoanID', 'LedgerID', ...]
                    actual_columns = actual.columns       # e.g., ['loan_id', 'ledger_id', ...]
                    
                    # Create a dictionary mapping expected to actual columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict  # Now a dictionary
                    }
                    current_app.logger.info(f"Retrieved mapping: {mapping}")
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
            current_app.logger.info(f"Mapping Data: {mapping}")
        except Exception as e:
            return jsonify({'error': f'Error retrieving mapping data: {str(e)}'}), 500

        # Build dynamic query
        def build_dynamic_query(mapping):
            try:
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})
                m = mapping.get("Members", {}) 
        
                # Ensure that the necessary columns are present in the mapping
                required_ll_columns = ["LoanID", "LedgerID", "OutstandingBalance", "ArrearsAmount", "ArrearsDays"]
                required_ld_columns = ["LoanAppID", "LoanStatus"]
                required_la_columns = ["LoanAppID", "LoanNo", "LoanAmount", "MemberID"]  # Added MemberID
                required_m_columns = ["MemberID", "FirstName", "LastName"]
        
                if not all(column in ll.get("columns", []) for column in required_ll_columns):
                    raise KeyError(f"Missing columns in LoanLedgerEntries mapping: {required_ll_columns}")
        
                if not all(column in ld.get("columns", []) for column in required_ld_columns):
                    raise KeyError(f"Missing columns in LoanDisbursements mapping: {required_ld_columns}")
        
                if not all(column in la.get("columns", []) for column in required_la_columns):
                    raise KeyError(f"Missing columns in LoanApplications mapping: {required_la_columns}")
        
                if not all(column in m.get("columns", []) for column in required_m_columns):
                    raise KeyError(f"Missing columns in Members mapping: {required_m_columns}")
        
                query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    l.{ll["columns"]["ArrearsAmount"]} AS ArrearsAmount,
                    l.{ll["columns"]["ArrearsDays"]} AS ArrearsDays,
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus,
                    CONCAT(m.{m["columns"]["FirstName"]}, ' ', m.{m["columns"]["LastName"]}) AS CustomerName
                FROM {ll["actual_table_name"]} l
                JOIN (
                    SELECT {ll["columns"]["LoanID"]} AS LoanID,
                        MAX({ll["columns"]["LedgerID"]}) AS latest_id
                    FROM {ll["actual_table_name"]}
                    GROUP BY {ll["columns"]["LoanID"]}
                ) latest ON l.{ll["columns"]["LoanID"]} = latest.LoanID AND l.{ll["columns"]["LedgerID"]} = latest.latest_id
                JOIN {la["actual_table_name"]} la ON l.{ll["columns"]["LoanID"]} = la.{la["columns"]["LoanAppID"]}
                JOIN {ld["actual_table_name"]} ld ON la.{la["columns"]["LoanAppID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN {m["actual_table_name"]} m ON la.{la["columns"]["MemberID"]} = m.{m["columns"]["MemberID"]}
                WHERE ld.{ld["columns"]["LoanStatus"]} = 'Active'
                ORDER BY l.{ll["columns"]["LoanID"]}
                """
                current_app.logger.info(f"Built query: {query}")
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        try:
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            loan_data = cursor.fetchall()
            current_app.logger.info(f"Fetched Loan Data: {loan_data}")
        except Exception as e:
            return jsonify({'error': f'Error executing query: {str(e)}'}), 500

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


