from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models.module import Module, FormField
from models.form_section import FormSection
from models.product import Product
from models.client_type import ClientType
from extensions import db, csrf
from flask_wtf import FlaskForm
import os
import json
from werkzeug.utils import secure_filename
from data.kenya_locations import KENYA_COUNTIES
from sqlalchemy import and_, or_, text, MetaData, Table
from datetime import datetime
import traceback
from models.staff import Staff

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
    
    # Get additional modules (not CLM or LN)
    additional_modules = Module.query.filter(
        and_(
            ~Module.code.like('CLM%'),
            ~Module.code.like('LN%'),
            Module.parent_id == None,
            Module.is_active == True
        )
    ).order_by(Module.code).all()
    
    return render_template('user/dashboard.html',
                         pending_clients=pending_clients,
                         pending_loans=pending_loans,
                         approved_loans=approved_loans,
                         rejected_loans=rejected_loans,
                         portfolio_value=portfolio_value,
                         client_modules=client_modules,
                         loan_modules=loan_modules,
                         client_parent=client_parent,
                         loan_parent=loan_parent,
                         additional_modules=additional_modules,
                         Module=Module)  # Pass Module class for querying additional modules

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
                            counties=KENYA_COUNTIES,
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

@user_bp.route('/get_postal_towns/<county>')
@login_required
def get_postal_towns(county):
    """Get postal towns for a given county."""
    try:
        # Clean the county name
        county = county.strip()
        
        # Check if county exists in our data
        if county in KENYA_COUNTIES:
            # Use the sub-counties as postal towns
            towns = sorted(KENYA_COUNTIES[county])  # Sort alphabetically
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
            raise ValueError('Client type is required')
            
        client_type_id = int(client_type_id)
        client_type = ClientType.query.get(client_type_id)
        if not client_type:
            raise ValueError('Invalid client type')
            
        if module_code == 'CLM01':  # Prospect Registration
            # Prepare SQL query
            sql = text("""
                INSERT INTO form_data_clm01 (
                    user_id, submission_date, status, client_type_id, client_type,
                    purpose_of_visit, purpose_description, product, first_name,
                    middle_name, last_name, gender, id_type, id_number,
                    serial_number, company_name, birth_date, member_count,
                    postal_address, postal_code, postal_town, mobile_phone,
                    email, county, sub_county, ward, village, trade_center
                ) VALUES (
                    :user_id, :submission_date, :status, :client_type_id, :client_type,
                    :purpose_of_visit, :purpose_description, :product, :first_name,
                    :middle_name, :last_name, :gender, :id_type, :id_number,
                    :serial_number, :company_name, :birth_date, :member_count,
                    :postal_address, :postal_code, :postal_town, :mobile_phone,
                    :email, :county, :sub_county, :ward, :village, :trade_center
                )
            """)
            
            # Prepare data
            data = {
                'user_id': current_user.id,
                'submission_date': datetime.utcnow(),
                'status': 'Pending',
                'client_type_id': client_type_id,
                'client_type': client_type.client_name,
                'purpose_of_visit': form_data.get('purpose_of_visit', ''),
                'purpose_description': form_data.get('purpose_description'),
                'product': form_data.get('product', ''),
                'first_name': form_data.get('first_name', ''),
                'middle_name': form_data.get('middle_name'),
                'last_name': form_data.get('last_name', ''),
                'gender': form_data.get('gender', ''),
                'id_type': form_data.get('id_type', ''),
                'id_number': form_data.get('id_number', ''),
                'serial_number': form_data.get('serial_number'),
                'company_name': form_data.get('company_name'),
                'birth_date': form_data.get('birth_date'),
                'member_count': form_data.get('member_count'),
                'postal_address': form_data.get('postal_address', ''),
                'postal_code': form_data.get('postal_code', ''),
                'postal_town': form_data.get('postal_town', ''),
                'mobile_phone': form_data.get('mobile_phone', ''),
                'email': form_data.get('email'),
                'county': form_data.get('county', ''),
                'sub_county': form_data.get('sub_county', ''),
                'ward': form_data.get('ward'),
                'village': form_data.get('village'),
                'trade_center': form_data.get('trade_center')
            }
            
            # Execute query
            db.session.execute(sql, data)
            db.session.commit()
            
            flash('Prospect registered successfully!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Form submitted successfully!', 'success')
            return redirect(url_for('user.dashboard'))
            
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('user.dynamic_form', module_code=module_code))
    except Exception as e:
        current_app.logger.error(f"Error processing form: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while processing your form. Please try again.', 'error')
        return redirect(url_for('user.dynamic_form', module_code=module_code))

@user_bp.route('/reports')
@login_required
def reports():
    # TODO: Implement reports page
    return render_template('user/reports.html')
