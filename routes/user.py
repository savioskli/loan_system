import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
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
from extensions import db, csrf
from flask_wtf import FlaskForm
from services.scheduler import get_cached_tables
from datetime import datetime
import traceback
import os
import json
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_, text, MetaData, Table
import time
from flask import current_app
from routes.collection_schedule import collection_schedule_bp

user_bp = Blueprint('user', __name__)

user_bp.register_blueprint(collection_schedule_bp, url_prefix='/user')

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
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    
    print(f"Search request - Query: {query}, Page: {page}")
    
    try:
        # Call mock core banking API
        response = requests.get(f'http://localhost:5003/api/mock/clients/search', params={
            'search': query,  # Changed from 'q' to 'search' to match mock server
            'page': page
        })
        
        print(f"Mock API request URL: {response.url}")
        print(f"Mock API status code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"Mock API response: {data}")
            result = {
                'items': [{
                    'id': client['id'],
                    'text': f"{client['name']} ({client['account_number']})"
                } for client in data['clients']],
                'has_more': data['has_more']
            }
            print(f"Sending to frontend: {result}")
            return jsonify(result)
        else:
            error_msg = f"Failed to fetch clients: {response.status_code} - {response.text}"
            print(error_msg)
            return jsonify({'error': error_msg}), 500
    except Exception as e:
        error_msg = f"Error fetching clients: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

@user_bp.route('/correspondence')
@login_required
def correspondence():
    return render_template('user/correspondence.html')

@user_bp.route('/api/correspondence/<client_id>')
@login_required
def get_correspondence(client_id):
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

@user_bp.route('/api/correspondence', methods=['POST'])
@login_required
def save_correspondence():
    data = request.form  # Get the form data from the request
    client_id = data.get('client_name')  # Adjusted to match the form field names
    communication_type = data.get('type')
    content = data.get('message')  # Adjusted to match the form field names
    account_no = data.get('account_no')
    sent_by = current_user.username  # Assuming sent_by is the current user's username

    # Validate data here (e.g., check if fields are not empty)
    if not client_id or not communication_type or not content or not account_no or not sent_by:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
    
    # Create a new Correspondence object
    new_correspondence = Correspondence(
        account_no=account_no,
        client_name=client_id,
        type=communication_type,
        message=content,
        status='pending',
        sent_by=sent_by
    )
    db.session.add(new_correspondence)
    db.session.commit()  # Save to the database

    return jsonify({'success': True, 'message': 'Correspondence saved successfully'}), 201

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
    # Get loan grading data from Navision
    tables, last_sync = get_cached_tables()
    loan_data = []
    
    # Calculate key metrics
    total_loans = 0
    overdue_loans = {
        'NORMAL': {'count': 0, 'amount': 0, 'description': '0-30 days'},
        'WATCH': {'count': 0, 'amount': 0, 'description': '31-90 days'},
        'SUBSTANDARD': {'count': 0, 'amount': 0, 'description': '91-180 days'},
        'DOUBTFUL': {'count': 0, 'amount': 0, 'description': '181-360 days'},
        'LOSS': {'count': 0, 'amount': 0, 'description': '>360 days'}
    }
    total_outstanding = 0
    total_in_arrears = 0
    
    try:
        # Make request to mock server
        response = requests.get(
            'http://localhost:5003/api/beta/companies/loan-grading',
            headers={'Database': 'navision_db'},
            auth=('admin', 'admin123')
        )
        
        if response.status_code == 200:
            # The response format is {'value': [...]} so we need to get the 'value' key
            loan_data = response.json().get('value', [])
            for loan in loan_data:
                total_loans += 1
                total_outstanding += loan['Outstanding_Balance']
                total_in_arrears += loan['Total_In_Arrears']
                if loan['Classification'] in overdue_loans:
                    overdue_loans[loan['Classification']]['count'] += 1
                    overdue_loans[loan['Classification']]['amount'] += loan['Outstanding_Balance']
    except Exception as e:
        print(f"Error fetching loan data: {str(e)}")
        flash('Error fetching loan data from core banking system', 'error')
    
    # Calculate recovery rate (recovered amount / total in arrears)
    recovery_rate = ((total_outstanding - total_in_arrears) / total_outstanding * 100) if total_outstanding > 0 else 0
    
    # Calculate NPL ratio (non-performing loans / total outstanding)
    npl_amount = overdue_loans['SUBSTANDARD']['amount'] + overdue_loans['DOUBTFUL']['amount'] + overdue_loans['LOSS']['amount']
    npl_ratio = (npl_amount / total_outstanding * 100) if total_outstanding > 0 else 0
    
    # Calculate NPL Coverage Ratio (provisions / NPL amount)
    provision_rate = {
        'NORMAL': 0.01,  # 1% provision
        'WATCH': 0.05,   # 5% provision
        'SUBSTANDARD': 0.25,  # 25% provision
        'DOUBTFUL': 0.50,     # 50% provision
        'LOSS': 1.00          # 100% provision
    }
    total_provisions = sum(overdue_loans[grade]['amount'] * rate for grade, rate in provision_rate.items())
    npl_coverage_ratio = (total_provisions / npl_amount * 100) if npl_amount > 0 else 0
    
    # Calculate Cost of Risk (total provisions / total outstanding)
    cost_of_risk = (total_provisions / total_outstanding * 100) if total_outstanding > 0 else 0
    
    # Calculate PAR30 (Portfolio at Risk > 30 days)
    par30_amount = sum(overdue_loans[grade]['amount'] for grade in ['WATCH', 'SUBSTANDARD', 'DOUBTFUL', 'LOSS'])
    par30_ratio = (par30_amount / total_outstanding * 100) if total_outstanding > 0 else 0
    
    # Prepare data for charts
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
            overdue_loans['NORMAL']['amount'],
            overdue_loans['WATCH']['amount'],
            overdue_loans['SUBSTANDARD']['amount'],
            overdue_loans['DOUBTFUL']['amount'],
            overdue_loans['LOSS']['amount']
        ]
    }
    
    return render_template(
        'user/post_disbursement.html',
        total_loans=total_loans,
        overdue_loans=overdue_loans,
        total_outstanding=total_outstanding,
        total_in_arrears=total_in_arrears,
        recovery_rate=round(recovery_rate, 2),
        npl_ratio=round(npl_ratio, 2),
        npl_coverage_ratio=round(npl_coverage_ratio, 2),
        cost_of_risk=round(cost_of_risk, 2),
        par30_ratio=round(par30_ratio, 2),
        total_provisions=total_provisions,
        classification_data=classification_data,
        loan_data=loan_data,
        last_sync=last_sync
    )

