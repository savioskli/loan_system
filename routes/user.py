from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models.module import Module, FormField
from models.form_section import FormSection
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
    try:
        # Get the module
        module = Module.query.filter_by(code=module_code).first_or_404()
        
        # Get module sections with fields
        sections = module.sections.filter_by(is_active=True).order_by(FormSection.order).all()
        
        # Get client types and products
        client_types = ClientType.query.filter(ClientType.status == True).all()
        products = Product.query.filter(Product.status == 'Active').all()
        
        # Kenya counties for postal town
        counties = KENYA_COUNTIES if 'KENYA_COUNTIES' in globals() else [
            'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Thika',
            'Kitale', 'Malindi', 'Garissa', 'Kakamega'
        ]
        
        # Create a dynamic form with CSRF protection
        class DynamicForm(FlaskForm):
            pass
        form = DynamicForm()
        
        if request.method == 'POST':
            form_data = request.form.to_dict()
            
            # Get the client type from the form
            client_type_id = form_data.get('client_type')
            if client_type_id:
                client_type_id = int(client_type_id)
                
                # Validate fields based on client type restrictions
                for section in sections:
                    for field in section.fields:
                        field_name = field.field_name
                        if field_name in form_data:
                            restrictions = field.client_type_restrictions or []
                            if restrictions and client_type_id not in restrictions:
                                del form_data[field_name]
            
            # Process the validated form data
            try:
                # Here you would typically save the form data to your database
                flash('Form submitted successfully!', 'success')
                return redirect(url_for('user.dashboard'))
                
            except Exception as e:
                current_app.logger.error(f"Error processing form: {str(e)}")
                flash('An error occurred while processing your form. Please try again.', 'error')
        
        # Return the template with all necessary data
        return render_template('user/dynamic_form.html',
                            module=module,
                            sections=sections,
                            form=form,
                            form_data={},
                            client_types=client_types,
                            products=products,
                            counties=counties)
                            
    except Exception as e:
        current_app.logger.error(f"Error in dynamic_form: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the form. Please try again.', 'error')
        return redirect(url_for('user.dashboard'))

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
