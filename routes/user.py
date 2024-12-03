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

@user_bp.route('/prospects')
@login_required
def prospects():
    """List all prospect registrations."""
    try:
        # Get search parameters
        search_query = request.args.get('search', '').strip()
        
        # Create a query to fetch prospects
        sql = text("""
            SELECT 
                fd.*,
                s.username as staff_username,
                COALESCE(ct.client_name, fd.client_type) as client_type_name
            FROM form_data_clm01 fd
            LEFT JOIN staff s ON s.id = fd.user_id
            LEFT JOIN client_types ct ON ct.id = fd.client_type_id AND ct.status = 1
            ORDER BY fd.submission_date DESC
        """)
        
        # Execute query
        result = db.session.execute(sql)
        prospects = result.fetchall()
        
        return render_template('user/prospects.html', 
                            prospects=prospects,
                            search_query=search_query)
                            
    except Exception as e:
        current_app.logger.error(f"Error loading prospects: {str(e)}\n{traceback.format_exc()}")
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

@user_bp.route('/prospects/<int:prospect_id>', methods=['DELETE'])
@login_required
def delete_prospect(prospect_id):
    """Delete a prospect registration."""
    try:
        # Verify CSRF token
        token = request.headers.get('X-CSRFToken')
        if not token or not csrf.validate_csrf(token):
            return jsonify({'success': False, 'message': 'Invalid CSRF token'}), 400
            
        # Delete the prospect
        sql = text("""
            DELETE FROM form_data_clm01
            WHERE id = :prospect_id AND user_id = :user_id
        """)
        
        result = db.session.execute(sql, {
            'prospect_id': prospect_id,
            'user_id': current_user.id
        })
        db.session.commit()
        
        if result.rowcount > 0:
            return jsonify({'success': True, 'message': 'Prospect deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Prospect not found or you do not have permission to delete it'}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting prospect: {str(e)}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while deleting the prospect'}), 500

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
            return redirect(url_for('user.prospects'))
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