@user_bp.route('/analytics', methods=['GET'])
@login_required
def analytics():
    correspondence_data = Correspondence.query.all()
    records_per_page = 10
    total_records = len(correspondence_data)
    total_pages = (total_records + records_per_page - 1) // records_per_page
    
    # Count by type
    type_counts = {}
    for correspondence in correspondence_data:
        type_counts[correspondence.type] = type_counts.get(correspondence.type, 0) + 1

    # Count by status
    status_counts = {}
    for correspondence in correspondence_data:
        status_counts[correspondence.status] = status_counts.get(correspondence.status, 0) + 1

    # Top clients
    client_counts = {}
    for correspondence in correspondence_data:
        client_counts[correspondence.client_name] = client_counts.get(correspondence.client_name, 0) + 1

    # Calculate statistics
    total_calls = len([c for c in correspondence_data if c.type == 'Call'])
    successful_calls = len([c for c in correspondence_data if c.call_outcome in ['Answered']])
    unsuccessful_calls = len([c for c in correspondence_data if c.call_outcome in ['No Answer', 'Voicemail']])
    call_durations = [c.call_duration for c in correspondence_data if c.type == 'Call']
    average_duration = sum(call_durations) / len(call_durations) if call_durations else 0

    # Calculate statistics for correspondences
    total_correspondences = len(correspondence_data)
    pending_correspondences = len([c for c in correspondence_data if c.status == 'Pending'])
    completed_correspondences = len([c for c in correspondence_data if c.status == 'Completed'])
    failed_deliveries = len([c for c in correspondence_data if c.delivery_status == 'Failed'])

    # Calculate statistics for SMS, Email, Call, Letter, and Visit correspondences
    sms_count = len([c for c in correspondence_data if c.type == 'SMS'])
    email_count = len([c for c in correspondence_data if c.type == 'Email'])
    call_count = len([c for c in correspondence_data if c.type == 'Call'])
    letter_count = len([c for c in correspondence_data if c.type == 'Letter'])
    visit_count = len([c for c in correspondence_data if c.type == 'Visit'])

    return render_template('user/analytics.html', 
                           data=correspondence_data, 
                           type_counts=type_counts, 
                           status_counts=status_counts, 
                           client_counts=client_counts,
                           total_pages=total_pages,
                           total_calls=total_calls,
                           successful_calls=successful_calls,
                           unsuccessful_calls=unsuccessful_calls,
                           average_duration=average_duration,
                           total_correspondences=total_correspondences,
                           pending_correspondences=pending_correspondences,
                           completed_correspondences=completed_correspondences,
                           failed_deliveries=failed_deliveries,
                           sms_count=sms_count,
                           email_count=email_count,
                           call_count=call_count,
                           letter_count=letter_count,
                           visit_count=visit_count)

@user_bp.route('/collection-schedule', methods=['GET'])
@login_required
def collection_schedule():
    return render_template('user/collection_schedule.html')

@user_bp.route('/collection_schedule', methods=['POST'])
@login_required
def create_collection_schedule():
    data = request.json
    new_schedule = CollectionSchedule(
        staff_id=data['staff_id'],
        loan_id=data['loan_id'],
        schedule_date=datetime.strptime(data['schedule_date'], '%Y-%m-%dT%H:%M:%S'),
        status=data['status']
    )
    db.session.add(new_schedule)
    db.session.commit()
    return jsonify({'message': 'Collection schedule created successfully'}), 201

@user_bp.route('/collection_schedule', methods=['GET'])
@login_required
def get_collection_schedules():
    staff_id = request.args.get('staff_id')
    loan_status = request.args.get('loan_status')
    query = CollectionSchedule.query
    if staff_id:
        query = query.filter_by(staff_id=staff_id)
    if loan_status:
        query = query.join(Loan).filter(Loan.status == loan_status)
    schedules = query.all()
    return jsonify([{
        'id': schedule.id,
        'staff_id': schedule.staff_id,
        'loan_id': schedule.loan_id,
        'schedule_date': schedule.schedule_date.isoformat(),
        'status': schedule.status
    } for schedule in schedules]), 200

@user_bp.route('/collection_schedule/<int:schedule_id>', methods=['PUT'])
@login_required
def update_collection_schedule(schedule_id):
    data = request.json
    schedule = CollectionSchedule.query.get_or_404(schedule_id)
    schedule.staff_id = data.get('staff_id', schedule.staff_id)
    schedule.loan_id = data.get('loan_id', schedule.loan_id)
    schedule.schedule_date = datetime.strptime(data['schedule_date'], '%Y-%m-%dT%H:%M:%S')
    schedule.status = data.get('status', schedule.status)
    db.session.commit()
    return jsonify({'message': 'Collection schedule updated successfully'}), 200

@user_bp.route('/collection_schedule/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_collection_schedule(schedule_id):
    schedule = CollectionSchedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'message': 'Collection schedule deleted successfully'}), 200
