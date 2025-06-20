import requests
import os
import re
import sqlparse
import traceback
import mimetypes
from sqlalchemy import create_engine, inspect, text, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import mysql.connector
from datetime import datetime, timedelta
import traceback
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash, send_file, abort, send_from_directory, session, current_app, g
import uuid
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from models.module import Module
from models.form_field import FormField
from models.form_section import FormSection
from models.crb_report import CRBReport
from models.credit_bureau import CreditBureau
from utils.module_permissions import check_module_access, get_accessible_modules
from models.staff import Staff
from models.form_submission import FormSubmission
from models.calendar_event import CalendarEvent
from models.client import Client
from models.correspondence import Correspondence
from models.form_section import FormSection
from models.product import Product
from models.client_type import ClientType
from models.guarantor import Guarantor
from models.field_visit import FieldVisit, FieldVisitStatusHistory, FieldVisitAttachment
from models.legal_case import LegalCase, LegalCaseAttachment
from models.loan import Loan
from services.guarantor_service import GuarantorService
from extensions import db, csrf
from flask_wtf import FlaskForm
from services.scheduler import get_cached_tables
import time
import math
import json
from decimal import Decimal
import traceback
import os
import json
from werkzeug.utils import secure_filename

# Import the collection schedule blueprint
try:
    from routes.collection_schedule import collection_schedule_bp
except ImportError:
    # Create a dummy blueprint if the import fails
    collection_schedule_bp = Blueprint('collection_schedule', __name__, url_prefix='/collection-schedule')
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
from models.legal_case import LegalCase, LegalCaseAttachment
from models.auction import Auction, AuctionHistory, AuctionHistoryAttachment
from models.loan_reschedule import LoanReschedule
from models.loan_refinance import RefinanceApplication
from models.post_disbursement_modules import ExpectedStructure, ActualStructure, PostDisbursementModule
from models import Client
from functools import lru_cache

# Global helper function to add visible_modules to template parameters
def render_with_modules(template, **kwargs):
    visible_modules = PostDisbursementModule.query.filter_by(hidden=False).order_by(PostDisbursementModule.order).all()
    kwargs['visible_modules'] = visible_modules
    return render_template(template, **kwargs)

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/system_field/<int:field_id>', methods=['GET'])
@login_required
def get_system_field_value(field_id):
    """
    Get the value of a system reference field
    
    Args:
        field_id (int): The ID of the system reference field
        
    Returns:
        JSON: The field value or an error message
    """
    from models.system_reference_field import SystemReferenceField
    from models.form_field import FormField
    from models.form_submission import FormSubmission
    from models.client import Client
    
    try:
        current_app.logger.info(f'[API] Fetching system reference field with ID: {field_id}')
        
        # Get the system reference field
        ref_field = SystemReferenceField.query.get(field_id)
        if not ref_field:
            current_app.logger.error(f'[API] System reference field not found with ID: {field_id}')
            return jsonify({
                'success': False,
                'error': 'System reference field not found',
                'debug': {'field_id': field_id}
            }), 404
        
        current_app.logger.info(f'[API] Found system reference field: {ref_field.reference_code} (ID: {ref_field.id})')
        
        # Get all form fields that reference this system field
        form_fields = FormField.query.filter_by(
            system_reference_field_id=field_id
        ).all()
        
        if not form_fields:
            current_app.logger.error(f'[API] No form fields reference system field with ID: {field_id}')
            return jsonify({
                'success': False,
                'error': 'No form fields reference this system field',
                'debug': {'field_id': field_id, 'reference_code': ref_field.reference_code}
            }), 400
        
        current_app.logger.info(f'[API] Found {len(form_fields)} form fields referencing this system field')
        
        # Get the client for the current user
        client = Client.query.filter_by(user_id=current_user.id).first()
        if not client:
            current_app.logger.warning(f'[API] No client found for user ID: {current_user.id}')
            return jsonify({
                'success': False,
                'message': 'No client found for current user',
                'debug': {'user_id': current_user.id}
            })
        
        current_app.logger.info(f'[API] Found client ID: {client.id} for user ID: {current_user.id}')
        
        # Get all submissions for this client and module
        submissions = FormSubmission.query.filter_by(
            client_id=client.id,
            module_id=ref_field.module_id
        ).order_by(FormSubmission.submitted_at.desc()).all()
        
        current_app.logger.info(f'[API] Found {len(submissions)} submissions for client {client.id} and module {ref_field.module_id}')
        
        if not submissions:
            current_app.logger.warning('[API] No submissions found')
            return jsonify({
                'success': False,
                'message': 'No submission found',
                'debug': {
                    'client_id': client.id,
                    'module_id': ref_field.module_id,
                    'submission_count': 0
                }
            })
        
        # Get values from all submissions for debugging
        all_values = []
        for submission in submissions:
            submission_data = submission.data or {}
            for form_field in form_fields:
                field_value = submission_data.get(form_field.field_name)
                if field_value is not None:
                    all_values.append({
                        'submission_id': submission.id,
                        'submitted_at': submission.submitted_at.isoformat(),
                        'field_name': form_field.field_name,
                        'field_label': form_field.field_label,
                        'value': field_value
                    })
        
        current_app.logger.info(f'[API] Found {len(all_values)} field values across all submissions')
        
        # Get the latest value from the most recent submission
        latest_submission = submissions[0]
        submission_data = latest_submission.data or {}
        
        # Collect all values from the latest submission
        latest_values = []
        for form_field in form_fields:
            field_value = submission_data.get(form_field.field_name)
            latest_values.append({
                'field_name': form_field.field_name,
                'field_label': form_field.field_label,
                'value': field_value
            })
        
        current_app.logger.info(f'[API] Latest submission values: {latest_values}')
        
        # For backward compatibility, return the first field's value as the main value
        main_value = latest_values[0]['value'] if latest_values else None
        
        response_data = {
            'success': True,
            'field_id': field_id,
            'reference_code': ref_field.reference_code,
            'data_type': ref_field.data_type,
            'value': main_value,
            'values': latest_values,
            'all_values': all_values,
            'debug': {
                'client_id': client.id,
                'module_id': ref_field.module_id,
                'submission_count': len(submissions),
                'latest_submission_id': latest_submission.id,
                'latest_submission_date': latest_submission.submitted_at.isoformat(),
                'form_fields_count': len(form_fields),
                'form_field_names': [f.field_name for f in form_fields]
            }
        }
        
        current_app.logger.info(f'[API] Returning response for field {field_id} ({ref_field.reference_code}): {main_value}')
        
        return jsonify(response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting system field value: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching the field value'}), 500

# Register collection schedule blueprint without additional prefix
try:
    user_bp.register_blueprint(collection_schedule_bp)
except Exception as e:
    current_app.logger.error(f"Error registering collection_schedule_bp: {str(e)}")
user_bp.register_blueprint(crb_bp)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        from utils.module_permissions import get_accessible_modules
        
        # Get all active modules that the user has read access to
        accessible_module_ids = get_accessible_modules('read')
        
        # Get all active modules
        modules = Module.query.filter(
            Module.is_active == True,
            Module.id.in_(accessible_module_ids)
        ).all()
        
        # Organize modules into a sidebar structure
        sidebar_modules = []
        for module in modules:
            # Only process root modules (no parent)
            if not module.parent_id:
                module_data = {
                    'id': module.id,
                    'name': module.name,
                    'code': module.code,
                    'icon': 'fa-folder',  # Default icon since the field doesn't exist in the model
                    'url': module.url if hasattr(module, 'url') else None,
                    'active_children': []
                }
                
                # Get active child modules that user has access to, ordered by order and then name
                children = Module.query.filter(
                    Module.is_active == True,
                    Module.parent_id == module.id,
                    Module.id.in_(accessible_module_ids)
                ).order_by(Module.order, Module.name).all()
                
                for child in children:
                    child_data = {
                        'id': child.id,
                        'name': child.name,
                        'code': child.code,
                        'icon': 'fa-file',  # Default icon since the field doesn't exist in the model
                        'url': getattr(child, 'url', None) or url_for('user.manage_module', module_id=child.id)
                    }
                    module_data['active_children'].append(child_data)
                
                # Only add modules that either have children or their own URL
                if module_data['active_children'] or module_data['url']:
                    sidebar_modules.append(module_data)
        
        # Sort sidebar modules by order (if available) and then by name
        sidebar_modules.sort(key=lambda x: (x.get('order', float('inf')), x['name']))
        
        # Get client management modules (only child modules)
        client_modules = Module.query.filter(
            and_(
                Module.code.like('CLM%'),
                Module.code != 'CLM00',  # Exclude parent module
                Module.is_active == True,
                Module.id.in_(accessible_module_ids)
            )
        ).order_by(Module.code).all()
        
        # Get loan management modules (only child modules)
        loan_modules = Module.query.filter(
            and_(
                Module.code.like('LN%'),
                ~Module.code.endswith('00'),  # Exclude parent modules
                Module.is_active == True,
                Module.id.in_(accessible_module_ids)
            )
        ).order_by(Module.code).all()
        
        # Get parent modules for organization (only if user has access)
        client_parent = Module.query.filter(
            and_(
                Module.code == 'CLM00',
                Module.is_active == True,
                Module.id.in_(accessible_module_ids)
            )
        ).first()
        
        loan_parent = Module.query.filter(
            and_(
                Module.code.like('LN%'),
                Module.code.endswith('00'),
                Module.is_active == True,
                Module.id.in_(accessible_module_ids)
            )
        ).first()
        
        return render_with_modules('user/dashboard.html',
                            sidebar_modules=sidebar_modules,
                            client_modules=client_modules,
                            loan_modules=loan_modules,
                            client_parent=client_parent,
                            loan_parent=loan_parent)
    except Exception as e:
        current_app.logger.error(f"Error in dashboard route: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('user.dashboard'))

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@user_bp.route('/dynamic_form/<int:module_id>', methods=['GET', 'POST'])
@login_required
def dynamic_form(module_id, prospect_id=None, client_id=None, mode='create'):
    # Check for query parameters
    if request.args.get('client_id') and not prospect_id:
        client_id = request.args.get('client_id')
        mode = request.args.get('mode', 'view')
        return handle_client_form(module_id, client_id, mode)
    
    """Render dynamic form for creating, viewing, or editing prospects.
    Args:
        module_id: The module ID
        prospect_id: Optional prospect ID when viewing/editing
        mode: One of 'create', 'view', or 'edit'
    """
    try:
        # Get the module and check permissions
        from utils.module_permissions import check_module_access
        from utils.table_inspector import get_model_by_module_id, get_form_fields_from_model
        from models.form_section import FormSection
        
        # Find the module by ID
        module = Module.query.get_or_404(module_id)
        
        # Check if user has write access to this module
        if not check_module_access(module.id, 'write'):
            flash('You do not have permission to submit forms for this module.', 'error')
            return redirect(url_for('user.dashboard'))
        
        # Get the model class for this module
        model_class = get_model_by_module_id(module_id)
        if not model_class:
            flash('No model found for this module. Please check the module configuration.', 'error')
            return redirect(url_for('user.dashboard'))
        
        from models.form_field import FormField
        
        # Get all sections for this specific module ID
        # Also include sections from parent modules that have this module as a submodule
        sections = FormSection.query.filter(
            (FormSection.module_id == module_id) | 
            (FormSection.submodule_id == module_id)
        ).order_by(FormSection.order.asc()).all()
        
        print(f"Found {len(sections)} sections for module {module_id}")
        
        # Get section IDs to ensure we only get fields for these sections
        section_ids = [s.id for s in sections]
        
        # Get all fields for these sections
        fields = []
        if section_ids:  # Only query if we have sections
            fields = FormField.query.filter(
                FormField.module_id == module_id,  # Must be for this module
                FormField.section_id.in_(section_ids)  # And must be in one of these sections
            ).order_by(
                FormField.section_id.asc(),
                FormField.field_order.asc()
            ).all()
            
        # If we don't have the client_type field, try to find it directly
        has_client_type = any(field.field_name == 'client_type' for field in fields)
        if not has_client_type:
            # Try to find client_type field that matches both module and section
            client_type_field = FormField.query.filter(
                FormField.field_name == 'client_type',
                FormField.module_id == module_id,
                FormField.section_id.in_(section_ids)
            ).first()
            if client_type_field:
                fields.append(client_type_field)
                print(f"Added client_type field directly: {client_type_field.id}")
        
        # Create a default section for fields without a section
        default_section_id = -1  # Use a negative ID that won't conflict with real sections
            
        print(f"Found {len(fields)} fields for module {module_id}")
        
        # Create a dictionary to hold sections and their fields
        sections_dict = {}
        
        # Process sections first
        for section in sections:
            sections_dict[section.id] = {
                'id': section.id,
                'name': section.name or f'Section {section.id}',
                'description': section.description or '',
                'order': section.order or 0,
                'fields': []
            }
        
        # Process all fields
        for field in fields:
            section_id = field.section_id
            
            # If field has no section, use our default section
            if not section_id:
                section_id = default_section_id
                
            # Create section if it doesn't exist in our dict
            if section_id not in sections_dict:
                # For our default section
                if section_id == default_section_id:
                    sections_dict[section_id] = {
                        'id': section_id,
                        'name': 'General Information',
                        'description': 'Basic information required for this form',
                        'order': 0,  # Put at the beginning
                        'fields': []
                    }
                else:
                    sections_dict[section_id] = {
                        'id': section_id,
                        'name': f'Section {section_id}',
                        'description': '',
                        'order': 999,  # Default to end
                        'fields': []
                    }
            
            # Add field to its section
            field_data = {
                'id': field.id,
                'field_name': field.field_name,
                'field_label': field.field_label or field.field_name.replace('_', ' ').title(),
                'field_placeholder': field.field_placeholder or '',
                'field_type': field.field_type or 'text',
                'is_required': bool(field.is_required),
                'field_order': field.field_order or 0,
                'section_id': section_id,
                'section_name': sections_dict[section_id]['name'] if section_id in sections_dict else 'General Information',
                'validation_rules': field.validation_rules or {},
                'default_value': getattr(field, 'default_value', None),
                'is_system': field.is_system,
                'system_reference_field_id': field.system_reference_field_id,
                'reference_field_code': field.reference_field_code,
                'is_visible': field.is_visible if hasattr(field, 'is_visible') else True,
                'client_type_restrictions': field.client_type_restrictions or []  # Add client type restrictions
            }
            
            # For client type field, get options from client_types table
            if field.field_name == 'client_type':
                from models.client_type import ClientType
                client_types = ClientType.query.filter_by(status=True).order_by(ClientType.client_name).all()
                field_data['options'] = [{
                    'value': str(ct.id),  # Use ID instead of client_code
                    'label': ct.client_name
                } for ct in client_types]
                # Set default value to Individual Client (ID: 1)
                field_data['default_value'] = '1'
                print(f"Found client_type field: {field.id}, section_id: {field.section_id}, name: {field.field_name}")
            else:
                field_data['options'] = field.options or []
            sections_dict[section_id]['fields'].append(field_data)
        
        # Convert to list and sort by section order
        sections_data = sorted(
            [s for s in sections_dict.values() if s['fields'] or s['name'] != 'General Information'],
            key=lambda x: (x['order'], x['id'])
        )
        
        # Convert the dictionary to a list and sort by section order
        sections_data = sorted(
            sections_dict.values(),
            key=lambda x: x['order']
        )
        
        # Handle form submission
        if request.method == 'POST':
            try:
                # Get form data
                form_data = request.form.to_dict()
                
                # Debug: Log form data
                current_app.logger.info(f"Form submission for module {module_id}: {module.name}")
                current_app.logger.info(f"Form data received: {form_data}")
                current_app.logger.info(f"Processing form with {len(fields)} fields")
                print(f"Form submission for module {module_id}: {module.name}")
                print(f"Processing form with {len(fields)} fields")
                
                # Debug model class information
                print(f"Model class: {model_class.__name__}")
                print(f"Model tablename: {getattr(model_class, '__tablename__', 'Unknown')}")
                
                # Get model columns
                model_columns = [column.name for column in getattr(model_class, '__table__', None).columns 
                               if hasattr(model_class, '__table__')]
                print(f"Model columns: {model_columns}")
                
                # Check if form fields match model columns
                form_fields = list(form_data.keys())
                print(f"Form fields: {form_fields}")
                
                # Find fields in form that don't exist in model
                non_matching_fields = [field for field in form_fields if field not in model_columns]
                if non_matching_fields:
                    print(f"WARNING: The following form fields don't match model columns: {non_matching_fields}")
                
                # Find required model columns that aren't in the form
                missing_columns = [col for col in model_columns if col not in form_fields 
                                 and col not in ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']]
                if missing_columns:
                    print(f"WARNING: The following model columns are missing from the form: {missing_columns}")
                
                # Create a new instance of the model
                new_record = model_class()
                print(f"Created new instance of {model_class.__name__}")
                
                # Process each field and set the corresponding attribute on the model
                for field in fields:
                    field_name = field.field_name
                    
                    # Skip fields that aren't in the form data
                    if field_name not in form_data:
                        print(f"Field '{field_name}' not found in form data, skipping")
                        continue
                    
                    # Get the value from the form
                    value = form_data[field_name]
                    original_value = value
                    
                    # Handle different field types
                    if field.field_type == 'checkbox':
                        value = True if value.lower() in ['true', 'on', 'yes', '1'] else False
                    elif field.field_type == 'number':
                        value = float(value) if value else None
                    elif field.field_type == 'date':
                        if value:
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                print(f"Invalid date format for field '{field_name}': {value}")
                                value = None
                        else:
                            value = None
                    
                    print(f"Processing field '{field_name}' (type: {field.field_type}): {original_value} → {value}")
                    
                    # Set the attribute on the model if it has that attribute
                    if hasattr(new_record, field_name):
                        setattr(new_record, field_name, value)
                        print(f"Set attribute '{field_name}' on model to {value}")
                    else:
                        print(f"Warning: Model does not have attribute '{field_name}', value not set")
                
                # Set created_by and other system fields
                if hasattr(new_record, 'created_by'):
                    new_record.created_by = current_user.id
                if hasattr(new_record, 'created_at'):
                    new_record.created_at = datetime.now()
                if hasattr(new_record, 'status'):
                    new_record.status = True
                
                # Check for required fields
                required_fields = ['first_name', 'last_name', 'mobile_number']
                missing_fields = []
                for field_name in required_fields:
                    if hasattr(new_record, field_name):
                        value = getattr(new_record, field_name)
                        if value is None or value == '':
                            missing_fields.append(field_name)
                            print(f"WARNING: Required field '{field_name}' is missing or empty")
                
                if missing_fields:
                    print(f"WARNING: The following required fields are missing: {missing_fields}")
                
                # Before saving, log the model attributes
                model_attrs = {attr: getattr(new_record, attr) for attr in dir(new_record) 
                             if not attr.startswith('_') and not callable(getattr(new_record, attr))}
                print(f"Model attributes before saving: {model_attrs}")
                
                # Save the record to the database
                print("About to add record to session")
                db.session.add(new_record)
                print("Record added to session, about to commit")
                
                try:
                    # Enable SQL echo for this transaction
                    import sqlalchemy
                    old_echo = db.engine.echo
                    db.engine.echo = True
                    
                    # Try to commit with error details
                    try:
                        db.session.commit()
                        print("Commit successful")
                    except Exception as inner_error:
                        print(f"DETAILED COMMIT ERROR: {inner_error}")
                        print(f"Error type: {type(inner_error).__name__}")
                        print(f"Error args: {inner_error.args}")
                        if hasattr(inner_error, 'orig'):
                            print(f"Original error: {inner_error.orig}")
                        db.session.rollback()
                        raise inner_error
                    
                    # Restore original echo setting
                    db.engine.echo = old_echo
                    
                    # Verify the record was actually inserted using direct SQL
                    if hasattr(new_record, 'id') and new_record.id:
                        try:
                            # Use parameterized query for safety
                            result = db.session.execute(
                                f"SELECT * FROM {model_class.__tablename__} WHERE id = :id",
                                {"id": new_record.id}
                            ).fetchone()
                            if result:
                                print(f"Record found in database with direct SQL query: {result}")
                            else:
                                print(f"VERIFICATION WARNING: ProspectRegistration record with ID {prospect.id} not found in database")
                                
                                # Try an alternative verification
                                from sqlalchemy import text
                                count_query = text(f"SELECT COUNT(*) FROM {model_class.__tablename__}")
                                count = db.session.execute(count_query).scalar()
                                print(f"Total records in table: {count}")
                        except Exception as verify_error:
                            print(f"Error verifying record: {verify_error}")
                    else:
                        print("Cannot verify record insertion - no ID available")
                except Exception as commit_error:
                    print(f"Commit failed: {commit_error}")
                    db.session.rollback()
                    raise commit_error
                
                # Get the ID of the newly created record
                record_id = getattr(new_record, 'id', None)
                
                # Show success message with record ID if available
                if record_id:
                    flash(f'Form submitted successfully! Record ID: {record_id}', 'success')
                    print(f"Successfully saved record with ID: {record_id}")
                else:
                    flash(f'Form submitted successfully!', 'success')
                    print("Successfully saved record (no ID available)")
                
                # Redirect to a success page or back to the dashboard
                return redirect(url_for('user.dashboard'))
                
            except Exception as e:
                db.session.rollback()
                error_details = traceback.format_exc()
                current_app.logger.error(f"Error saving form data: {str(e)}\n{error_details}")
                print(f"Error saving form data: {str(e)}")
                print(error_details)
                
                # Provide a more user-friendly error message
                if 'IntegrityError' in error_details:
                    flash('Error saving form: A required unique field already exists. Please check your input.', 'error')
                elif 'ValidationError' in error_details:
                    flash('Error saving form: Some fields failed validation. Please check your input.', 'error')
                else:
                    flash(f'Error saving form data: {str(e)}', 'error')
        
        # Get current date for date fields
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Render the form template with the sections and fields using the fixed template
        return render_with_modules('user/dynamic_form_fixed.html',
                            module=module,
                            sections=sections_data,
                            current_date=current_date,
                            # All other data will be loaded dynamically via AJAX if needed
                            client_types=[],
                            products=[],
                            counties=[],
                            id_types=[],
                            prospect_data={},
                            section_data={},  # Empty section data for new forms
                            mode=mode)
                            
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

@user_bp.route('/save_draft/<int:module_id>', methods=['POST'])
@login_required
def save_draft(module_id):
    """
    Save a form as a draft.
    
    Args:
        module_id (int): The ID of the module the form belongs to
        
    Returns:
        JSON response with success status and message
    """
    try:
        # Get form data
        form_data = request.form.to_dict()
        files = request.files
        
        # Get the module
        module = Module.query.get_or_404(module_id)
        
        # Create a new form submission record
        submission = FormSubmission(
            module_id=module_id,
            submitted_by=current_user.id,
            status='draft',
            form_data=json.dumps(form_data, default=str)
        )
        
        # Handle file uploads if any
        if files:
            file_data = {}
            for file_key, file in files.items():
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    file_data[file_key] = {
                        'filename': filename,
                        'path': file_path,
                        'content_type': file.content_type
                    }
            
            if file_data:
                submission.file_data = json.dumps(file_data, default=str)
        
        # Save to database
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Draft saved successfully',
            'submission_id': submission.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving draft: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to save draft: {str(e)}'
        }), 500


@user_bp.route('/submit_form/<int:module_id>', methods=['POST'])
@login_required
@csrf.exempt  # Exempt this route from automatic CSRF protection
def submit_form(module_id):
    """Handle form submission."""
    try:
        # Manually validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token:
            return jsonify({"error": "The CSRF session token is missing.", "status_code": 400}), 400
        
        # Validate the token
        from flask_wtf.csrf import validate_csrf as flask_validate_csrf
        try:
            flask_validate_csrf(csrf_token)
        except Exception:
            return jsonify({"error": "Invalid or expired CSRF token.", "status_code": 400}), 400
            
        # Get form data
        form_data = request.form.to_dict()
        
        # Get client type
        client_type_id = form_data.get('client_type')
        if not client_type_id:
            flash('Client type is required', 'error')
            return redirect(url_for('user.dynamic_form', module_id=module_id))
        
        # Get the module and check permissions
        from utils.module_permissions import check_module_access
        
        # Find the module by ID
        module = Module.query.get_or_404(module_id)
            
        # Check if user has write access to this module
        if not check_module_access(module.id, 'write'):
            flash('You do not have permission to submit forms for this module.', 'error')
            return redirect(url_for('user.dashboard'))
        
        # Create a record based on the module's table_name
        import json
        from sqlalchemy import inspect, Table, MetaData, text
        
        # Get the table name from the module
        table_name = module.table_name
        if not table_name:
            flash(f'Module {module.name} does not have an associated database table', 'error')
            return redirect(url_for('user.dynamic_form', module_id=module_id))
            
        print(f"Using database table: {table_name}")
        
        # Get table structure dynamically
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        
        if table_name not in metadata.tables:
            flash(f'Table {table_name} does not exist in the database', 'error')
            return redirect(url_for('user.dynamic_form', module_id=module_id))
            
        # Get the table object
        table = metadata.tables[table_name]
        
        # Get column information
        db_columns = {column.name: column for column in table.columns}
        print(f"Database columns: {list(db_columns.keys())}")
        
        # Get form fields defined for this module
        from models.form_field import FormField
        form_fields = FormField.query.filter_by(module_id=module_id).all()
        
        # Create a mapping of form field names to database column names and field types
        # Using the column_name field from the database for explicit mapping
        field_mapping = {}
        field_types = {}
        for field in form_fields:
            # Use the column_name field from the database
            db_field_name = field.column_name
            if not db_field_name:  # Fallback only if column_name is somehow not set
                db_field_name = field.field_name.lower().replace(' ', '_')
                print(f"Warning: Missing column_name for field '{field.field_name}', using generated value '{db_field_name}'")
            
            field_mapping[field.field_name] = db_field_name
            field_types[field.field_name] = field.field_type
            print(f"Mapping form field '{field.field_name}' ({field.field_type}) to database column '{db_field_name}'")
            
        print(f"Field mapping: {field_mapping}")
        print(f"Field types: {field_types}")
        
        # Initialize record data with required fields
        record_data = {
            'created_by': current_user.id,
            'is_active': True,
            'status': 'pending',
            'client_type': int(client_type_id) if client_type_id else None
        }
        
        # Add created_at if the column exists
        if 'created_at' in db_columns:
            record_data['created_at'] = datetime.utcnow()
        
        # Process each form field dynamically
        for field_name, value in form_data.items():
            if field_name == 'csrf_token' or field_name == 'client_type':
                continue  # Skip non-data fields
                
            # Get the corresponding database column name
            db_field_name = field_mapping.get(field_name)
            if not db_field_name:
                print(f"Warning: No mapping found for field '{field_name}', skipping")
                continue
            
            # Get the field type for proper type conversion
            field_type = field_types.get(field_name)
            
            # Check if this field exists in the database table
            if db_field_name in db_columns:
                # Process value based on field type
                if value == '':
                    # Handle empty strings
                    value = None
                elif field_type == 'select':
                    # Handle JSON fields like gender
                    try:
                        value = json.loads(value) if value else None
                    except json.JSONDecodeError:
                        value = value  # Keep as is if not valid JSON
                elif field_type == 'date':
                    # Handle date fields
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d').date() if value else None
                    except ValueError:
                        value = None
                elif field_type == 'number':
                    # Handle numeric fields
                    try:
                        value = int(value) if value else None
                    except (ValueError, TypeError):
                        value = None
                elif field_type == 'decimal':
                    # Handle decimal fields
                    try:
                        value = float(value) if value else None
                    except (ValueError, TypeError):
                        value = None
                
                # Add the field to the record data
                record_data[db_field_name] = value
                print(f"Adding field {db_field_name} ({field_type}) with value {value}")
            else:
                print(f"Warning: Field '{db_field_name}' does not exist in database table '{table_name}', skipping")
            
        # Debug: Print the final data to be saved
        print("\nFinal data to save:")
        for key, value in record_data.items():
            print(f"  {key}: {value}")
        
        # Insert data directly using the table object
        insert_stmt = table.insert().values(**record_data)
        
        try:
            # Execute the insert statement
            result = db.session.execute(insert_stmt)
            record_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
            print(f"Inserted record with ID: {record_id}")
            
            # Commit changes to database
            db.session.commit()
            
            flash(f'Form submitted successfully! Record ID: {record_id}', 'success')
            return redirect(url_for('user.manage_module', module_id=module.id))
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            print(f"Database error: {error_msg}")
            flash(f'Error saving data: {error_msg}', 'error')
            return redirect(url_for('user.dynamic_form', module_id=module_id))
                
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting form: {str(e)}', 'error')
        return redirect(url_for('user.dynamic_form', module_id=module_id))

@user_bp.route('/manage/<int:module_id>')
@login_required
def manage_module(module_id):
    """Manage submissions for a specific module."""
    try:
        # Debug logs
        print(f"Accessing manage_module with module_id: {module_id}")
        
        # Get the module and check permissions
        from utils.module_permissions import check_module_access
        module = Module.query.get_or_404(module_id)
        print(f"Found module: {module.name} (ID: {module.id}, Code: {module.code})")
        
        # Check if user has read access to this module
        if not check_module_access(module.id, 'read'):
            flash('You do not have permission to access this module.', 'error')
            return redirect(url_for('user.dashboard'))
        
        # Get all client types for filtering
        client_types = ClientType.query.filter_by(status=True).all()
        print(f"Found {len(client_types)} client types")
        
        # Get all active products
        products = Product.query.filter_by(status='Active').all()
        print(f"Found {len(products)} active products")
        
        # Get selected client type from query params
        selected_type = request.args.get('client_type', 'all')
        print(f"Selected client type: {selected_type}")
        
        # Check if this is a prospect registration module
        if module.code.startswith(('CLM01', 'CLT_M01')):  # Prospect registration modules
            from models.prospect_registration import ProspectRegistration
            
            # Start with base query
            query = ProspectRegistration.query
            
            # Apply client type filter if specified
            if selected_type != 'all':
                print(f"Filtering by client type code: {selected_type}")
                # First get the client type ID from the code
                client_type = ClientType.query.filter_by(client_code=selected_type).first()
                if client_type:
                    print(f"Found client type: {client_type.client_name} (ID: {client_type.id})")
                    # Get a sample prospect to check the client_type field format
                    sample = ProspectRegistration.query.first()
                    if sample:
                        print(f"Sample prospect client_type value: {sample.client_type} (type: {type(sample.client_type).__name__})")
                    
                    # Try filtering with both string and integer versions of the ID
                    query = query.filter(
                        db.or_(
                            ProspectRegistration.client_type == str(client_type.id),
                            ProspectRegistration.client_type == client_type.id
                        )
                    )
                else:
                    print(f"No client type found with code: {selected_type}")
                    # If no client type found, return empty result
                    query = query.filter(ProspectRegistration.id < 0)  # This will return no results
            
            # Get submissions from prospect_registration_data table
            submissions = query.order_by(ProspectRegistration.created_at.desc()).all()
            print(f"Found {len(submissions)} prospect submissions")
            
        # Check if this is a client registration module
        elif module.code.startswith(('CLM02', 'CLT_M02')):  # Client registration modules
            try:
                # Import the ClientRegistration model
                from models.client_registration import ClientRegistration
                
                # Start with base query for client registration data
                query = ClientRegistration.query
                
                # Apply client type filter if specified
                if selected_type != 'all':
                    print(f"Filtering by client type code: {selected_type}")
                    # First get the client type ID from the code
                    client_type = ClientType.query.filter_by(client_code=selected_type).first()
                    if client_type:
                        print(f"Found client type: {client_type.client_name} (ID: {client_type.id})")
                        # Try filtering with both string and integer versions of the ID
                        query = query.filter(
                            db.or_(
                                ClientRegistration.client_type == str(client_type.id),
                                ClientRegistration.client_type == client_type.id
                            )
                        )
                    else:
                        print(f"No client type found with code: {selected_type}")
                        # If no client type found, return empty result
                        query = query.filter(ClientRegistration.id < 0)  # This will return no results
                
                # Get client submissions
                submissions = query.order_by(ClientRegistration.created_at.desc()).all()
                print(f"Found {len(submissions)} client submissions from ClientRegistration model")
                
                # Import SystemReferenceValue for product and purpose lookups
                from models.system_reference_value import SystemReferenceValue
                
                # Enhance client records with additional attributes needed by the template
                for client in submissions:
                    # Add client_type_ref attribute to match the template's expectations
                    try:
                        client_type_id = int(client.client_type) if client.client_type else None
                        client.client_type_ref = ClientType.query.get(client_type_id) if client_type_id else None
                    except (ValueError, TypeError):
                        client.client_type_ref = None
                        
                    # Add product_ref attribute
                    try:
                        product_id = int(client.product) if client.product else None
                        if product_id:
                            client.product_ref = SystemReferenceValue.query.get(product_id)
                        else:
                            # Try to find by name/code if product is a string
                            if client.product and isinstance(client.product, str):
                                client.product_ref = SystemReferenceValue.query.filter(
                                    SystemReferenceValue.code == client.product
                                ).first()
                            else:
                                client.product_ref = None
                    except (ValueError, TypeError):
                        client.product_ref = None
                        
                    # Add purpose_ref attribute
                    try:
                        purpose_id = int(client.purpose) if client.purpose else None
                        if purpose_id:
                            client.purpose_ref = SystemReferenceValue.query.get(purpose_id)
                        else:
                            # Try to find by name/code if purpose is a string
                            if client.purpose and isinstance(client.purpose, str):
                                client.purpose_ref = SystemReferenceValue.query.filter(
                                    SystemReferenceValue.code == client.purpose
                                ).first()
                            else:
                                client.purpose_ref = None
                    except (ValueError, TypeError):
                        client.purpose_ref = None
            except Exception as e:
                print(f"Error loading client data: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
                submissions = []
                flash('Error loading client data: ' + str(e), 'error')
        
        # Handle other modules
        else:
            # For other modules, filter by module ID
            submissions = db.session.query(FormSubmission).\
                join(ClientType, FormSubmission.client_type_id == ClientType.id).\
                filter(FormSubmission.module_id == module_id)
            
            # Apply client type filter if specified
            if selected_type != 'all':
                submissions = submissions.filter(ClientType.client_code == selected_type)
            
            submissions = submissions.order_by(FormSubmission.created_at.desc()).all()
            print(f"Found {len(submissions)} submissions for module {module.name} (ID: {module_id})")
        
        # Debug log submission details
        print("Submission details:")
        for sub in submissions[:5]:  # Only log first 5 to avoid cluttering logs
            print(f"ID: {getattr(sub, 'id', 'N/A')}, Status: {getattr(sub, 'status', 'N/A')}, "
                  f"Converted: {getattr(sub, 'is_converted', 'N/A')}")
        if len(submissions) > 5:
            print(f"... and {len(submissions) - 5} more")
        
        # Get all active modules that the user has read access to
        accessible_module_ids = get_accessible_modules('read')
        
        # Get all active modules
        modules = Module.query.filter(
            Module.is_active == True,
            Module.id.in_(accessible_module_ids)
        ).all()
        
        # Organize modules into a sidebar structure
        sidebar_modules = []
        for mod in modules:
            # Only process root modules (no parent)
            if not mod.parent_id:
                module_data = {
                    'id': mod.id,
                    'name': mod.name,
                    'code': mod.code,
                    'icon': 'fa-folder',  # Default icon
                    'url': mod.url if hasattr(mod, 'url') else None,
                    'active_children': []
                }
                
                # Get active child modules that user has access to
                children = Module.query.filter(
                    Module.is_active == True,
                    Module.parent_id == mod.id,
                    Module.id.in_(accessible_module_ids)
                ).order_by(Module.order, Module.name).all()
                
                for child in children:
                    child_data = {
                        'id': child.id,
                        'name': child.name,
                        'code': child.code,
                        'icon': 'fa-file',  # Default icon
                        'url': getattr(child, 'url', None) or url_for('user.manage_module', module_id=child.id)
                    }
                    module_data['active_children'].append(child_data)
                
                # Only add modules that either have children or their own URL
                if module_data['active_children'] or module_data['url']:
                    sidebar_modules.append(module_data)
        
        # Sort sidebar modules by order and name
        sidebar_modules.sort(key=lambda x: (x.get('order', float('inf')), x['name']))

        return render_with_modules('user/manage_module.html',
                             module=module,
                             submissions=submissions,
                             client_types=client_types,
                             products=products,
                             selected_type=selected_type,
                             sidebar_modules=sidebar_modules)
                             
                             
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
        # Get submission and check permissions
        from utils.module_permissions import check_module_access
        submission = FormSubmission.query.get_or_404(submission_id)
        
        # Check if user has write access to this module
        if not check_module_access(submission.module_id, 'write'):
            flash('You do not have permission to delete submissions for this module.', 'error')
            return redirect(url_for('user.dashboard'))
        
        module_id = submission.module_id
        db.session.delete(submission)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting submission {submission_id}: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/view_prospect/<int:prospect_id>')
@login_required
def view_prospect(prospect_id):
    """View prospect details using dynamic form."""
    return dynamic_form(module_id=32, prospect_id=prospect_id, mode='view')


def handle_client_form(module_id, client_id, mode='view'):
    """Handle client registration form with data from the database.
    
    Args:
        module_id: The module ID (should be 33 for client registration)
        client_id: The client ID to load data from
        mode: One of 'view', 'edit', or 'register'
    """
    try:
        # Import necessary models
        from models.client_registration import ClientRegistration
        from utils.module_permissions import check_module_access
        from utils.table_inspector import get_model_by_module_id, get_form_fields_from_model
        from models.form_section import FormSection
        from models.form_field import FormField
        # Import corporate models for repeatable sections
        from models.corporate_official import CorporateOfficial
        from models.corporate_signatory import CorporateSignatory
        from models.corporate_attachment import CorporateAttachment
        from models.corporate_service import CorporateService
        
        # Find the module by ID
        module = Module.query.get_or_404(module_id)
        
        # Check if user has write access to this module
        if not check_module_access(module.id, 'write'):
            flash('You do not have permission to access this module.', 'error')
            return redirect(url_for('user.dashboard'))
        
        # Get the client data
        client = ClientRegistration.query.get_or_404(client_id)
        
        # Load repeatable section data for corporate clients
        corporate_data = {}
        if client.client_type == 2:  # Assuming client_type 2 is for corporate clients
            # Load corporate officials
            corporate_officials = CorporateOfficial.query.filter_by(client_id=client_id).all()
            corporate_data['corporate_officials'] = corporate_officials
            
            # Load corporate signatories
            corporate_signatories = CorporateSignatory.query.filter_by(client_id=client_id).all()
            corporate_data['corporate_signatories'] = corporate_signatories
            
            # Load corporate attachments
            corporate_attachments = CorporateAttachment.query.filter_by(client_id=client_id).all()
            corporate_data['corporate_attachments'] = corporate_attachments
            
            # Load corporate services
            corporate_services = CorporateService.query.filter_by(client_id=client_id).all()
            corporate_data['corporate_services'] = corporate_services
        
        # Get all sections for this specific module ID
        sections = FormSection.query.filter(
            (FormSection.module_id == module_id) | 
            (FormSection.submodule_id == module_id)
        ).order_by(FormSection.order.asc()).all()
        
        # Get section IDs
        section_ids = [s.id for s in sections]
        
        # Get all fields for these sections
        fields = []
        if section_ids:
            fields = FormField.query.filter(
                FormField.module_id == module_id,
                FormField.section_id.in_(section_ids)
            ).order_by(
                FormField.section_id.asc(),
                FormField.field_order.asc()
            ).all()
        
        # Create a dictionary to hold sections and their fields
        sections_dict = {}
        
        # Create a dictionary to hold repeatable section data
        section_data = {}
        
        # Process sections
        for section in sections:
            # Add is_repeatable and related model info to sections
            sections_dict[section.id] = {
                'id': section.id,
                'name': section.name or f'Section {section.id}',
                'description': section.description or '',
                'order': section.order or 0,
                'fields': [],
                'is_repeatable': section.is_repeatable,
                'min_entries': section.min_entries or 0,
                'max_entries': section.max_entries or 10,
                'related_model': section.related_model
            }
        
        # Process fields and populate with client data
        for field in fields:
            section_id = field.section_id or -1  # Use -1 for default section
            
            # Create section if it doesn't exist
            if section_id not in sections_dict:
                sections_dict[section_id] = {
                    'id': section_id,
                    'name': 'General Information' if section_id == -1 else f'Section {section_id}',
                    'description': 'Basic information required for this form' if section_id == -1 else '',
                    'order': 0 if section_id == -1 else 999,
                    'fields': []
                }
            
            # Get the field value from client data
            field_name = field.field_name
            field_value = getattr(client, field_name, None) if hasattr(client, field_name) else None
            
            # Create field data dictionary
            field_data = {
                'id': field.id,
                'field_name': field_name,
                'field_label': field.field_label or field_name.replace('_', ' ').title(),
                'field_placeholder': field.field_placeholder or '',
                'field_type': field.field_type or 'text',
                'is_required': bool(field.is_required),
                'field_order': field.field_order or 0,
                'section_id': section_id,
                'section_name': sections_dict[section_id]['name'],
                'validation_rules': field.validation_rules or {},
                'default_value': field_value,  # Use client data as default value
                'is_system': field.is_system,
                'system_reference_field_id': field.system_reference_field_id,
                'reference_field_code': field.reference_field_code,
                'is_visible': field.is_visible if hasattr(field, 'is_visible') else True,
                'client_type_restrictions': field.client_type_restrictions or []
            }
            
            # For client type field, get options from client_types table
            if field_name == 'client_type':
                from models.client_type import ClientType
                client_types = ClientType.query.filter_by(status=True).order_by(ClientType.client_name).all()
                field_data['options'] = [{
                    'value': str(ct.id),
                    'label': ct.client_name
                } for ct in client_types]
                # Set default value to client's client_type
                field_data['default_value'] = client.client_type
            else:
                field_data['options'] = field.options or []
            
            sections_dict[section_id]['fields'].append(field_data)
        
        # Prepare repeatable section data for the template
        for section in sections_dict.values():
            if section['is_repeatable'] and section['related_model']:
                model_name = section['related_model'].lower()
                if model_name in corporate_data and corporate_data[model_name]:
                    entries = []
                    for item in corporate_data[model_name]:
                        entry_data = {}
                        for field in section['fields']:
                            field_name = field['field_name']
                            if hasattr(item, field_name):
                                entry_data[field_name] = getattr(item, field_name)
                        entries.append(entry_data)
                    section_data[model_name] = entries
                else:
                    # Initialize with empty list if no data
                    section_data[model_name] = []
        
        # Convert to list and sort by section order
        sections_data = sorted(
            [s for s in sections_dict.values() if s['fields']],
            key=lambda x: (x['order'], x['id'])
        )
        
        # Handle form submission for register or edit mode
        if request.method == 'POST' and mode in ['register', 'edit']:
            try:
                # Process form data and update client status
                form_data = request.form.to_dict()
                
                # Process repeatable sections if client is corporate
                if client.client_type == 2:  # Corporate client
                    # Process corporate officials
                    if 'corporateofficial' in request.form:
                        # Delete existing officials
                        CorporateOfficial.query.filter_by(client_id=client_id).delete()
                        
                        # Get officials data from form
                        officials_data = {}
                        for key, value in request.form.items():
                            if key.startswith('corporateofficial['):
                                # Extract index and field name from the key
                                # Format is corporateofficial[index][field_name]
                                match = re.match(r'corporateofficial\[(\d+)\]\[([^\]]+)\]', key)
                                if match:
                                    index, field_name = match.groups()
                                    if index not in officials_data:
                                        officials_data[index] = {}
                                    officials_data[index][field_name] = value
                        
                        # Create new officials
                        for official_data in officials_data.values():
                            official = CorporateOfficial(
                                client_id=client_id,
                                created_by=current_user.id,
                                updated_by=current_user.id,
                                **official_data
                            )
                            db.session.add(official)
                    
                    # Process corporate signatories
                    if 'corporatesignatory' in request.form:
                        # Delete existing signatories
                        CorporateSignatory.query.filter_by(client_id=client_id).delete()
                        
                        # Get signatories data from form
                        signatories_data = {}
                        for key, value in request.form.items():
                            if key.startswith('corporatesignatory['):
                                match = re.match(r'corporatesignatory\[(\d+)\]\[([^\]]+)\]', key)
                                if match:
                                    index, field_name = match.groups()
                                    if index not in signatories_data:
                                        signatories_data[index] = {}
                                    signatories_data[index][field_name] = value
                        
                        # Create new signatories
                        for signatory_data in signatories_data.values():
                            signatory = CorporateSignatory(
                                client_id=client_id,
                                created_by=current_user.id,
                                updated_by=current_user.id,
                                **signatory_data
                            )
                            db.session.add(signatory)
                    
                    # Process corporate services
                    if 'corporateservice' in request.form:
                        # Delete existing services
                        CorporateService.query.filter_by(client_id=client_id).delete()
                        
                        # Get services data from form
                        services_data = {}
                        for key, value in request.form.items():
                            if key.startswith('corporateservice['):
                                match = re.match(r'corporateservice\[(\d+)\]\[([^\]]+)\]', key)
                                if match:
                                    index, field_name = match.groups()
                                    if index not in services_data:
                                        services_data[index] = {}
                                    services_data[index][field_name] = value
                        
                        # Create new services
                        for service_data in services_data.values():
                            service = CorporateService(
                                client_id=client_id,
                                created_by=current_user.id,
                                updated_by=current_user.id,
                                **service_data
                            )
                            db.session.add(service)
                    
                    # Process corporate attachments with file uploads
                    if 'corporateattachment' in request.form:
                        # Delete existing attachments
                        CorporateAttachment.query.filter_by(client_id=client_id).delete()
                        
                        # Get attachments data from form
                        attachments_data = {}
                        for key, value in request.form.items():
                            if key.startswith('corporateattachment['):
                                match = re.match(r'corporateattachment\[(\d+)\]\[([^\]]+)\]', key)
                                if match:
                                    index, field_name = match.groups()
                                    if index not in attachments_data:
                                        attachments_data[index] = {}
                                    attachments_data[index][field_name] = value
                        
                        # Process file uploads
                        for index in attachments_data.keys():
                            file_key = f'corporateattachment[{index}][attachment_file]'
                            if file_key in request.files and request.files[file_key].filename:
                                file = request.files[file_key]
                                filename = secure_filename(file.filename)
                                # Save file to uploads directory
                                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                                file.save(file_path)
                                # Store file path in attachment data
                                attachments_data[index]['file_path'] = file_path
                        
                        # Create new attachments
                        for attachment_data in attachments_data.values():
                            attachment = CorporateAttachment(
                                client_id=client_id,
                                created_by=current_user.id,
                                updated_by=current_user.id,
                                **attachment_data
                            )
                            db.session.add(attachment)
                
                # Update client status to 'registered' for register mode
                if mode == 'register':
                    client.status = 'registered'
                
                client.updated_at = datetime.now()
                client.updated_by = current_user.id
                
                # Save changes
                db.session.commit()
                
                success_message = 'Client registered successfully!' if mode == 'register' else 'Client updated successfully!'
                flash(success_message, 'success')
                return redirect(url_for('user.manage_module', module_id=module_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error processing client data: {str(e)}', 'error')
                print(f"Error processing client data: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
        
        # Render the form template with the fixed wizard template
        return render_with_modules('user/dynamic_form_fixed.html',
            module=module,
            sections=sections_data,
            section_data=section_data,  # Pass repeatable section data to template
            mode=mode,
            client=client,
            prospect_data=client,  # For compatibility with existing template
            form_title=f"{mode.title()} Client Registration",
            form_action=url_for('user.dynamic_form', module_id=module_id) + f"?client_id={client_id}&mode={mode}"
        )
    except Exception as e:
        flash(f'Error loading client form: {str(e)}', 'error')
        print(f"Error loading client form: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return redirect(url_for('user.dashboard'))


def view_prospect_legacy(submission_id):
    """View a prospect submission."""
    return dynamic_form(module_id=32, prospect_id=submission_id, mode='view')


@user_bp.route('/edit_prospect_legacy/<int:submission_id>')
@login_required
def edit_prospect_legacy(submission_id):
    """Edit prospect details using dynamic form."""
    return dynamic_form(module_id=32, prospect_id=submission_id, mode='edit')


@user_bp.route('/view_client/<int:client_id>')
@login_required
def view_client(client_id):
    """View client details using dynamic form."""
    # Directly call handle_client_form instead of dynamic_form
    return handle_client_form(33, client_id, 'view')


@user_bp.route('/edit_client/<int:client_id>')
@login_required
def edit_client(client_id):
    """Edit client details using dynamic form."""
    # Directly call handle_client_form instead of dynamic_form
    return handle_client_form(33, client_id, 'edit')


@user_bp.route('/client_registration/<int:client_id>')
@login_required
def client_registration(client_id):
    """Register client using dynamic form."""
    # Directly call handle_client_form instead of dynamic_form
    return handle_client_form(33, client_id, 'register')

@user_bp.route('/prospect/<int:prospect_id>')
@login_required
@csrf.exempt
def view_prospect_legacy(prospect_id):
    """View prospect details."""
    try:
        # Get the prospect from the dedicated table
        from models.prospect_registration import ProspectRegistration
        prospect = ProspectRegistration.query.get_or_404(prospect_id)
        
        # Get the prospect module (CLM01)
        module = Module.query.filter_by(code='CLM01').first()
        if not module:
            flash('Prospect module not found.', 'error')
            return redirect(url_for('user.dashboard'))
        
        # Get all active products
        products = Product.query.filter_by(status='Active').all()
        
        # Get all client types
        client_types = ClientType.query.filter_by(status=True).all()
        
        # Get module sections with fields
        sections = FormSection.query.filter_by(
            module_id=module.id,
            is_active=True
        ).order_by(FormSection.order).all()

        # Process fields to ensure proper client type restrictions
        individual_fields = ['first_name', 'middle_name', 'last_name', 'gender', 'id_type', 'serial_number']
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
            module_id=module.id,
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
        
        # ID types configuration
        ID_TYPES = [
            {'value': 'National ID', 'label': 'National ID'},
            {'value': 'Passport', 'label': 'Passport'},
            {'value': 'Alien ID', 'label': 'Alien ID'},
            {'value': 'Military ID', 'label': 'Military ID'}
        ]
        
        # Convert prospect to form data format
        form_data = {
            'first_name': prospect.first_name,
            'middle_name': prospect.middle_name,
            'last_name': prospect.last_name,
            'id_type': prospect.id_type,
            'id_number': prospect.id_number,
            'email': prospect.email,
            'phone': prospect.phone,
            'date_of_birth': prospect.date_of_birth.strftime('%Y-%m-%d') if prospect.date_of_birth else '',
            'gender': prospect.gender,
            'marital_status': prospect.marital_status,
            'nationality': prospect.nationality,
            'county': prospect.county,
            'sub_county': prospect.sub_county,
            'ward': prospect.ward,
            'postal_code': prospect.postal_code,
            'postal_town': prospect.postal_town,
            'estate': prospect.estate,
            'house_number': prospect.house_number,
            'occupation': prospect.occupation,
            'employer_name': prospect.employer_name,
            'employment_type': prospect.employment_type,
            'monthly_income': float(prospect.monthly_income) if prospect.monthly_income else 0,
            'other_income': float(prospect.other_income) if prospect.other_income else 0,
            'income_source': prospect.income_source,
            'next_of_kin_name': prospect.next_of_kin_name,
            'next_of_kin_phone': prospect.next_of_kin_phone,
            'next_of_kin_relationship': prospect.next_of_kin_relationship,
            'next_of_kin_id': prospect.next_of_kin_id,
            'purpose_of_visit': prospect.purpose_of_visit,
            'purpose_description': prospect.purpose_description,
            'product': prospect.product_id,
            'status': prospect.status,
            'is_converted': prospect.is_converted,
            'client_type_id': prospect.client_type_id,
            'created_at': prospect.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': prospect.updated_at.strftime('%Y-%m-%d %H:%M:%S') if prospect.updated_at else ''
        }
        
        # Get the creator's name
        creator = Staff.query.get(prospect.created_by)
        creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"
        
        # Get the current user's role for permission checks
        current_user_role = current_user.role.name if current_user.role else None
        
        # Check if the current user can approve/reject
        can_approve_reject = current_user_role in ['admin', 'manager', 'supervisor']
        
        # Check if the current user can convert to client
        can_convert = (current_user_role in ['admin', 'manager', 'officer'] and 
                      prospect.status == 'approved' and 
                      not prospect.is_converted)
        
        # Get product details if available
        product = Product.query.get(prospect.product_id) if prospect.product_id else None
        
        # Get client type
        client_type = ClientType.query.get(prospect.client_type_id)
        
        return render_with_modules('user/view_prospect.html',
                             submission=prospect,
                             form_data=form_data,
                             sections=sections,
                             products=products,
                             product=product,
                             client_types=client_types,
                             client_type=client_type,
                             id_types=ID_TYPES,
                             counties=[],
                             purpose_options=purpose_options,
                             creator_name=creator_name,
                             can_approve_reject=can_approve_reject,
                             can_convert=can_convert)
    except Exception as e:
        flash(f'Error viewing prospect: {str(e)}', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/prospect/<int:prospect_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_prospect_details(prospect_id):
    """Edit a prospect's details."""
    try:
        from models.prospect_registration import ProspectRegistration
        prospect = ProspectRegistration.query.get_or_404(prospect_id)
        
        # Get the prospect module (CLM01)
        module = Module.query.filter_by(code='CLM01').first()
        if not module:
            flash('Prospect module not found.', 'error')
            return redirect(url_for('user.dashboard'))
            
        # Check if user has permission to edit
        if not check_module_access(module.id, 'write'):
            flash('You do not have permission to edit this prospect.', 'error')
            return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
        
        # Check if prospect can be edited
        if prospect.status == 'approved' and prospect.is_converted:
            flash('This prospect has already been converted to a client and cannot be edited.', 'error')
            return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
        
        # Get all active products
        products = Product.query.filter_by(status='Active').all()
        
        # Get all client types
        client_types = ClientType.query.filter_by(status=True).all()
        
        # Get module sections with fields
        sections = FormSection.query.filter_by(
            module_id=module.id,
            is_active=True
        ).order_by(FormSection.order).all()

        # Process fields to ensure proper client type restrictions
        individual_fields = ['first_name', 'middle_name', 'last_name', 'gender', 'id_type', 'serial_number']
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
            module_id=module.id,
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
        
        # ID types configuration
        ID_TYPES = [
            {'value': 'National ID', 'label': 'National ID'},
            {'value': 'Passport', 'label': 'Passport'},
            {'value': 'Alien ID', 'label': 'Alien ID'},
            {'value': 'Military ID', 'label': 'Military ID'}
        ]
        
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
            try:
                # Update prospect fields from form data
                prospect.first_name = request.form.get('first_name', '').strip()
                prospect.middle_name = request.form.get('middle_name', '').strip()
                prospect.last_name = request.form.get('last_name', '').strip()
                prospect.id_type = request.form.get('id_type', '').strip()
                prospect.id_number = request.form.get('id_number', '').strip()
                prospect.email = request.form.get('email', '').strip()
                prospect.phone = request.form.get('phone', '').strip()
                
                # Handle date fields
                dob = request.form.get('date_of_birth')
                if dob:
                    try:
                        prospect.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        prospect.date_of_birth = None
                
                prospect.gender = request.form.get('gender', '').strip()
                prospect.marital_status = request.form.get('marital_status', '').strip()
                prospect.nationality = request.form.get('nationality', '').strip()
                
                # Address information
                prospect.county = request.form.get('county', '').strip()
                prospect.sub_county = request.form.get('sub_county', '').strip()
                prospect.ward = request.form.get('ward', '').strip()
                prospect.postal_code = request.form.get('postal_code', '').strip()
                prospect.postal_town = request.form.get('postal_town', '').strip()
                prospect.estate = request.form.get('estate', '').strip()
                prospect.house_number = request.form.get('house_number', '').strip()
                
                # Employment information
                prospect.occupation = request.form.get('occupation', '').strip()
                prospect.employer_name = request.form.get('employer_name', '').strip()
                prospect.employment_type = request.form.get('employment_type', '').strip()
                
                # Income information
                try:
                    prospect.monthly_income = float(request.form.get('monthly_income', 0))
                except (ValueError, TypeError):
                    prospect.monthly_income = 0
                    
                try:
                    prospect.other_income = float(request.form.get('other_income', 0))
                except (ValueError, TypeError):
                    prospect.other_income = 0
                    
                prospect.income_source = request.form.get('income_source', '').strip()
                
                # Next of kin information
                prospect.next_of_kin_name = request.form.get('next_of_kin_name', '').strip()
                prospect.next_of_kin_phone = request.form.get('next_of_kin_phone', '').strip()
                prospect.next_of_kin_relationship = request.form.get('next_of_kin_relationship', '').strip()
                prospect.next_of_kin_id = request.form.get('next_of_kin_id', '').strip()
                
                # Purpose of visit
                prospect.purpose_of_visit = request.form.get('purpose_of_visit', '').strip()
                prospect.purpose_description = request.form.get('purpose_description', '').strip()
                
                # Product and client type
                try:
                    product_id = int(request.form.get('product_id', 0))
                    if product_id > 0:
                        prospect.product_id = product_id
                except (ValueError, TypeError):
                    pass
                    
                try:
                    client_type_id = int(request.form.get('client_type_id', 0))
                    if client_type_id > 0:
                        prospect.client_type_id = client_type_id
                except (ValueError, TypeError):
                    pass
                
                # Handle file uploads if any
                if 'id_copy' in request.files and request.files['id_copy'].filename != '':
                    file = request.files['id_copy']
                    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'prospects', str(prospect.id))
                        os.makedirs(file_path, exist_ok=True)
                        file.save(os.path.join(file_path, filename))
                        prospect.id_copy_path = f"prospects/{prospect.id}/{filename}"
                
                # Update timestamps
                prospect.updated_at = datetime.utcnow()
                prospect.updated_by = current_user.id
                
                db.session.commit()
                
                flash('Prospect details updated successfully!', 'success')
                return redirect(url_for('user.view_prospect', prospect_id=prospect.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating prospect: {str(e)}', 'error')
                current_app.logger.error(f"Error updating prospect {prospect_id}: {str(e)}\n{traceback.format_exc()}")
        
        # Convert prospect to form data format for the template
        form_data = {
            'first_name': prospect.first_name,
            'middle_name': prospect.middle_name,
            'last_name': prospect.last_name,
            'id_type': prospect.id_type,
            'id_number': prospect.id_number,
            'email': prospect.email,
            'phone': prospect.phone,
            'date_of_birth': prospect.date_of_birth.strftime('%Y-%m-%d') if prospect.date_of_birth else '',
            'gender': prospect.gender,
            'marital_status': prospect.marital_status,
            'nationality': prospect.nationality,
            'county': prospect.county,
            'sub_county': prospect.sub_county,
            'ward': prospect.ward,
            'postal_code': prospect.postal_code,
            'postal_town': prospect.postal_town,
            'estate': prospect.estate,
            'house_number': prospect.house_number,
            'occupation': prospect.occupation,
            'employer_name': prospect.employer_name,
            'employment_type': prospect.employment_type,
            'monthly_income': float(prospect.monthly_income) if prospect.monthly_income else 0,
            'other_income': float(prospect.other_income) if prospect.other_income else 0,
            'income_source': prospect.income_source,
            'next_of_kin_name': prospect.next_of_kin_name,
            'next_of_kin_phone': prospect.next_of_kin_phone,
            'next_of_kin_relationship': prospect.next_of_kin_relationship,
            'next_of_kin_id': prospect.next_of_kin_id,
            'purpose_of_visit': prospect.purpose_of_visit,
            'purpose_description': prospect.purpose_description,
            'product_id': prospect.product_id,
            'client_type_id': prospect.client_type_id,
            'status': prospect.status
        }
        
        # Get the current user's role for permission checks
        current_user_role = current_user.role.name if current_user.role else None
        
        # Check if the current user can approve/reject
        can_approve_reject = current_user_role in ['admin', 'manager', 'supervisor']
        
        # Check if the current user can convert to client
        can_convert = (current_user_role in ['admin', 'manager', 'officer'] and 
                      prospect.status == 'approved' and 
                      not prospect.is_converted)
        
        # Get the creator's name
        creator = Staff.query.get(prospect.created_by)
        creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"
        
        # Get product details if available
        product = Product.query.get(prospect.product_id) if prospect.product_id else None
        
        # Get client type
        client_type = ClientType.query.get(prospect.client_type_id)
        
        return render_with_modules('user/edit_prospect.html',
                             prospect=prospect,
                             form_data=form_data,
                             sections=sections,
                             products=products,
                             product=product,
                             client_types=client_types,
                             client_type=client_type,
                             id_types=ID_TYPES,
                             postal_towns=POSTAL_TOWNS,
                             purpose_options=purpose_options,
                             creator_name=creator_name,
                             can_approve_reject=can_approve_reject,
                             can_convert=can_convert)
                             
    except Exception as e:
        db.session.rollback()
        flash(f'Error loading prospect edit form: {str(e)}', 'error')
        current_app.logger.error(f"Error in edit_prospect: {str(e)}\n{traceback.format_exc()}")
        return redirect(url_for('user.dashboard'))

@user_bp.route('/prospect/<int:prospect_id>/delete')
@login_required
def delete_prospect(prospect_id):
    """Delete a prospect."""
    try:
        from models.prospect_registration import ProspectRegistration
        prospect = ProspectRegistration.query.get_or_404(prospect_id)
        
        # Check if user has permission to delete
        if not check_module_access(1, 'delete'):  # Assuming 1 is the ID for prospect module
            flash('You do not have permission to delete this prospect.', 'error')
            return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
        
        # Check if prospect can be deleted
        if prospect.status == 'approved' and prospect.is_converted:
            flash('This prospect has already been converted to a client and cannot be deleted.', 'error')
            return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
        
        # Delete the prospect
        db.session.delete(prospect)
        db.session.commit()
        
        flash('Prospect deleted successfully', 'success')
        return redirect(url_for('user.manage_module', module_code='CLM01'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting prospect: {str(e)}', 'error')
        current_app.logger.error(f"Error deleting prospect {prospect_id}: {str(e)}\n{traceback.format_exc()}")
        return redirect(url_for('user.dashboard'))

@user_bp.route('/convert_to_client/<int:prospect_id>', methods=['GET', 'POST'])
@login_required
def convert_to_client(prospect_id):
    """Convert a prospect to a client - supports both regular form submission and GET requests"""
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # For AJAX requests, redirect to the AJAX-specific endpoint
    if is_ajax and request.method == 'POST':
        return ajax_convert_to_client(prospect_id)
        
    # Continue with regular (non-AJAX) processing
    
@user_bp.route('/api/convert_to_client/<int:prospect_id>', methods=['POST'])
@login_required
def ajax_convert_to_client(prospect_id):
    """AJAX-specific endpoint for prospect-to-client conversion
    This function will only handle AJAX requests and always return JSON"""
    try:
        current_app.logger.info(f"=== AJAX convert_to_client STARTED for prospect_id={prospect_id} ===")
        
        # Import required models
        from models.prospect_registration import ProspectRegistration
        from models.module import Module
        
        # Get the prospect
        prospect = ProspectRegistration.query.get(prospect_id)
        if not prospect:
            response = jsonify({
                'success': False,
                'message': f'Prospect with ID {prospect_id} not found'
            })
            response.headers['Content-Type'] = 'application/json'
            return response, 404
            
        # Check user permissions
        has_permission = False
        for role in ['admin', 'manager', 'officer']:
            if current_user.has_role(role):
                has_permission = True
                break
                
        if not has_permission:
            response = jsonify({
                'success': False,
                'message': 'You do not have permission to convert prospects to clients.'
            })
            response.headers['Content-Type'] = 'application/json'
            return response, 403
            
        # Check if prospect is approved
        status = getattr(prospect, 'status', '').strip().lower()
        if status not in ['pending', 'approved']:
            response = jsonify({
                'success': False,
                'message': 'Only pending or approved prospects can be converted to clients.'
            })
            response.headers['Content-Type'] = 'application/json'
            return response, 400
            
        # Get required modules
        client_module = Module.query.filter_by(code='client_registration').first()
        if not client_module:
            client_module = Module.query.filter(Module.name.ilike('%client%registration%')).first()
            
        prospect_module = Module.query.filter_by(code='prospect_registration').first()
        if not prospect_module:
            prospect_module = Module.query.filter(Module.name.ilike('%prospect%registration%')).first()
            
        # Check if modules exist
        if not client_module:
            response = jsonify({
                'success': False,
                'message': 'Client registration module not found.',
                'client_id': None
            })
            response.headers['Content-Type'] = 'application/json'
            return response, 404
            
        if not prospect_module:
            response = jsonify({
                'success': False,
                'message': 'Prospect registration module not found.',
                'client_id': None
            })
            response.headers['Content-Type'] = 'application/json'
            return response, 404
            
        # Use default table names if not specified in the module
        if not client_module.table_name:
            current_app.logger.warning(f"Client module (ID: {client_module.id}) has no table_name, using default")
            client_module.table_name = 'client_registration_data'
            
        if not prospect_module.table_name:
            current_app.logger.warning(f"Prospect module (ID: {prospect_module.id}) has no table_name, using default")
            prospect_module.table_name = 'prospect_registration_data'
            
        # Log module information
        current_app.logger.info(f"Client module: ID={client_module.id}, Name={client_module.name}, Table={client_module.table_name}")
        current_app.logger.info(f"Prospect module: ID={prospect_module.id}, Name={prospect_module.name}, Table={prospect_module.table_name}")
            
        # Now perform the actual conversion
        current_app.logger.info("=== STARTING ACTUAL CONVERSION PROCESS ===")
        
        try:
            # Get the branch ID from the form data or use a default
            form_data = request.form.to_dict()
            branch_id = form_data.get('branch_id')
            if branch_id is None and hasattr(current_user, 'branch_id'):
                branch_id = current_user.branch_id
            if branch_id is None:
                branch_id = 1  # Default branch ID
            current_app.logger.info(f"Using branch_id: {branch_id}")
            
            # Get client table information using SQLAlchemy Core
            from sqlalchemy import inspect, Table, MetaData, Column, Integer, String, Boolean, DateTime, Float
            from sqlalchemy.sql import text
            
            # Get the client table columns from the database
            query = text(f"SHOW COLUMNS FROM {client_module.table_name}")
            columns_result = db.session.execute(query).fetchall()
            client_db_columns = [col[0] for col in columns_result]
            current_app.logger.info(f"Client table columns from DB: {client_db_columns[:10]}...")
            
            # Create a metadata object
            metadata = MetaData()
            
            # Define the table with autoload to get all columns
            client_table = Table(client_module.table_name, metadata, autoload_with=db.engine)
            
            # Get form fields for both modules
            from models.form_field import FormField
            client_fields = FormField.query.filter_by(module_id=client_module.id).all()
            prospect_fields = FormField.query.filter_by(module_id=prospect_module.id).all()
            
            # Create field mappings
            client_field_mapping = {}
            client_field_types = {}
            for field in client_fields:
                # Ensure we have a valid column name (not None)
                if field.column_name:
                    db_field_name = field.column_name
                else:
                    # Create a safe column name from the field name
                    db_field_name = field.field_name.lower().replace(' ', '_')
                    current_app.logger.info(f"Created column name '{db_field_name}' for field '{field.field_name}'")
                
                # Skip fields with empty column names
                if not db_field_name or db_field_name.strip() == '':
                    current_app.logger.warning(f"Skipping field '{field.field_name}' with empty column name")
                    continue
                    
                client_field_mapping[field.field_name] = db_field_name
                client_field_types[field.field_name] = field.field_type
            
            prospect_field_mapping = {}
            for field in prospect_fields:
                # Ensure we have a valid column name (not None)
                if field.column_name:
                    db_field_name = field.column_name
                else:
                    # Create a safe column name from the field name
                    db_field_name = field.field_name.lower().replace(' ', '_')
                
                # Skip fields with empty column names
                if not db_field_name or db_field_name.strip() == '':
                    continue
                    
                prospect_field_mapping[field.field_name] = db_field_name
            
            # Initialize record data with required fields
            from datetime import datetime
            record_data = {
                'created_by': current_user.id,
                'updated_by': current_user.id,
                'is_active': True,
                'status': 'Active',
                'branch_id': int(branch_id) if branch_id is not None else 1,
                'client_type': getattr(prospect, 'client_type', 'Individual'),
                'organization_id': current_user.organization_id if hasattr(current_user, 'organization_id') else None
            }
            
            # Add timestamps if the columns exist
            if 'created_at' in client_db_columns:
                record_data['created_at'] = datetime.utcnow()
            if 'updated_at' in client_db_columns:
                record_data['updated_at'] = datetime.utcnow()
            
            # Convert prospect data to a dictionary
            prospect_dict = {}
            for column in inspect(ProspectRegistration).columns:
                value = getattr(prospect, column.name)
                prospect_dict[column.name] = value
            
            # Map prospect fields to client fields
            import json
            for client_field_name, client_db_field in client_field_mapping.items():
                # Skip fields that don't exist in the client table
                if client_db_field not in client_db_columns:
                    continue
                
                # First check if the field exists in the form data
                if client_field_name in form_data:
                    value = form_data[client_field_name]
                else:
                    # Try to find a matching field in the prospect data
                    prospect_db_field = prospect_field_mapping.get(client_field_name)
                    
                    if prospect_db_field and prospect_db_field in prospect_dict:
                        value = prospect_dict[prospect_db_field]
                    elif client_db_field in prospect_dict:
                        # Try direct column name match
                        value = prospect_dict[client_db_field]
                    else:
                        # No match found, skip this field
                        continue
                
                # Process value based on field type
                field_type = client_field_types.get(client_field_name)
                
                if value == '':
                    value = None
                elif field_type == 'select':
                    try:
                        value = json.loads(value) if isinstance(value, str) else value
                    except (json.JSONDecodeError, TypeError):
                        pass  # Keep as is if not valid JSON
                elif field_type == 'date':
                    if isinstance(value, str):
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            value = None
                elif field_type == 'number':
                    try:
                        value = int(value) if value else None
                    except (ValueError, TypeError):
                        value = None
                elif field_type == 'decimal':
                    try:
                        value = float(value) if value else None
                    except (ValueError, TypeError):
                        value = None
                
                # Add the field to the record data if the key is valid
                if client_db_field and client_db_field.strip() != '':
                    record_data[client_db_field] = value
                else:
                    current_app.logger.warning(f"Skipping field with invalid column name: {client_field_name}")
            
            # Log the record data before insertion
            current_app.logger.info(f"Prepared {len(record_data)} fields for insertion")
            
            # Validate record data to ensure no None keys
            validated_data = {}
            for key, value in record_data.items():
                if key is not None and key.strip() != '':
                    validated_data[key] = value
                else:
                    current_app.logger.warning(f"Removing invalid key: {key}")
            
            # Log all keys for debugging
            current_app.logger.info(f"Record data keys: {list(validated_data.keys())}")
            
            # Use proper SQLAlchemy Core insert
            current_app.logger.info("Using SQLAlchemy Core insert...")
            
            # Create the insert statement using the insert() construct
            from sqlalchemy import insert
            
            # Log the validated data keys
            current_app.logger.info(f"Validated data keys: {list(validated_data.keys())}")
            
            # Create an insert statement with the validated data
            insert_stmt = insert(client_table).values(**validated_data)
            
            # Execute the insert
            try:
                current_app.logger.info("Executing SQLAlchemy insert...")
                result = db.session.execute(insert_stmt)
                db.session.flush()
                
                # Get the last inserted ID
                client_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
                if not client_id:
                    # Fallback to get the last insert ID
                    id_query = text("SELECT LAST_INSERT_ID()")
                    client_id = db.session.execute(id_query).scalar()
                    
                current_app.logger.info(f"New client ID: {client_id}")
            except Exception as sql_error:
                current_app.logger.error(f"SQLAlchemy Error: {str(sql_error)}")
                # Log the data being inserted (excluding sensitive fields)
                safe_data = {k: v for k, v in validated_data.items() if k not in ['password', 'pin']}
                current_app.logger.error(f"Data: {safe_data}")
                raise
            
            # Update prospect with client reference and change status
            current_app.logger.info(f"Updating prospect {prospect.id} with client_id {client_id}")
            prospect.client_id = client_id
            
            # Update status from pending to converted
            if hasattr(prospect, 'status'):
                old_status = prospect.status
                prospect.status = 'Converted'
                current_app.logger.info(f"Updated prospect status from '{old_status}' to 'Converted'")
            
            # Add conversion timestamp and user if those fields exist
            if hasattr(prospect, 'converted_at'):
                prospect.converted_at = datetime.utcnow()
            if hasattr(prospect, 'converted_by'):
                prospect.converted_by = current_user.id
            
            # Commit all changes in a transaction
            current_app.logger.info("Committing transaction...")
            db.session.commit()
            current_app.logger.info("Transaction committed successfully")
            
            # Return success response
            response = jsonify({
                'success': True,
                'message': 'Prospect successfully converted to client.',
                'client_id': client_id,
                'prospect_id': prospect_id,
                'prospect_name': f"{getattr(prospect, 'first_name', '')} {getattr(prospect, 'last_name', '')}"
            })
            response.headers['Content-Type'] = 'application/json'
            return response
            
        except Exception as e:
            db.session.rollback()
            import traceback
            current_app.logger.error(f"Error in conversion process: {str(e)}\n{traceback.format_exc()}")
            
            response = jsonify({
                'success': False,
                'message': f'Error during conversion: {str(e)}'
            })
            response.headers['Content-Type'] = 'application/json'
            return response, 500
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"AJAX conversion error: {str(e)}\n{traceback.format_exc()}")
        
        response = jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })
        response.headers['Content-Type'] = 'application/json'
        return response, 500
    try:
        # Log the start of the function with detailed request info
        current_app.logger.info("\n" + "="*80)
        current_app.logger.info(f"=== convert_to_client STARTED - prospect_id: {prospect_id} ===")
        current_app.logger.info(f"Request URL: {request.url}")
        current_app.logger.info(f"Request method: {request.method}")
        current_app.logger.info(f"Request path: {request.path}")
        current_app.logger.info(f"Request endpoint: {request.endpoint}")
        current_app.logger.info(f"Request view_args: {request.view_args}")
        current_app.logger.info(f"Request headers: {dict(request.headers)}")
        current_app.logger.info(f"Request data: {request.data}")
        
        # Log current user info
        current_app.logger.info(f"Current user: {current_user.id if hasattr(current_user, 'id') else 'Anonymous'}")
        if hasattr(current_user, 'role'):
            current_app.logger.info(f"User role: {current_user.role.name if current_user.role else 'No role'}")
        
        # Determine if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        current_app.logger.info(f"Is AJAX request: {is_ajax}")
        
        # Log request details
        current_app.logger.info(f"Request Content-Type: {request.content_type}")
        current_app.logger.info(f"Request method: {request.method}")
        current_app.logger.info(f"Request URL: {request.url}")
        current_app.logger.info(f"Request headers: {dict(request.headers)}")
        
        # Log form data if present
        if request.form:
            current_app.logger.info(f"Form data: {dict(request.form)}")
        
        # Log JSON data if present
        if request.is_json:
            try:
                json_data = request.get_json()
                current_app.logger.info(f"JSON data: {json_data}")
            except Exception as e:
                current_app.logger.warning(f"Failed to parse JSON data: {str(e)}")
                
        # Log request args
        current_app.logger.info(f"Request args: {dict(request.args)}")
        
        # Verify CSRF token is present
        csrf_token = request.form.get('csrf_token')
        current_app.logger.info(f"CSRF token in form: {'present' if csrf_token else 'missing'}")
        
        # Log all registered routes for debugging
        current_app.logger.info("\n=== REGISTERED ROUTES ===")
        for rule in current_app.url_map.iter_rules():
            if 'convert_to_client' in rule.endpoint:
                current_app.logger.info(f"FOUND ROUTE: {rule.endpoint} -> {rule.rule} (methods: {rule.methods})")
        current_app.logger.info("="*80 + "\n")
        
        # Import inside the function to avoid circular imports
        from models.prospect_registration import ProspectRegistration
        from models.module import Module
        from sqlalchemy import text
        
        # Log before querying the prospect
        current_app.logger.info(f"Attempting to find prospect with ID: {prospect_id}")
        
        # Get the prospect with explicit error handling
        try:
            current_app.logger.info(f"Attempting database query: ProspectRegistration.query.get({prospect_id})")
            prospect = ProspectRegistration.query.get(prospect_id)
            current_app.logger.info(f"Query result: prospect={'exists' if prospect else 'not found'}")
            
            if not prospect:
                error_msg = f"Prospect with ID {prospect_id} not found"
                current_app.logger.error(error_msg)
                if is_ajax:
                    response = jsonify({'success': False, 'message': error_msg})
                    response.headers['Content-Type'] = 'application/json'
                    return response, 404
                flash(error_msg, 'error')
                return redirect(url_for('user.dashboard'))
                
            current_app.logger.info(f"Found prospect: ID={prospect.id}")
            current_app.logger.info(f"Prospect name: {getattr(prospect, 'first_name', 'N/A')} {getattr(prospect, 'last_name', '')}")
            current_app.logger.info(f"Prospect status: {getattr(prospect, 'status', 'N/A')}")
            
        except Exception as e:
            error_msg = f"Error querying prospect: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            if is_ajax:
                response = jsonify({'success': False, 'message': error_msg})
                response.headers['Content-Type'] = 'application/json'
                return response, 500
            flash(error_msg, 'error')
            return redirect(url_for('user.dashboard'))
        
        # Check if user has permission to convert
        current_user_role = current_user.role.name.lower() if hasattr(current_user, 'role') and current_user.role else None
        if current_user_role not in ['admin', 'manager', 'officer']:
            error_msg = 'You do not have permission to convert prospects to clients.'
            current_app.logger.warning(f"Permission denied for user {current_user.id}: {error_msg}")
            if is_ajax:
                response = jsonify({'success': False, 'message': error_msg})
                response.headers['Content-Type'] = 'application/json'
                return response, 403
            flash(error_msg, 'error')
            return redirect(url_for('user.dashboard'))
        
        # Check if prospect has valid status (pending or approved)
        current_app.logger.info(f"Prospect status: {prospect.status}")
        # Allow both 'pending' and 'approved' statuses
        valid_statuses = ['pending', 'approved']
        if not prospect.status or prospect.status.lower().strip() not in valid_statuses:
            error_msg = 'Only pending or approved prospects can be converted to clients.'
            current_app.logger.info(f"Conversion rejected: {error_msg}")
            if is_ajax:
                response = jsonify({
                    'success': False,
                    'message': error_msg
                })
                response.headers['Content-Type'] = 'application/json'
                return response, 400
            flash(error_msg, 'error')
            return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
            
        # Ensure proper content type for AJAX responses
        if is_ajax:
            current_app.logger.info("Setting response content type to application/json for AJAX request")
        
        # Check if client_id is already set (indicating previous conversion)
        if hasattr(prospect, 'client_id') and prospect.client_id:
            if is_ajax:
                response = jsonify({
                    'success': False,
                    'message': 'This prospect has already been converted to a client.'
                })
                response.headers['Content-Type'] = 'application/json'
                return response, 400
            flash('This prospect has already been converted to a client.', 'error')
            return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
        
        # Find both required modules using their codes (more reliable than IDs)
        current_app.logger.info("Attempting to fetch required modules by code...")
        
        # Get modules by code instead of ID
        client_module = Module.query.filter_by(code='client_registration').first()
        current_app.logger.info(f"Client module (code=client_registration): {'found' if client_module else 'not found'}")
        
        prospect_module = Module.query.filter_by(code='prospect_registration').first()
        current_app.logger.info(f"Prospect module (code=prospect_registration): {'found' if prospect_module else 'not found'}")
        
        # If modules aren't found by code, try to find by name as fallback
        if not client_module:
            client_module = Module.query.filter(Module.name.ilike('%client%registration%')).first()
            current_app.logger.info(f"Fallback client module search by name: {'found' if client_module else 'still not found'}")
            
        if not prospect_module:
            prospect_module = Module.query.filter(Module.name.ilike('%prospect%registration%')).first()
            current_app.logger.info(f"Fallback prospect module search by name: {'found' if prospect_module else 'still not found'}")
        
        # Validate modules with detailed error messages
        if not client_module:
            error_msg = 'Client registration module not found in the system. Please contact the administrator to set up the required modules.'
            current_app.logger.error(error_msg)
            if is_ajax:
                response = jsonify({
                    'success': False,
                    'message': error_msg,
                    'error_type': 'missing_module'
                })
                response.headers['Content-Type'] = 'application/json'
                return response, 404
            flash(error_msg, 'error')
            return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
            
        if not prospect_module:
            error_msg = 'Prospect registration module not found in the system. Please contact the administrator to set up the required modules.'
            current_app.logger.error(error_msg)
            if is_ajax:
                response = jsonify({
                    'success': False,
                    'message': error_msg,
                    'error_type': 'missing_module'
                })
                response.headers['Content-Type'] = 'application/json'
                return response, 404
            flash(error_msg, 'error')
            return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
            
        # Log module IDs for reference
        current_app.logger.info(f"Using client_module.id={client_module.id} and prospect_module.id={prospect_module.id}")
        
        # Check if a client with the same ID number already exists
        try:
            check_query = text(f"SELECT id FROM {client_module.table_name} WHERE identification_number = :id_number")
            existing_client = db.session.execute(check_query, {"id_number": prospect.identification_number}).fetchone()
            
            if existing_client:
                if is_ajax:
                    response = jsonify({
                        'success': False,
                        'message': f'A client with ID number {prospect.identification_number} already exists.'
                    })
                    response.headers['Content-Type'] = 'application/json'
                    return response, 400
                flash(f'A client with ID number {prospect.identification_number} already exists.', 'error')
                return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
        except Exception as e:
            current_app.logger.error(f"Error checking for existing client: {str(e)}")
            # Continue even if this check fails
            
        if request.method == 'GET':
            # Get all active branches for the form
            branches = Branch.query.filter_by(status=True).all()
            return render_template('user/convert_to_client.html', prospect=prospect, branches=branches)
        
        # Handle POST request
        elif request.method == 'POST':
            try:
                # For AJAX requests, we don't need form data
                # Just proceed with the conversion using the prospect data
                
                # Get branch ID from form if provided (for non-AJAX requests)
                branch_id = request.form.get('branch_id') if not is_ajax else None
                
                # For AJAX requests, we don't require branch selection
                if not branch_id and not is_ajax:
                    flash('Branch is required', 'error')
                    return redirect(url_for('user.convert_to_client', prospect_id=prospect_id))
                
                # Dynamically reflect the client registration table
                from sqlalchemy import inspect, Table, MetaData
                
                # Get the table name from the client module
                client_table_name = client_module.table_name
                if not client_table_name:
                    flash(f'Client module does not have an associated database table', 'error')
                    return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
                
                # Get table structure dynamically
                metadata = MetaData()
                metadata.reflect(bind=db.engine)
                
                if client_table_name not in metadata.tables:
                    flash(f'Table {client_table_name} does not exist in the database', 'error')
                    return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
                
                # Get the table object
                client_table = metadata.tables[client_table_name]
                
                # Get column information
                client_db_columns = {column.name: column for column in client_table.columns}
                
                # Get form fields defined for both modules
                from models.form_field import FormField
                client_fields = FormField.query.filter_by(module_id=client_module.id).all()
                prospect_fields = FormField.query.filter_by(module_id=prospect_module.id).all()
                
                # Create mappings of field names to column names
                client_field_mapping = {}
                client_field_types = {}
                for field in client_fields:
                    db_field_name = field.column_name
                    if not db_field_name:
                        db_field_name = field.field_name.lower().replace(' ', '_')
                    
                    client_field_mapping[field.field_name] = db_field_name
                    client_field_types[field.field_name] = field.field_type
                
                prospect_field_mapping = {}
                for field in prospect_fields:
                    db_field_name = field.column_name
                    if not db_field_name:
                        db_field_name = field.field_name.lower().replace(' ', '_')
                    
                    prospect_field_mapping[field.field_name] = db_field_name
                
                # Create a reverse mapping from prospect db columns to field names
                prospect_reverse_mapping = {v: k for k, v in prospect_field_mapping.items()}
                
                # Initialize record data with required fields
                import json
                record_data = {
                    'created_by': current_user.id,
                    'updated_by': current_user.id,
                    'is_active': True,
                    'status': 'Active',
                    'branch_id': int(branch_id),
                    'client_type': prospect.client_type,
                    'organization_id': current_user.organization_id if hasattr(current_user, 'organization_id') else None
                }
                
                # Add created_at if the column exists
                if 'created_at' in client_db_columns:
                    record_data['created_at'] = datetime.utcnow()
                if 'updated_at' in client_db_columns:
                    record_data['updated_at'] = datetime.utcnow()
                
                # Convert prospect data to a dictionary
                prospect_dict = {}
                for column in inspect(ProspectRegistration).columns:
                    value = getattr(prospect, column.name)
                    prospect_dict[column.name] = value
                
                # Map prospect fields to client fields based on field name matching
                for client_field_name, client_db_field in client_field_mapping.items():
                    # Skip fields that don't exist in the client table
                    if client_db_field not in client_db_columns:
                        continue
                    
                    # First check if the field exists in the form data (user input during conversion)
                    if client_field_name in form_data:
                        value = form_data[client_field_name]
                    else:
                        # Try to find a matching field in the prospect data
                        # First check by exact field name match
                        prospect_db_field = prospect_field_mapping.get(client_field_name)
                        
                        if prospect_db_field and prospect_db_field in prospect_dict:
                            value = prospect_dict[prospect_db_field]
                        elif client_db_field in prospect_dict:
                            # Try direct column name match
                            value = prospect_dict[client_db_field]
                        else:
                            # No match found, skip this field
                            continue
                    
                    # Process value based on field type
                    field_type = client_field_types.get(client_field_name)
                    
                    if value == '':
                        # Handle empty strings
                        value = None
                    elif field_type == 'select':
                        # Handle JSON fields
                        try:
                            value = json.loads(value) if isinstance(value, str) else value
                        except (json.JSONDecodeError, TypeError):
                            pass  # Keep as is if not valid JSON
                    elif field_type == 'date':
                        # Handle date fields
                        if isinstance(value, str):
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                value = None
                    elif field_type == 'number':
                        # Handle numeric fields
                        try:
                            value = int(value) if value else None
                        except (ValueError, TypeError):
                            value = None
                    elif field_type == 'decimal':
                        # Handle decimal fields
                        try:
                            value = float(value) if value else None
                        except (ValueError, TypeError):
                            value = None
                    
                    # Add the field to the record data
                    record_data[client_db_field] = value
                
                # Log the record data before insertion
                current_app.logger.info("=== DATABASE INSERT OPERATION ===")
                current_app.logger.info(f"Inserting into table: {client_module.table_name}")
                current_app.logger.info(f"Record data keys: {list(record_data.keys())}")
                
                # Log a few key fields for debugging
                safe_fields = ['first_name', 'last_name', 'email', 'phone_number', 'client_type', 'branch_id']
                for field in safe_fields:
                    if field in record_data:
                        current_app.logger.info(f"Field {field}: {record_data[field]}")
                
                # Insert data directly using the table object
                insert_stmt = client_table.insert().values(**record_data)
                current_app.logger.info(f"Insert statement prepared: {insert_stmt}")
                
                # Execute the insert statement
                current_app.logger.info("Executing insert statement...")
                result = db.session.execute(insert_stmt)
                current_app.logger.info("Insert statement executed successfully")
                
                client_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
                current_app.logger.info(f"New client ID: {client_id}")
                
                # Update prospect with client reference
                current_app.logger.info("=== UPDATING PROSPECT RECORD ===")
                current_app.logger.info(f"Updating prospect ID {prospect.id} with client_id {client_id}")
                
                # Store the client ID in the prospect record
                prospect.client_id = client_id
                
                # Add conversion timestamp and user if those fields exist
                if hasattr(prospect, 'converted_at'):
                    prospect.converted_at = datetime.utcnow()
                    current_app.logger.info("Set converted_at timestamp")
                if hasattr(prospect, 'converted_by'):
                    prospect.converted_by = current_user.id
                    current_app.logger.info(f"Set converted_by to user ID {current_user.id}")
                
                # Commit all changes in a transaction
                current_app.logger.info("Committing transaction...")
                db.session.commit()
                current_app.logger.info("Transaction committed successfully")
                current_app.logger.info("=== DATABASE OPERATIONS COMPLETED SUCCESSFULLY ===")
                
                # Return appropriate response based on request type
                if is_ajax:
                    response = jsonify({
                        'success': True,
                        'message': 'Prospect successfully converted to client.',
                        'client_id': client_id
                    })
                    response.headers['Content-Type'] = 'application/json'
                    return response
                else:
                    flash('Prospect successfully converted to client.', 'success')
                    return redirect(url_for('user.manage_module', module_id=client_module.id))
                
            except Exception as e:
                db.session.rollback()
                import traceback
                current_app.logger.error("=== DATABASE ERROR OCCURRED ===")
                current_app.logger.error(f"Error converting prospect to client: {str(e)}")
                current_app.logger.error(traceback.format_exc())
                
                # Log the state of key objects
                try:
                    current_app.logger.error(f"Prospect ID: {prospect.id if prospect else 'None'}")
                    current_app.logger.error(f"Client module: {client_module.id if client_module else 'None'}")
                    current_app.logger.error(f"Prospect module: {prospect_module.id if prospect_module else 'None'}")
                except Exception as inner_e:
                    current_app.logger.error(f"Error logging object state: {str(inner_e)}")
                
                current_app.logger.error("=== END OF ERROR DETAILS ===")
                
                # Return appropriate error response based on request type
                if is_ajax:
                    response = jsonify({
                        'success': False,
                        'message': f'Error converting prospect to client: {str(e)}'
                    })
                    response.headers['Content-Type'] = 'application/json'
                    return response, 500
                else:
                    flash(f'Error converting prospect to client: {str(e)}', 'error')
                    return redirect(url_for('user.view_prospect', prospect_id=prospect_id))
        
        # GET request - show form to confirm conversion
        branches = Branch.query.filter_by(status=True).all()
        return render_template('user/convert_prospect.html', prospect=prospect, branches=branches)
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error in convert_to_client: {str(e)}\n{traceback.format_exc()}")
        flash(f'Error: {str(e)}', 'error')
        # Use a safe fallback if prospect_module is not defined
        try:
            return redirect(url_for('user.manage_module', module_id=prospect_module.id))
        except UnboundLocalError:
            # Fallback to dashboard if prospect_module is not defined
            return redirect(url_for('user.dashboard'))


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

    # Get current user ID from Flask-Login
    from flask_login import current_user
    user_id = current_user.id

    # Use the global render_with_modules function
    
    # Statically define the module ID
    module_id = 1  # Replace with the desired module ID

    # Define default values for overdue loans
    default_overdue_loans = {
        'NORMAL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '0-30 days'},
        'WATCH': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '31-90 days'},
        'SUBSTANDARD': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '91-180 days'},
        'DOUBTFUL': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '181-360 days'},
        'LOSS': {'count': 0, 'amount': float(0), 'percentage': float(0), 'description': '360+ days'}
    }

    # Get workflow tasks assigned to the current user based on their role
    workflow_tasks = []
    
    try:
        # Get the current user's roles
        user_roles = [role.id for role in current_user.roles]
        
        if user_roles:
            # Find workflow steps assigned to the user's roles
            from models.post_disbursement_workflows import WorkflowStep, WorkflowInstance, WorkflowDefinition, WorkflowHistory
            
            # Get active workflow instances where the current step is assigned to one of the user's roles
            workflow_instances = db.session.query(
                WorkflowInstance, WorkflowStep, WorkflowDefinition
            ).join(
                WorkflowStep, WorkflowInstance.current_step_id == WorkflowStep.id
            ).join(
                WorkflowDefinition, WorkflowInstance.workflow_id == WorkflowDefinition.id
            ).filter(
                WorkflowStep.role_id.in_(user_roles),
                WorkflowInstance.status == 'active'
            ).all()
            
            # Process workflow instances to get task details
            for instance, step, workflow_def in workflow_instances:
                # For impact assessment verification tasks
                if instance.entity_type == 'loan_impact':
                    from models.loan_impact import LoanImpact
                    from models.impact import ImpactCategory
                    
                    # Get the loan impact record
                    loan_impact = LoanImpact.query.get(instance.entity_id)
                    if loan_impact:
                        # Get category name
                        category = ImpactCategory.query.get(loan_impact.impact_category_id)
                        category_name = category.name if category else 'Unknown'
                        
                        # Get submitter name
                        submitter = Staff.query.get(loan_impact.submitted_by)
                        submitter_name = f"{submitter.first_name} {submitter.last_name}" if submitter else 'Unknown'
                        
                        # Add task to the list
                        workflow_tasks.append({
                            'id': instance.id,
                            'type': 'Impact Assessment Verification',
                            'entity_id': loan_impact.loan_id,  # This is the loan ID
                            'entity_name': f"Loan #{loan_impact.loan_id} - {category_name}",
                            'current_step': step.name,
                            'workflow_name': workflow_def.name,
                            'submitted_by': submitter_name,
                            'submission_date': loan_impact.submission_date,
                            'url': f"/user/impact_assessment/view/{loan_impact.loan_id}"
                        })
    except Exception as e:
        current_app.logger.error(f"Error fetching workflow tasks: {str(e)}")
    
    # Prepare template data
    template_data = {
        'user_id': user_id,
        'default_overdue_loans': default_overdue_loans,
        'workflow_tasks': workflow_tasks
    }

    try:
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            flash('No active core banking system configured', 'error')
            return render_with_modules('user/post_disbursement.html',
                                   user_id=user_id,
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
            error=None,
            user_id=current_user.id
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
            'error': str(e),
            'user_id': current_user.id
        }

        return render_with_modules('user/post_disbursement.html', **default_values)
@user_bp.route('/clear_chat_history', methods=['POST'])
def clear_chat_history():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')

        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # Get the ChatMessage model
        from models.chat_message import ChatMessage

        try:
            # If conversation_id is provided, delete specific conversation
            if conversation_id:
                deleted = ChatMessage.query.filter_by(
                    user_id=user_id,
                    conversation_id=conversation_id
                ).delete()
                message = 'Conversation deleted successfully'
            else:
                # Delete all conversations for the user
                deleted = ChatMessage.query.filter_by(user_id=user_id).delete()
                message = 'All chat history cleared successfully'
            
            # Commit the transaction
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': message,
                'deleted_count': deleted
            })
        except Exception as db_error:
            db.session.rollback()
            current_app.logger.error(f'Database error clearing chat history: {str(db_error)}')
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500

    except Exception as e:
        current_app.logger.error(f'Error processing clear chat history request: {str(e)}')
        return jsonify({'error': str(e)}), 400

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
    """Display guarantors list page with data from the core banking system"""
    current_app.logger.info("Starting guarantors route")
    
    # Define module ID for guarantors
    module_id = 11
    
    try:
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            flash('No active core banking system configured', 'error')
            return render_with_modules('user/guarantors_list.html', 
                                   guarantors=[], 
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
            return render_with_modules('user/guarantors_list.html', 
                                   guarantors=[], 
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
                    expected_columns = expected.columns  # e.g., ['GuarantorID', 'LoanAppID', ...]
                    actual_columns = actual.columns     # e.g., ['guarantor_id', 'loan_app_id', ...]
                    
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
            return render_with_modules('user/guarantors_list.html', 
                                   guarantors=[], 
                                   error=f'Error retrieving mapping data: {str(e)}')

        def build_dynamic_query(mapping):
            try:
                # Access the mapping correctly using string keys
                g = mapping.get("Guarantors", {})
                m = mapping.get("Members", {})
                la = mapping.get("LoanApplications", {})

                # Ensure that the necessary columns are present in the mapping
                if not all(key in g["columns"] for key in ["GuarantorID", "LoanAppID", "GuarantorMemberID", "GuaranteedAmount", "DateAdded", "Status"]):
                    raise KeyError("Missing columns in Guarantors mapping")

                if not all(key in m["columns"] for key in ["MemberID", "MemberNo", "FirstName", "MiddleName", "LastName", "NationalID"]):
                    raise KeyError("Missing columns in Members mapping")

                if not all(key in la["columns"] for key in ["LoanAppID", "LoanNo", "MemberID"]):
                    raise KeyError("Missing columns in LoanApplications mapping")

                # Build the dynamic SQL query using the mapped column and table names
                query = f"""
                    SELECT 
                        g.{g["columns"]["GuarantorID"]} as GuarantorID,
                        g.{g["columns"]["LoanAppID"]} as LoanAppID,
                        g.{g["columns"]["GuarantorMemberID"]} as GuarantorMemberID,
                        g.{g["columns"]["GuaranteedAmount"]} as GuaranteedAmount,
                        g.{g["columns"]["DateAdded"]} as DateAdded,
                        g.{g["columns"]["Status"]} as Status,
                        m.{m["columns"]["NationalID"]} as NationalID,
                        m.{m["columns"]["FirstName"]} as FirstName,
                        m.{m["columns"]["MiddleName"]} as MiddleName,
                        m.{m["columns"]["LastName"]} as LastName,
                        m.{m["columns"]["MemberNo"]} as MemberNo,
                        m.{m["columns"]["MemberID"]} as MemberID,
                        la.{la["columns"]["LoanNo"]} as LoanNo,
                        la.{la["columns"]["MemberID"]} as BorrowerID,
                        bm.{m["columns"]["MemberNo"]} as BorrowerMemberNo,
                        bm.{m["columns"]["FirstName"]} as BorrowerFirstName,
                        bm.{m["columns"]["MiddleName"]} as BorrowerMiddleName,
                        bm.{m["columns"]["LastName"]} as BorrowerLastName
                    FROM {g["actual_table_name"]} g
                    JOIN {m["actual_table_name"]} m ON g.{g["columns"]["GuarantorMemberID"]} = m.{m["columns"]["MemberID"]}
                    JOIN {la["actual_table_name"]} la ON g.{g["columns"]["LoanAppID"]} = la.{la["columns"]["LoanAppID"]}
                    JOIN {m["actual_table_name"]} bm ON la.{la["columns"]["MemberID"]} = bm.{m["columns"]["MemberID"]}
                    ORDER BY g.{g["columns"]["DateAdded"]} DESC
                """
                return query
            except KeyError as e:
                current_app.logger.error(f"Missing key in mapping: {str(e)}")
                raise
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        try:
            # Build and execute the query
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            guarantors = cursor.fetchall()
            current_app.logger.info(f"Retrieved {len(guarantors)} guarantors")
            
            # Process the data for display
            for guarantor in guarantors:
                # Format dates
                if 'DateAdded' in guarantor and guarantor['DateAdded']:
                    if isinstance(guarantor['DateAdded'], datetime):
                        guarantor['DateAdded'] = guarantor['DateAdded'].strftime('%Y-%m-%d')
                
                # Format names
                guarantor['GuarantorName'] = f"{guarantor['FirstName']} {guarantor['MiddleName'] or ''} {guarantor['LastName']}".strip()
                guarantor['BorrowerName'] = f"{guarantor['BorrowerFirstName']} {guarantor['BorrowerMiddleName'] or ''} {guarantor['BorrowerLastName']}".strip()
                
                # Format amounts
                if 'GuaranteedAmount' in guarantor and guarantor['GuaranteedAmount']:
                    guarantor['FormattedAmount'] = f"{float(guarantor['GuaranteedAmount']):,.2f}"
            
            # Calculate statistics
            stats = {
                'total': len(guarantors),
                'active': 0,
                'released': 0,
                'total_guaranteed_amount': 0.0,
                'avg_guaranteed_amount': 0.0,
                'unique_guarantors': set(),
                'unique_borrowers': set()
            }
            
            for guarantor in guarantors:
                # Count by status
                if guarantor.get('Status') == 'Active':
                    stats['active'] += 1
                elif guarantor.get('Status') == 'Released':
                    stats['released'] += 1
                
                # Sum guaranteed amounts
                if 'GuaranteedAmount' in guarantor and guarantor['GuaranteedAmount']:
                    stats['total_guaranteed_amount'] += float(guarantor['GuaranteedAmount'])
                
                # Count unique guarantors and borrowers
                if 'GuarantorMemberID' in guarantor:
                    stats['unique_guarantors'].add(guarantor['GuarantorMemberID'])
                if 'BorrowerID' in guarantor:
                    stats['unique_borrowers'].add(guarantor['BorrowerID'])
            
            # Calculate averages and convert sets to counts
            if stats['total'] > 0:
                stats['avg_guaranteed_amount'] = stats['total_guaranteed_amount'] / stats['total']
            
            stats['unique_guarantors'] = len(stats['unique_guarantors'])
            stats['unique_borrowers'] = len(stats['unique_borrowers'])
            
            # Format currency values
            stats['total_guaranteed_amount_formatted'] = f"{stats['total_guaranteed_amount']:,.2f}"
            stats['avg_guaranteed_amount_formatted'] = f"{stats['avg_guaranteed_amount']:,.2f}"
            
            return render_with_modules('user/guarantors_list.html', guarantors=guarantors, stats=stats)
            
        except Exception as e:
            current_app.logger.error(f"Error executing query: {str(e)}")
            flash(f'Error retrieving guarantors: {str(e)}', 'error')
            return render_with_modules('user/guarantors_list.html', 
                                   guarantors=[], 
                                   error=f'Error retrieving guarantors: {str(e)}')
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in guarantors route: {str(e)}")
        flash(f'Unexpected error: {str(e)}', 'error')
        return render_with_modules('user/guarantors_list.html', 
                               guarantors=[], 
                               error=f'Unexpected error: {str(e)}')
    finally:
        # Close database connections
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@user_bp.route('/sync-guarantors-list', methods=['POST'])
@login_required
@csrf.exempt
def sync_guarantors_list():
    """Sync all guarantors from the core banking system"""
    current_app.logger.info("Starting sync_guarantors_list route")
    
    # Simply return success - the API endpoint will handle the actual data fetching
    return jsonify({
        'success': True, 
        'message': 'Guarantors list refreshed successfully'
    })

@user_bp.route('/guarantor/<int:guarantor_id>')
@login_required
def view_guarantor(guarantor_id):
    """Display details for a specific guarantor"""
    current_app.logger.info(f"Starting view_guarantor route for guarantor_id: {guarantor_id}")
    
    # Define module ID for guarantors
    module_id = 11
    
    try:
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            flash('No active core banking system configured', 'error')
            return render_with_modules('user/guarantor_details.html', 
                                   guarantor=None, 
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
            return render_with_modules('user/guarantor_details.html', 
                                   guarantor=None, 
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
                    expected_columns = expected.columns  # e.g., ['GuarantorID', 'LoanAppID', ...]
                    actual_columns = actual.columns     # e.g., ['guarantor_id', 'loan_app_id', ...]
                    
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
            return render_with_modules('user/guarantor_details.html', 
                                   guarantor=None, 
                                   error=f'Error retrieving mapping data: {str(e)}')

        def build_dynamic_query(mapping, guarantor_id):
            try:
                # Access the mapping correctly using string keys
                g = mapping.get("Guarantors", {})
                m = mapping.get("Members", {})
                la = mapping.get("LoanApplications", {})

                # Ensure that the necessary columns are present in the mapping
                if not all(key in g["columns"] for key in ["GuarantorID", "LoanAppID", "GuarantorMemberID", "GuaranteedAmount", "DateAdded", "Status"]):
                    raise KeyError("Missing columns in Guarantors mapping")

                if not all(key in m["columns"] for key in ["MemberID", "MemberNo", "FirstName", "MiddleName", "LastName", "NationalID"]):
                    raise KeyError("Missing columns in Members mapping")

                if not all(key in la["columns"] for key in ["LoanAppID", "LoanNo", "MemberID"]):
                    raise KeyError("Missing columns in LoanApplications mapping")

                # Build the dynamic SQL query using the mapped column and table names
                query = f"""
                    SELECT 
                        g.{g["columns"]["GuarantorID"]} as GuarantorID,
                        g.{g["columns"]["LoanAppID"]} as LoanAppID,
                        g.{g["columns"]["GuarantorMemberID"]} as GuarantorMemberID,
                        g.{g["columns"]["GuaranteedAmount"]} as GuaranteedAmount,
                        g.{g["columns"]["DateAdded"]} as DateAdded,
                        g.{g["columns"]["Status"]} as Status,
                        m.{m["columns"]["NationalID"]} as NationalID,
                        m.{m["columns"]["FirstName"]} as FirstName,
                        m.{m["columns"]["MiddleName"]} as MiddleName,
                        m.{m["columns"]["LastName"]} as LastName,
                        m.{m["columns"]["MemberNo"]} as MemberNo,
                        m.{m["columns"]["MemberID"]} as MemberID,
                        la.{la["columns"]["LoanNo"]} as LoanNo,
                        la.{la["columns"]["MemberID"]} as BorrowerID,
                        bm.{m["columns"]["MemberNo"]} as BorrowerMemberNo,
                        bm.{m["columns"]["FirstName"]} as BorrowerFirstName,
                        bm.{m["columns"]["MiddleName"]} as BorrowerMiddleName,
                        bm.{m["columns"]["LastName"]} as BorrowerLastName
                    FROM {g["actual_table_name"]} g
                    JOIN {m["actual_table_name"]} m ON g.{g["columns"]["GuarantorMemberID"]} = m.{m["columns"]["MemberID"]}
                    JOIN {la["actual_table_name"]} la ON g.{g["columns"]["LoanAppID"]} = la.{la["columns"]["LoanAppID"]}
                    JOIN {m["actual_table_name"]} bm ON la.{la["columns"]["MemberID"]} = bm.{m["columns"]["MemberID"]}
                    WHERE g.{g["columns"]["GuarantorID"]} = %s
                """
                return query
            except KeyError as e:
                current_app.logger.error(f"Missing key in mapping: {str(e)}")
                raise
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        try:
            # Build and execute the query
            query = build_dynamic_query(mapping, guarantor_id)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query, (guarantor_id,))
            guarantor = cursor.fetchone()
            
            if not guarantor:
                flash(f'Guarantor with ID {guarantor_id} not found', 'error')
                return render_with_modules('user/guarantor_details.html', 
                                      guarantor=None, 
                                      error=f'Guarantor with ID {guarantor_id} not found')
            
            current_app.logger.info(f"Retrieved guarantor data: {guarantor}")
            
            # Process the data for display
            # Format dates
            if 'DateAdded' in guarantor and guarantor['DateAdded']:
                if isinstance(guarantor['DateAdded'], datetime):
                    guarantor['DateAdded'] = guarantor['DateAdded'].strftime('%Y-%m-%d')
            
            # Format names
            guarantor['GuarantorName'] = f"{guarantor['FirstName']} {guarantor['MiddleName'] or ''} {guarantor['LastName']}".strip()
            guarantor['BorrowerName'] = f"{guarantor['BorrowerFirstName']} {guarantor['BorrowerMiddleName'] or ''} {guarantor['BorrowerLastName']}".strip()
            
            # Format amounts
            if 'GuaranteedAmount' in guarantor and guarantor['GuaranteedAmount']:
                guarantor['FormattedAmount'] = f"{float(guarantor['GuaranteedAmount']):,.2f}"
            
            # Get guarantor communication history if available
            try:
                # Query for communication history
                comm_query = f"""
                    SELECT * FROM GuarantorCommunications 
                    WHERE GuarantorID = %s
                    ORDER BY CommunicationDate DESC
                """
                cursor.execute(comm_query, (guarantor_id,))
                communications = cursor.fetchall()
                
                # Format communication dates
                for comm in communications:
                    if 'CommunicationDate' in comm and comm['CommunicationDate']:
                        if isinstance(comm['CommunicationDate'], datetime):
                            comm['FormattedDate'] = comm['CommunicationDate'].strftime('%Y-%m-%d %H:%M')
                
                guarantor['communications'] = communications
            except Exception as e:
                current_app.logger.warning(f"Could not retrieve communication history: {str(e)}")
                guarantor['communications'] = []
            
            return render_with_modules('user/guarantor_details.html', guarantor=guarantor)
            
        except Exception as e:
            current_app.logger.error(f"Error executing query: {str(e)}")
            flash(f'Error retrieving guarantor details: {str(e)}', 'error')
            return render_with_modules('user/guarantor_details.html', 
                                   guarantor=None, 
                                   error=f'Error retrieving guarantor details: {str(e)}')
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in view_guarantor route: {str(e)}")
        flash(f'Unexpected error: {str(e)}', 'error')
        return render_with_modules('user/guarantor_details.html', 
                               guarantor=None, 
                               error=f'Unexpected error: {str(e)}')
    finally:
        # Close database connections
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

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

        # Get all loans from the database
        loans = Loan.query.all()

        # Add loans to template data
        template_data = {}
        template_data['loans'] = loans

        # Return the template with the data
        return render_template('user/loan_rescheduling.html', loan_reschedules=loan_reschedules, **template_data)
    except Exception as e:
        current_app.logger.error(f"Error rendering loan rescheduling page: {str(e)}")
        flash('An error occurred while loading the loan rescheduling page', 'error')
        return redirect(url_for('user.dashboard'))

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

@user_bp.route('/field-visits')
@login_required
def field_visits():
    try:
        print("Entering field_visits route handler")
        current_app.logger.info("Entering field_visits route handler")
        
        # Fetch field visits from the database
        try:
            field_visits = FieldVisit.query.all()
            print(f"Found {len(field_visits)} field visits")
            current_app.logger.info(f"Found {len(field_visits)} field visits")
        except Exception as db_error:
            print(f"Error fetching field visits: {str(db_error)}")
            current_app.logger.error(f"Error fetching field visits: {str(db_error)}")
            import traceback
            print(traceback.format_exc())
            current_app.logger.error(traceback.format_exc())
            field_visits = []  # Use empty list if query fails
        
        # Get staff names to display in the table
        staff_ids = [visit.field_officer_id for visit in field_visits if visit.field_officer_id]
        staff_dict = {}
        
        if staff_ids:
            try:
                staff_records = Staff.query.filter(Staff.id.in_(staff_ids)).all()
                for staff in staff_records:
                    staff_dict[staff.id] = f"{staff.first_name} {staff.last_name}"
                print(f"Found {len(staff_records)} staff records")
                current_app.logger.info(f"Found {len(staff_records)} staff records")
            except Exception as staff_error:
                print(f"Error fetching staff data: {str(staff_error)}")
                current_app.logger.error(f"Error fetching staff data: {str(staff_error)}")
                import traceback
                print(traceback.format_exc())
                current_app.logger.error(traceback.format_exc())
        
        # Add staff names to visits and format dates
        for visit in field_visits:
            visit.field_officer_name = staff_dict.get(visit.field_officer_id, 'Unknown')
            # Format the date and time for display
            if visit.visit_date:
                visit.visit_date = visit.visit_date.strftime('%Y-%m-%d')
            # Format the updated_at timestamp
            if visit.updated_at:
                visit.updated_at = visit.updated_at.strftime('%Y-%m-%d %H:%M')
            # Calculate missed payments based on days in arrears
            if hasattr(visit, 'days_in_arrears') and visit.days_in_arrears:
                visit.missed_payments = math.ceil(visit.days_in_arrears / 30)
        
        # Get today's date for highlighting
        today = datetime.now().date()
        
        # Try using render_template with the data
        try:
            # Get visible modules for the sidebar
            try:
                visible_modules = PostDisbursementModule.query.filter_by(hidden=False).order_by(PostDisbursementModule.order).all()
                print(f"Found {len(visible_modules)} visible modules")
                current_app.logger.info(f"Found {len(visible_modules)} visible modules")
            except Exception as module_error:
                print(f"Error fetching modules: {str(module_error)}")
                current_app.logger.info(f"Error fetching modules: {str(module_error)}")
                visible_modules = []  # Use empty list if query fails
            
            # Create stats dictionary for the dashboard counters
            stats = {
                'scheduled': 0,
                'in_progress': 0,
                'completed': 0,
                'cancelled': 0,
                'submitted_reports': 0,
                'total': 0
            }
            
            # Get all completed visits that need reports
            completed_visit_ids = []
            visits_with_reports = []
            
            # If we have field visits data, calculate the stats
            if field_visits:
                for visit in field_visits:
                    stats['total'] += 1
                    if visit.status == 'scheduled':
                        stats['scheduled'] += 1
                    elif visit.status == 'in-progress':
                        stats['in_progress'] += 1
                    elif visit.status == 'completed':
                        stats['completed'] += 1
                        completed_visit_ids.append(visit.id)
                    elif visit.status == 'cancelled':
                        stats['cancelled'] += 1
                
                # Query the status history table to find visits with report submissions
                if completed_visit_ids:
                    try:
                        # Find visits with report submissions in the status history
                        # Look for any status history entry for completed visits
                        # This indicates a report has been submitted
                        report_submissions = db.session.query(FieldVisitStatusHistory.field_visit_id)\
                            .filter(FieldVisitStatusHistory.field_visit_id.in_(completed_visit_ids))\
                            .distinct().all()
                        
                        # Debug information
                        print(f"Completed visits: {completed_visit_ids}")
                        print(f"Found report submissions: {report_submissions}")
                        
                        # Extract the visit IDs that have report submissions
                        visits_with_reports = [r[0] for r in report_submissions]
                        
                        # Count submitted reports
                        stats['submitted_reports'] = len(visits_with_reports)
                    except Exception as e:
                        print(f"Error querying status history for reports: {str(e)}")
                        current_app.logger.error(f"Error querying status history for reports: {str(e)}")
                        # Fallback: assume no reports have been submitted
                        stats['submitted_reports'] = 0
            
            # Render with direct template call including the stats
            return render_template('user/field_visits.html', field_visits=field_visits, today=today, visible_modules=visible_modules, stats=stats)
        except Exception as render_error:
            print(f"Error with template render: {str(render_error)}")
            current_app.logger.error(f"Error with template render: {str(render_error)}")
            import traceback
            print(traceback.format_exc())
            current_app.logger.error(traceback.format_exc())
            raise
    except Exception as e:
        print(f"Error in simplified field_visits route: {str(e)}")
        current_app.logger.error(f"Error in simplified field_visits route: {str(e)}")
        import traceback
        print(traceback.format_exc())
        current_app.logger.error(traceback.format_exc())
        flash('An error occurred while loading field visits: ' + str(e), 'error')
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
        # Get active credit bureaus for the dropdown
        from models.credit_bureau import CreditBureau
        credit_bureaus = CreditBureau.query.filter_by(is_active=True).all()
        
        return render_with_modules('user/crb_reports.html', credit_bureaus=credit_bureaus)
    except Exception as e:
        current_app.logger.error(f"Error rendering CRB reports page: {str(e)}")
        flash('An error occurred while loading the CRB reports page', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/crb-reports/generate', methods=['POST'])
@login_required
def generate_crb_report():
    """Generate a CRB report for a customer"""
    # Add detailed logging at the start of the function
    current_app.logger.info("=== Starting CRB report generation ===")
    current_app.logger.info(f"Form data: {request.form}")
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        current_app.logger.info(f"Created logs directory: {log_dir}")
    
    # Write debug information to a specific debug log file
    debug_log_file = os.path.join(log_dir, 'crb_debug.log')
    with open(debug_log_file, 'a') as f:
        f.write(f"=== {datetime.now()} - CRB Report Generation ===\n")
        f.write(f"Form data: {request.form}\n")
    try:
        # Get form data
        customer_id = request.form.get('customer')
        bureau_id = request.form.get('bureau')
        report_type = request.form.get('report_type', 'full')
        
        if not customer_id or not bureau_id:
            flash('Customer and Credit Bureau are required', 'error')
            return redirect(url_for('user.crb_reports'))
        
        # Get customer details
        from models.credit_bureau import CreditBureau
        
        # Get credit bureau credentials
        bureau = CreditBureau.query.get(bureau_id)
        if not bureau:
            flash('Selected Credit Bureau not found', 'error')
            return redirect(url_for('user.crb_reports'))
        
        # Get customer details directly from the form submission
        # The form already has all the necessary customer details
        customer_name = request.form.get('customer_name', '')
        national_id = request.form.get('national_id', '')
        phone_number = request.form.get('phone_number', '')
        email = request.form.get('email', '')
        
        # Log the customer details
        current_app.logger.info(f"Customer details from form: name={customer_name}, national_id={national_id}, phone={phone_number}, email={email}")
        
        # Validate required fields
        if not national_id:
            flash('Customer National ID is required for CRB report', 'error')
            return redirect(url_for('user.crb_reports'))
        
        # Log the customer data for debugging
        customer_data = {
            'customer_name': customer_name,
            'national_id': national_id,
            'phone_number': phone_number,
            'email': email
        }
        current_app.logger.info(f"Customer data for CRB report: {customer_data}")
        
        # Check if we have the required fields
        if not national_id:
            flash('Customer National ID is required for CRB report', 'error')
            return redirect(url_for('user.crb_reports'))
        
        # Prepare response for different bureau providers
        if bureau.provider.lower() == 'metropol':
            try:
                # Import the CRB service
                from services.crb_service import CRBService
                from models.crb_report import CRBReport
                
                # Prepare customer data for the API
                customer_data = {
                    'customer_name': customer_name,
                    'national_id': national_id,
                    'phone_number': phone_number,
                    'email': email
                }
                
                # Initialize the CRB service with bureau credentials
                crb_service = CRBService(bureau=bureau)
                
                # Generate the report
                current_app.logger.info(f"Calling Metropol API for customer {customer_name} with National ID {national_id}")
                report = crb_service.generate_report(customer_data, report_type)
                
                # Get the report data
                report_data = {
                    'customer_name': customer_name,
                    'national_id': national_id,
                    'phone_number': phone_number,
                    'email': email,
                    'report_type': report_type,
                    'bureau': bureau.name,
                    'timestamp': report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': report.status,
                    'score': report.credit_score or 'N/A',
                    'risk_level': 'N/A',  # This would be calculated based on the score
                    'report_reference': report.report_reference or 'N/A',
                    'report_id': report.id
                }
                
                # Add risk level based on credit score
                if report.credit_score:
                    score = int(report.credit_score)
                    if score >= 700:
                        report_data['risk_level'] = 'Low'
                    elif score >= 500:
                        report_data['risk_level'] = 'Medium'
                    else:
                        report_data['risk_level'] = 'High'
                
                # Add report data if available
                if report.report_data:
                    report_data['full_report'] = report.report_data
                
                # Return success message
                flash(f'CRB report generated successfully for {customer_name}', 'success')
                
                # Return the report data
                return render_with_modules('user/crb_report_result.html', report=report_data)
                
            except ValueError as e:
                # Handle specific error messages from the API service
                error_message = str(e)
                current_app.logger.error(f"Metropol API error: {error_message}")
                
                # Provide user-friendly error messages based on the error
                if "Authentication failed" in error_message:
                    flash('Authentication failed. Please check the API credentials for the selected credit bureau.', 'error')
                elif "Network error" in error_message:
                    flash('Network error connecting to the credit bureau. Please check the API base URL and try again.', 'error')
                elif "No access token" in error_message:
                    flash('Invalid API credentials. The credit bureau did not provide an authentication token.', 'error')
                else:
                    flash(f'Error generating CRB report: {error_message}', 'error')
                
                # Add a flash message with detailed error information for administrators
                flash(f'Technical details: {error_message}', 'warning')
                
                return redirect(url_for('user.crb_reports'))
                
            except Exception as e:
                error_message = str(e)
                current_app.logger.error(f"Unexpected error calling Metropol API: {error_message}")
                flash(f'An unexpected error occurred while generating the CRB report. Please try again later.', 'error')
                flash(f'Technical details: {error_message}', 'warning')
                return redirect(url_for('user.crb_reports'))
        
        else:
            flash(f'Credit Bureau provider {bureau.provider} not supported yet', 'error')
            return redirect(url_for('user.crb_reports'))
            
    except Exception as e:
        # Log the detailed error
        current_app.logger.error(f"Error generating CRB report: {str(e)}")
        
        # Write to debug log file
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        debug_log_file = os.path.join(log_dir, 'crb_debug.log')
        with open(debug_log_file, 'a') as f:
            f.write(f"=== {datetime.now()} - CRB Report Generation ERROR ===\n")
            f.write(f"Error: {str(e)}\n")
        
        # Provide a more specific error message to the user
        if 'Invalid or missing credentials' in str(e) or 'API key is missing' in str(e):
            flash('The credit bureau API credentials are invalid or missing. Please contact the administrator.', 'error')
        elif 'Network error' in str(e):
            flash('Could not connect to the credit bureau API. Please check your internet connection and try again.', 'error')
        elif 'Authentication failed' in str(e):
            flash('Authentication with the credit bureau failed. Please check your credentials.', 'error')
        else:
            flash('An error occurred while generating the CRB report: ' + str(e), 'error')
            
        return redirect(url_for('user.crb_reports'))

@user_bp.route('/view-logs')
@login_required
def view_logs():
    """View application logs for debugging"""
    try:
        # Get the log file path
        log_file = current_app.config.get('LOG_FILE', '/tmp/loan_system.log')
        
        # Read the last 100 lines of the log file
        import subprocess
        result = subprocess.run(['tail', '-n', '100', log_file], capture_output=True, text=True)
        logs = result.stdout
        
        return render_with_modules('user/view_logs.html', logs=logs)
    except Exception as e:
        current_app.logger.error(f"Error viewing logs: {str(e)}")
        flash('An error occurred while viewing logs', 'error')
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
        
        # Count upcoming hearings (next 30 days)
        today = datetime.now().date()
        thirty_days_later = today + timedelta(days=30)
        upcoming_hearings = LegalCase.query.filter(
            LegalCase.next_hearing_date.between(today, thirty_days_later)
        ).count()
        
        # Calculate total amount in litigation
        active_cases_query = LegalCase.query.filter_by(status='Active').all()
        amount_in_litigation = sum(case.amount_claimed for case in active_cases_query if case.amount_claimed)
        
        # Format amount with commas using KES currency
        amount_in_litigation = f"KES {amount_in_litigation:,.2f}"
        
        return render_with_modules('user/legal_cases.html', 
                            legal_cases=legal_cases,
                            active_cases=active_cases,
                            resolved_cases=resolved_cases,
                            upcoming_hearings=upcoming_hearings,
                            amount_in_litigation=amount_in_litigation)
    except Exception as e:
        current_app.logger.error(f"Error loading legal cases: {str(e)}")
        flash('An error occurred while loading legal cases. Please try again.', 'error')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/legal-cases/debug')
@login_required
def debug_legal_cases():
    """Debug route to list all legal cases"""
    try:
        # Get all legal cases
        legal_cases = LegalCase.query.all()
        
        # Prepare response data
        cases_data = []
        for case in legal_cases:
            cases_data.append({
                'id': case.id,
                'loan_id': case.loan_id,
                'case_number': case.case_number,
                'plaintiff': case.plaintiff,
                'defendant': case.defendant,
                'status': case.status
            })
        
        return jsonify({
            'count': len(cases_data),
            'cases': cases_data
        })
    
    except Exception as e:
        current_app.logger.error(f"Error debugging legal cases: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'An error occurred while debugging legal cases'}), 500

@user_bp.route('/legal-cases/<int:case_id>/history')
@login_required
def get_case_history(case_id):
    """Get case history data including plaintiff/defendant details, case history information, and attachments"""
    try:
        # Get the legal case with detailed logging
        current_app.logger.info(f"Fetching legal case with ID: {case_id}")
        legal_case = LegalCase.query.get_or_404(case_id)
        current_app.logger.info(f"Found legal case: {legal_case.id}, plaintiff: {legal_case.plaintiff}, defendant: {legal_case.defendant}")
        
        # Get case history entries with their attachments
        case_history = CaseHistory.query.filter_by(case_id=case_id).order_by(CaseHistory.action_date.desc()).all()
        current_app.logger.info(f"Found {len(case_history)} history entries for case {case_id}")
        
        # Get case attachments
        case_attachments = LegalCaseAttachment.query.filter_by(legal_case_id=case_id).all()
        current_app.logger.info(f"Found {len(case_attachments)} attachments for case {case_id}")
        
        # Prepare the response data
        history_data = []
        for entry in case_history:
            # Get attachments for this history entry
            attachments = []
            for attachment in entry.history_attachments:
                attachments.append({
                    'id': attachment.id,
                    'file_name': attachment.file_name,
                    'file_type': attachment.file_type,
                    'file_size': attachment.file_size,
                    'uploaded_at': attachment.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if attachment.uploaded_at else None
                })
            
            history_data.append({
                'id': entry.id,
                'action': entry.action,
                'action_date': entry.action_date.strftime('%Y-%m-%d %H:%M:%S') if entry.action_date else None,
                'notes': entry.notes,
                'status': entry.status,
                'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S') if entry.created_at else None,
                'created_by': entry.created_by,
                'attachments': attachments
            })
        
        # Prepare case attachments data
        attachments_data = []
        for attachment in case_attachments:
            attachments_data.append({
                'id': attachment.id,
                'file_name': attachment.file_name,
                'file_type': attachment.file_type,
                'uploaded_at': attachment.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if attachment.uploaded_at else None
            })
        
        # Prepare case data with explicit handling of plaintiff and defendant
        case_data = {
            'id': legal_case.id,
            'loan_id': legal_case.loan_id,
            'case_number': legal_case.case_number,
            'court_name': legal_case.court_name,
            'case_type': legal_case.case_type,
            'filing_date': legal_case.filing_date.strftime('%Y-%m-%d') if legal_case.filing_date else None,
            'status': legal_case.status,
            'plaintiff': legal_case.plaintiff or "No plaintiff specified",  # Ensure we have a value
            'defendant': legal_case.defendant or "No defendant specified",  # Ensure we have a value
            'amount_claimed': legal_case.amount_claimed,
            'lawyer_name': legal_case.lawyer_name,
            'lawyer_contact': legal_case.lawyer_contact,
            'description': legal_case.description,
            'next_hearing_date': legal_case.next_hearing_date.strftime('%Y-%m-%d') if legal_case.next_hearing_date else None
        }
        
        # Log the response data for debugging
        current_app.logger.info(f"Returning case data with plaintiff: {case_data['plaintiff']}, defendant: {case_data['defendant']}")
        
        response_data = {
            'case': case_data,
            'history': history_data,
            'attachments': attachments_data
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        current_app.logger.error(f"Error getting case history: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'An error occurred while getting case history'}), 500

@user_bp.route('/legal-cases/<int:case_id>/attachments/<int:attachment_id>/view')
@login_required
def view_case_attachment(case_id, attachment_id):
    """View a case attachment"""
    try:
        # Get the attachment
        attachment = LegalCaseAttachment.query.filter_by(id=attachment_id, legal_case_id=case_id).first_or_404()
        
        # Check if the file exists
        if not os.path.exists(attachment.file_path):
            flash('Attachment file not found.', 'error')
            return redirect(url_for('user.legal_cases'))
        
        # Determine content type
        content_type = attachment.file_type or 'application/octet-stream'
        
        # For images and PDFs, display them directly
        if content_type.startswith('image/') or content_type == 'application/pdf':
            return send_file(attachment.file_path, mimetype=content_type)
        
        # For other file types, force download
        return send_file(attachment.file_path, 
                         mimetype=content_type,
                         as_attachment=True,
                         download_name=attachment.file_name)
    
    except Exception as e:
        current_app.logger.error(f"Error viewing case attachment: {str(e)}")
        flash('An error occurred while viewing the attachment.', 'error')
        return redirect(url_for('user.legal_cases'))

@user_bp.route('/legal-cases/<int:case_id>/attachments/<int:attachment_id>/download')
@login_required
def download_case_attachment(case_id, attachment_id):
    """Download a case attachment"""
    try:
        # Get the attachment
        attachment = LegalCaseAttachment.query.filter_by(id=attachment_id, legal_case_id=case_id).first_or_404()
        
        # Check if the file exists
        if not os.path.exists(attachment.file_path):
            flash('Attachment file not found.', 'error')
            return redirect(url_for('user.legal_cases'))
        
        # Force download
        return send_file(attachment.file_path, 
                         mimetype=attachment.file_type or 'application/octet-stream',
                         as_attachment=True,
                         download_name=attachment.file_name)
    
    except Exception as e:
        current_app.logger.error(f"Error downloading case attachment: {str(e)}")
        flash('An error occurred while downloading the attachment.', 'error')
        return redirect(url_for('user.legal_cases'))

@user_bp.route('/legal-cases/<int:case_id>/history/<int:history_id>/attachments/<int:attachment_id>/view')
@login_required
def view_case_history_attachment(case_id, history_id, attachment_id):
    """View a case history attachment"""
    try:
        # Get the case history entry
        history_entry = CaseHistory.query.filter_by(id=history_id, case_id=case_id).first_or_404()
        
        # Get the attachment
        attachment = CaseHistoryAttachment.query.filter_by(id=attachment_id, case_history_id=history_id).first_or_404()
        
        # Check if the file exists
        if not os.path.exists(attachment.file_path):
            flash('Attachment file not found.', 'error')
            return redirect(url_for('user.legal_cases'))
        
        # Determine content type
        content_type = attachment.file_type or 'application/octet-stream'
        
        # For images and PDFs, display them directly
        if content_type.startswith('image/') or content_type == 'application/pdf':
            return send_file(attachment.file_path, mimetype=content_type)
        
        # For other file types, force download
        return send_file(attachment.file_path, 
                         mimetype=content_type,
                         as_attachment=True,
                         download_name=attachment.file_name)
    
    except Exception as e:
        current_app.logger.error(f"Error viewing case history attachment: {str(e)}")
        flash('An error occurred while viewing the attachment.', 'error')
        return redirect(url_for('user.legal_cases'))

@user_bp.route('/legal-cases/<int:case_id>/history/<int:history_id>/attachments/<int:attachment_id>/download')
@login_required
def download_case_history_attachment(case_id, history_id, attachment_id):
    """Download a case history attachment"""
    try:
        # Get the case history entry
        history_entry = CaseHistory.query.filter_by(id=history_id, case_id=case_id).first_or_404()
        
        # Get the attachment
        attachment = CaseHistoryAttachment.query.filter_by(id=attachment_id, case_history_id=history_id).first_or_404()
        
        # Check if the file exists
        if not os.path.exists(attachment.file_path):
            flash('Attachment file not found.', 'error')
            return redirect(url_for('user.legal_cases'))
        
        # Force download
        return send_file(attachment.file_path, 
                         mimetype=attachment.file_type or 'application/octet-stream',
                         as_attachment=True,
                         download_name=attachment.file_name)
    
    except Exception as e:
        current_app.logger.error(f"Error downloading case history attachment: {str(e)}")
        flash('An error occurred while downloading the attachment.', 'error')
        return redirect(url_for('user.legal_cases'))

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
        # Instead of redirecting, render the page with an error message
        return render_with_modules('user/auction_process.html',
                              auctions=[],
                              pending_auctions=0,
                              completed_auctions=0,
                              properties_listed=0,
                              total_recovery=0,
                              error_message='An error occurred while loading the auction data')

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
            property_location=data.get('property_location'),
            property_description=data['property_description'],
            valuation_amount=data['valuation_amount'],
            reserve_price=data['reserve_price'],
            auction_date=auction_date,
            auction_venue=data['auction_venue'],
            status=data.get('status', 'Scheduled'),  # Default to Scheduled if not provided
            auctioneer_name=data.get('auctioneer_name'),
            auctioneer_contact=data.get('auctioneer_contact'),
            advertisement_date=advertisement_date,
            advertisement_medium=data.get('advertisement_medium'),
            notes=data.get('notes'),
            # Add staff assignment data
            assigned_staff_id=data.get('assigned_staff_id'),
            assigned_staff_name=data.get('assigned_staff_name'),
            supervisor_id=data.get('supervisor_id'),
            supervisor_name=data.get('supervisor_name')
        )
        
        db.session.add(new_auction)
        db.session.commit()
        
        return jsonify({'message': 'Auction created successfully', 'id': new_auction.id})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating auction: {str(e)}")
        return jsonify({'error': 'An error occurred while creating the auction'}), 500

@user_bp.route('/auction/<int:auction_id>/history', methods=['GET'])
@login_required
def get_auction_history(auction_id):
    try:
        auction = Auction.query.get_or_404(auction_id)
        history_entries = AuctionHistory.query.filter_by(auction_id=auction_id).order_by(AuctionHistory.action_date.desc()).all()
        
        history_data = []
        for entry in history_entries:
            attachments = [{
                'id': att.id,
                'file_name': att.file_name,
                'file_type': att.file_type,
                'uploaded_at': att.uploaded_at.isoformat() if att.uploaded_at else None,
                'url': url_for('user.view_auction_attachment', auction_id=auction_id, history_id=entry.id, attachment_id=att.id),
                'download_url': url_for('user.download_auction_attachment', auction_id=auction_id, history_id=entry.id, attachment_id=att.id)
            } for att in entry.attachments]
            
            history_data.append({
                'id': entry.id,
                'action': entry.action,
                'action_date': entry.action_date.isoformat(),
                'notes': entry.notes,
                'status': entry.status,
                'created_at': entry.created_at.isoformat() if entry.created_at else None,
                'created_by': entry.created_by,
                'attachments': attachments
            })
        
        return jsonify(history_data)
    except Exception as e:
        current_app.logger.error(f"Error fetching auction history: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching auction history'}), 500

@user_bp.route('/auction/<int:auction_id>/history/<int:history_id>/attachments/<int:attachment_id>/view')
@login_required
def view_auction_attachment(auction_id, history_id, attachment_id):
    try:
        # Get the auction and attachment
        auction = Auction.query.get_or_404(auction_id)
        history_entry = AuctionHistory.query.get_or_404(history_id)
        attachment = AuctionHistoryAttachment.query.get_or_404(attachment_id)
        
        # Verify the attachment belongs to this auction history
        if history_entry.auction_id != auction_id or attachment.history_id != history_id:
            abort(404)
        
        # Get the directory name from the file path
        directory = os.path.dirname(attachment.file_path)
        filename = os.path.basename(attachment.file_path)
        
        return send_from_directory(directory, filename)
    except Exception as e:
        current_app.logger.error(f"Error serving auction attachment: {str(e)}")
        abort(404)

@user_bp.route('/auction/<int:auction_id>/history/<int:history_id>/attachments/<int:attachment_id>/download')
@login_required
def download_auction_attachment(auction_id, history_id, attachment_id):
    try:
        # Get the auction and attachment
        auction = Auction.query.get_or_404(auction_id)
        history_entry = AuctionHistory.query.get_or_404(history_id)
        attachment = AuctionHistoryAttachment.query.get_or_404(attachment_id)
        
        # Verify the attachment belongs to this auction history
        if history_entry.auction_id != auction_id or attachment.history_id != history_id:
            abort(404)
        
        # Get the directory name from the file path
        directory = os.path.dirname(attachment.file_path)
        filename = os.path.basename(attachment.file_path)
        
        return send_from_directory(
            directory,
            filename,
            as_attachment=True,
            download_name=attachment.file_name
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading auction attachment: {str(e)}")
        abort(404)

@user_bp.route('/auction/<int:auction_id>/add_update', methods=['POST'])
@login_required
def add_auction_update(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    
    # Get form data
    current_app.logger.debug(f"Form data received: {request.form}")
    action_type = request.form.get('action')
    action_date_str = request.form.get('action_date')
    notes = request.form.get('notes')
    status = request.form.get('status')
    current_app.logger.debug(f"Parsed values: action={action_type}, date={action_date_str}, status={status}")
    
    # Validate required fields with detailed error message
    missing_fields = []
    if not action_type:
        missing_fields.append('Action Type')
    if not action_date_str:
        missing_fields.append('Action Date')
    if not status:
        missing_fields.append('Status')
    
    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        current_app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 400

    # Parse action_date
    try:
        # The HTML datetime-local input format is 'YYYY-MM-DDTHH:MM'
        action_date = datetime.strptime(action_date_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        return jsonify({'error': 'Invalid date format for Action Date'}), 400

    history_entry = None # Initialize to ensure it's in scope for finally block if needed

    try:
        history_entry = AuctionHistory(
            auction_id=auction.id,
            action=action_type,
            action_date=action_date,
            notes=notes, # Renamed from description
            status=status,
            created_by=current_user.id,
            # created_at is default now() in model
        )
        db.session.add(history_entry)
        db.session.flush() # Flush to get history_entry.id for attachments
        
        uploaded_files_info = []
        files = request.files.getlist('attachments')
        
        if files:
            # Ensure base upload folder exists
            base_upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            auction_attachment_folder = os.path.join(base_upload_folder, 'auction_attachments', str(history_entry.id))
            
            try:
                os.makedirs(auction_attachment_folder, exist_ok=True)
            except OSError as e:
                current_app.logger.error(f"Error creating directory {auction_attachment_folder}: {e}")
                db.session.rollback()
                return jsonify({'error': 'Failed to create directory for attachments'}), 500

            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(auction_attachment_folder, filename)
                    
                    try:
                        file.save(file_path)
                        
                        # Get file type (extension)
                        file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
                        
                        attachment = AuctionHistoryAttachment(
                            history_id=history_entry.id,
                            file_name=filename,
                            file_path=file_path, # Storing relative path from app root might be better for serving
                                               # Or adjust based on how UPLOAD_FOLDER is configured and served.
                                               # For now, using the full path as saved.
                            file_type=file_type
                        )
                        db.session.add(attachment)
                        uploaded_files_info.append({'name': filename, 'path': file_path})
                    except Exception as e:
                        current_app.logger.error(f"Error saving file {filename} for auction history {history_entry.id}: {e}")
                        # Potentially delete already saved files for this entry if one fails? Or mark entry as partial?
                        # For now, continue and let overall transaction rollback.
                        raise # Re-raise to trigger overall rollback

        db.session.commit()
        current_app.logger.info(f"Auction update added for auction {auction_id} (History ID: {history_entry.id}) by user {current_user.id}")
        return jsonify({
            'message': 'Auction update added successfully', 
            'history_id': history_entry.id,
            'attachments_uploaded': uploaded_files_info
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding auction update for auction {auction_id}: {e}")
        # Clean up created directory if history_entry was flushed and ID obtained
        if history_entry and history_entry.id:
             auction_attachment_folder_to_clean = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'auction_attachments', str(history_entry.id))
             if os.path.exists(auction_attachment_folder_to_clean):
                try:
                    # Be careful with rmtree, ensure it's the correct directory
                    import shutil
                    shutil.rmtree(auction_attachment_folder_to_clean)
                    current_app.logger.info(f"Cleaned up attachment directory: {auction_attachment_folder_to_clean}")
                except Exception as cleanup_error:
                    current_app.logger.error(f"Error cleaning up attachment directory {auction_attachment_folder_to_clean}: {cleanup_error}")
        return jsonify({'error': f'Failed to add auction update: {str(e)}'}), 500


@user_bp.route('/api/field-visits/<int:visit_id>', methods=['GET'])
@login_required
def get_field_visit(visit_id):
    """Get field visit details by ID"""
    try:
        # Fetch the field visit from the database
        field_visit = FieldVisit.query.get(visit_id)
        
        if not field_visit:
            return jsonify({
                'success': False,
                'message': 'Field visit not found'
            }), 404
        
        # Get staff names
        field_officer_name = 'Unknown'
        supervisor_name = 'N/A'
        
        # Get field officer name
        if field_visit.field_officer_id:
            try:
                field_officer = Staff.query.get(field_visit.field_officer_id)
                if field_officer:
                    field_officer_name = f"{field_officer.first_name} {field_officer.last_name}"
            except Exception as e:
                current_app.logger.error(f"Error fetching field officer: {str(e)}")
        
        # Get supervisor name
        if field_visit.supervisor_id:
            try:
                supervisor = Staff.query.get(field_visit.supervisor_id)
                if supervisor:
                    supervisor_name = f"{supervisor.first_name} {supervisor.last_name}"
            except Exception as e:
                current_app.logger.error(f"Error fetching supervisor: {str(e)}")
        
        # Convert field visit to dictionary
        visit_data = {
            'id': field_visit.id,
            'customer_id': field_visit.customer_id,
            'customer_name': field_visit.customer_name,
            'loan_account_no': field_visit.loan_account_no,
            'field_officer_id': field_visit.field_officer_id,
            'field_officer_name': field_officer_name,
            'supervisor_id': field_visit.supervisor_id,
            'supervisor_name': supervisor_name,
            'visit_date': field_visit.visit_date.strftime('%Y-%m-%d'),
            'visit_time': field_visit.visit_time.strftime('%H:%M'),
            'location': field_visit.location,
            'purpose': field_visit.purpose,
            'priority': field_visit.priority,
            'alternative_contact': field_visit.alternative_contact,
            'notes': field_visit.notes,
            'special_instructions': field_visit.special_instructions,
            'attachment': field_visit.attachment,
            'status': field_visit.status,
            'outstanding_balance': field_visit.outstanding_balance,
            'days_in_arrears': field_visit.days_in_arrears,
            'missed_payments': field_visit.missed_payments,
            'installment_amount': field_visit.installment_amount,
            'created_at': field_visit.created_at.strftime('%Y-%m-%d %H:%M:%S') if field_visit.created_at else None,
            'updated_at': field_visit.updated_at.strftime('%Y-%m-%d %H:%M:%S') if field_visit.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'visit': visit_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching field visit: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching the field visit'
        }), 500


@user_bp.route('/api/field-visits/<int:visit_id>/status', methods=['POST'])
@csrf.exempt
def update_field_visit_status(visit_id):
    try:
        # Get the field visit
        visit = FieldVisit.query.get_or_404(visit_id)
        
        # Get the request data
        data = request.form
        
        # Get the new status
        new_status = data.get('new_status')
        if not new_status:
            return jsonify({'success': False, 'message': 'New status is required'}), 400
        
        # Get the previous status
        previous_status = data.get('previous_status') or visit.status or 'new'
        
        # Get the notes
        notes = data.get('notes', '')
        
        # Begin transaction
        db.session.begin_nested()
        
        # 1. Update the FieldVisit table
        visit.status = new_status
        visit.updated_at = datetime.utcnow()
        db.session.add(visit)  # Explicitly add the updated visit to the session
        
        # Log the update
        current_app.logger.info(f"Updating field visit {visit_id} status from {previous_status} to {new_status}")
        
        # Get the current user ID if available
        current_user_id = current_user.id if current_user.is_authenticated else None
        
        # 2. Create a status history record in FieldVisitStatusHistory table
        status_history = FieldVisitStatusHistory(
            field_visit_id=visit_id,
            previous_status=previous_status,
            new_status=new_status,
            notes=notes,
            created_by=current_user_id,
            created_at=datetime.utcnow()  # Explicitly set creation time
        )
        
        # Add the status history record
        db.session.add(status_history)
        
        # 3. Handle attachment if provided - update FieldVisitAttachment table
        attachment_file = request.files.get('attachment')
        if attachment_file and attachment_file.filename:
            # Create a secure filename
            filename = secure_filename(attachment_file.filename)
            
            # Create the uploads directory if it doesn't exist
            uploads_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'field_visits', str(visit_id))
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(uploads_dir, unique_filename)
            
            # Save the file
            attachment_file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Get file type
            file_type = attachment_file.content_type
            
            # Create attachment record
            attachment = FieldVisitAttachment(
                field_visit_id=visit_id,
                file_name=filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                attachment_type=data.get('attachment_type', 'status_update'),
                description=data.get('description', f"Status update attachment: {new_status}"),
                uploaded_by=current_user_id,
                uploaded_at=datetime.utcnow()  # Explicitly set upload time
            )
            
            # Add the attachment record
            db.session.add(attachment)
            
            # Log the attachment
            current_app.logger.info(f"Added attachment {filename} to field visit {visit_id}")
        
        # Commit the transaction
        db.session.commit()
        
        # Log success
        current_app.logger.info(f"Successfully updated field visit {visit_id} status to {new_status}")
        
        # Return success response with updated data
        return jsonify({
            'success': True, 
            'message': 'Field visit status updated successfully',
            'visit': {
                'id': visit.id,
                'status': new_status,
                'updated_at': visit.updated_at.strftime('%Y-%m-%d %H:%M:%S') if visit.updated_at else None
            }
        })
    except Exception as e:
        # Rollback the transaction if any error occurs
        db.session.rollback()
        
        # Log the error
        current_app.logger.error(f"Error updating field visit status: {str(e)}")
        
        # Return error response
        return jsonify({'success': False, 'message': f"Error updating field visit status: {str(e)}"}), 500


@user_bp.route('/api/field-visits/<int:visit_id>/status-history', methods=['GET'])
@csrf.exempt
def get_field_visit_status_history(visit_id):
    try:
        # Get the field visit
        visit = FieldVisit.query.get_or_404(visit_id)
        
        # Log debugging information
        current_app.logger.info(f"Fetching status history for field visit {visit_id}")
        
        # Get the status history
        history_records = FieldVisitStatusHistory.query.filter_by(field_visit_id=visit_id).order_by(FieldVisitStatusHistory.created_at.desc()).all()
        
        # Log the number of records found
        current_app.logger.info(f"Found {len(history_records)} status history records for field visit {visit_id}")
        
        # Format the history records
        history_data = []
        for record in history_records:
            # Get the staff name if available
            created_by_name = None
            if record.created_by:
                try:
                    staff = Staff.query.get(record.created_by)
                    if staff:
                        created_by_name = f"{staff.first_name} {staff.last_name}"
                except Exception as e:
                    current_app.logger.error(f"Error fetching staff for status history: {str(e)}")
            
            history_data.append({
                'id': record.id,
                'previous_status': record.previous_status,
                'new_status': record.new_status,
                'notes': record.notes,
                'created_by': record.created_by,
                'created_by_name': created_by_name,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else None
            })
        
        return jsonify({
            'success': True,
            'history': history_data
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching field visit status history: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching the field visit status history'
        }), 500


@user_bp.route('/api/field-visits/<int:visit_id>/test-data', methods=['GET'])
@csrf.exempt
def create_test_status_history(visit_id):
    try:
        # Get the field visit
        visit = FieldVisit.query.get_or_404(visit_id)
        
        # Create some test status history records if none exist
        history_count = FieldVisitStatusHistory.query.filter_by(field_visit_id=visit_id).count()
        
        if history_count == 0:
            # Create sample status history records
            statuses = ['scheduled', 'in-progress', 'completed']
            current_status = 'new'
            
            for i, new_status in enumerate(statuses):
                # Create a status history record
                history = FieldVisitStatusHistory(
                    field_visit_id=visit_id,
                    previous_status=current_status,
                    new_status=new_status,
                    notes=f"Test status change to {new_status}",
                    created_by=None,
                    created_at=datetime.utcnow() - timedelta(days=3-i)
                )
                db.session.add(history)
                current_status = new_status
            
            # Commit the changes
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f"Created {len(statuses)} test status history records for field visit {visit_id}"
            })
        else:
            return jsonify({
                'success': True,
                'message': f"Field visit {visit_id} already has {history_count} status history records"
            })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating test status history: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error creating test status history: {str(e)}"
        }), 500

@user_bp.route('/api/field-visits/<int:visit_id>/attachments', methods=['GET', 'POST'])
@csrf.exempt
def field_visit_attachments(visit_id):
    # Handle POST request for uploading attachments
    if request.method == 'POST':
        try:
            # Get the field visit
            visit = FieldVisit.query.get_or_404(visit_id)
            
            # Get form data
            attachment_type = request.form.get('attachment_type')
            description = request.form.get('description')
            
            # Check if file was uploaded
            if 'attachment' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No file uploaded'
                }), 400
            
            file = request.files['attachment']
            if not file or not file.filename:
                return jsonify({
                    'success': False,
                    'message': 'No file selected'
                }), 400
            
            # Generate a unique filename
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = secure_filename(f"{attachment_type or 'document'}_{visit_id}_{timestamp}_{file.filename}")
            
            # Create the directory if it doesn't exist
            upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'field_visit_attachments')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Get file metadata
            file_size = os.path.getsize(file_path)
            file_type = file.content_type if hasattr(file, 'content_type') else ''
            
            # Get the current user ID if available
            current_user_id = current_user.id if current_user.is_authenticated else None
            
            # Create a new attachment record
            attachment = FieldVisitAttachment(
                field_visit_id=visit_id,
                file_name=file.filename,  # Store the original filename
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                attachment_type=attachment_type or 'document',
                description=description or f"Attachment for field visit {visit_id}",
                uploaded_by=current_user_id,
                uploaded_at=datetime.utcnow()
            )
            
            # Add the attachment to the database
            db.session.add(attachment)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Attachment uploaded successfully',
                'attachment': {
                    'id': attachment.id,
                    'file_name': attachment.file_name,
                    'attachment_type': attachment.attachment_type,
                    'description': attachment.description
                }
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error uploading attachment: {str(e)}")
            return jsonify({
                'success': False,
                'message': f"Error uploading attachment: {str(e)}"
            }), 500
    
    # Handle GET request for fetching attachments
    try:
        # Get the field visit
        visit = FieldVisit.query.get_or_404(visit_id)
        
        # Get the attachments
        attachment_records = FieldVisitAttachment.query.filter_by(field_visit_id=visit_id).order_by(FieldVisitAttachment.uploaded_at.desc()).all()
        
        # Format the attachment records
        attachments_data = []
        for record in attachment_records:
            # Get the staff name if available
            uploaded_by_name = None
            if record.uploaded_by:
                try:
                    staff = Staff.query.get(record.uploaded_by)
                    if staff:
                        uploaded_by_name = f"{staff.first_name} {staff.last_name}"
                except Exception as e:
                    current_app.logger.error(f"Error fetching staff for attachment: {str(e)}")
            
            # Generate download URL
            download_url = url_for('user.download_field_visit_attachment', attachment_id=record.id)
            
            attachments_data.append({
                'id': record.id,
                'file_name': record.file_name,
                'file_type': record.file_type,
                'file_size': record.file_size,
                'attachment_type': record.attachment_type,
                'description': record.description,
                'uploaded_by': record.uploaded_by,
                'uploaded_by_name': uploaded_by_name,
                'uploaded_at': record.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if record.uploaded_at else None,
                'download_url': download_url
            })
        
        return jsonify({
            'success': True,
            'attachments': attachments_data
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching field visit attachments: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching the field visit attachments'
        }), 500


@user_bp.route('/api/field-visits/attachments/<int:attachment_id>/download', methods=['GET'])
@csrf.exempt
def download_field_visit_attachment(attachment_id):
    try:
        # Get the attachment
        attachment = FieldVisitAttachment.query.get_or_404(attachment_id)
        
        # Check if file exists
        if not os.path.exists(attachment.file_path):
            return jsonify({
                'success': False,
                'message': 'Attachment file not found'
            }), 404
        
        # Return the file for download
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.file_name,
            mimetype=attachment.file_type or 'application/octet-stream'
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading field visit attachment: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while downloading the attachment'
        }), 500


@user_bp.route('/api/field-visits/<int:visit_id>/report', methods=['POST'])
def submit_field_visit_report(visit_id):
    try:
        # Get the field visit
        visit = FieldVisit.query.get_or_404(visit_id)
        
        # Check if visit is completed
        if visit.status != 'completed':
            return jsonify({
                'success': False, 
                'message': 'Field visit must be marked as completed before submitting a report'
            }), 400
        
        # Get form data
        outcome = request.form.get('outcome')
        amount_collected = request.form.get('amount_collected', 0)
        next_action = request.form.get('next_action')
        notes = request.form.get('notes')
        attachment_type = request.form.get('attachment_type')
        attachment_description = request.form.get('attachment_description')
        
        # Validate required fields
        if not outcome or not next_action or not notes:
            return jsonify({
                'success': False, 
                'message': 'Outcome, next action, and notes are required'
            }), 400
        
        # Convert amount_collected to float if provided
        if amount_collected:
            try:
                amount_collected = float(amount_collected)
            except ValueError:
                amount_collected = 0
        
        # Get the current user ID if available
        current_user_id = current_user.id if current_user.is_authenticated else None
        
        # Format report information for the notes field
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_content = f"=== FIELD VISIT REPORT ({timestamp}) ===\n"
        report_content += f"Outcome: {outcome}\n"
        report_content += f"Amount Collected: ${amount_collected:.2f}\n"
        report_content += f"Next Action: {next_action}\n"
        report_content += f"Details:\n{notes}\n"
        
        # Update the visit notes with the report content
        if visit.notes:
            visit.notes = f"{visit.notes}\n\n{report_content}"
        else:
            visit.notes = report_content
        
        # Handle report attachment if any
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                # Generate a unique filename
                timestamp_str = timestamp.replace(' ', '_').replace(':', '-')
                filename = secure_filename(f"{attachment_type}_{visit_id}_{timestamp_str}_{file.filename}")
                
                # Create the directory if it doesn't exist
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'field_visit_attachments')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save the file
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Get file metadata
                file_size = os.path.getsize(file_path)
                file_type = file.content_type if hasattr(file, 'content_type') else ''
                
                # Create a new attachment record
                attachment = FieldVisitAttachment(
                    field_visit_id=visit.id,
                    file_name=file.filename,  # Store the original filename
                    file_path=file_path,
                    file_type=file_type,
                    file_size=file_size,
                    attachment_type=attachment_type or 'report',
                    description=attachment_description or f"Report attachment for {outcome} outcome",
                    uploaded_by=current_user_id
                )
                
                # Add the attachment to the database
                db.session.add(attachment)
        
        # Save all changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Field visit report submitted successfully'
        })
    except Exception as e:
        current_app.logger.error(f"Error submitting field visit report: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Error submitting field visit report: {str(e)}"}), 500


@user_bp.route('/api/field-visits/<int:visit_id>', methods=['PUT', 'POST'])
@login_required
def update_field_visit(visit_id):
    """Update a field visit"""
    try:
        # Get the field visit
        field_visit = FieldVisit.query.get(visit_id)
        if not field_visit:
            return jsonify({
                'success': False,
                'message': 'Field visit not found'
            }), 404
        
        # Get form data
        data = request.form
        current_app.logger.info(f"Updating field visit {visit_id} with data: {data}")
        
        # Update customer and loan information
        if 'customer_id' in data and data['customer_id']:
            field_visit.customer_id = data['customer_id']
        
        if 'customer_name' in data and data['customer_name']:
            field_visit.customer_name = data['customer_name']
        
        if 'loan_id' in data and data['loan_id']:
            field_visit.loan_id = data['loan_id']
        
        if 'loan_account_no' in data and data['loan_account_no']:
            field_visit.loan_account_no = data['loan_account_no']
        
        # Update loan details
        if 'raw_outstanding_balance' in data and data['raw_outstanding_balance']:
            try:
                field_visit.outstanding_balance = float(data['raw_outstanding_balance'])
            except (ValueError, TypeError):
                current_app.logger.warning(f"Invalid outstanding balance value: {data.get('raw_outstanding_balance')}")
        
        if 'raw_days_in_arrears' in data and data['raw_days_in_arrears']:
            try:
                field_visit.days_in_arrears = int(data['raw_days_in_arrears'])
            except (ValueError, TypeError):
                current_app.logger.warning(f"Invalid days in arrears value: {data.get('raw_days_in_arrears')}")
        
        if 'missed_payments' in data and data['missed_payments']:
            try:
                field_visit.missed_payments = int(data['missed_payments'])
            except (ValueError, TypeError):
                # Calculate based on days in arrears per requirements
                if field_visit.days_in_arrears:
                    field_visit.missed_payments = math.ceil(field_visit.days_in_arrears / 30)
        
        if 'raw_installment_amount' in data and data['raw_installment_amount']:
            try:
                field_visit.installment_amount = float(data['raw_installment_amount'])
            except (ValueError, TypeError):
                # Use outstanding balance as fallback per requirements
                if field_visit.outstanding_balance:
                    field_visit.installment_amount = field_visit.outstanding_balance
        
        # Update visit details
        if 'visit_date' in data and data['visit_date']:
            field_visit.visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d').date()
        
        if 'visit_time' in data and data['visit_time']:
            field_visit.visit_time = datetime.strptime(data['visit_time'], '%H:%M').time()
        
        if 'purpose' in data:
            field_visit.purpose = data['purpose']
        
        if 'priority' in data:
            field_visit.priority = data['priority']
        
        if 'location' in data:
            field_visit.location = data['location']
        
        if 'alternative_contact' in data:
            field_visit.alternative_contact = data['alternative_contact']
        
        if 'notes' in data:
            field_visit.notes = data['notes']
        
        if 'special_instructions' in data:
            field_visit.special_instructions = data['special_instructions']
        
        if 'status' in data:
            field_visit.status = data['status']
        
        # Update staff assignments
        if 'field_officer_id' in data and data['field_officer_id']:
            try:
                field_visit.field_officer_id = int(data['field_officer_id'])
            except (ValueError, TypeError):
                current_app.logger.warning(f"Invalid field officer ID: {data.get('field_officer_id')}")
        
        if 'field_officer_name' in data and data['field_officer_name']:
            field_visit.field_officer_name = data['field_officer_name']
        
        if 'supervisor_id' in data and data['supervisor_id']:
            try:
                field_visit.supervisor_id = int(data['supervisor_id'])
            except (ValueError, TypeError):
                current_app.logger.warning(f"Invalid supervisor ID: {data.get('supervisor_id')}")
        
        if 'supervisor_name' in data and data['supervisor_name']:
            field_visit.supervisor_name = data['supervisor_name']
        
        # Handle file upload if present
        if 'attachment' in request.files and request.files['attachment'].filename:
            file = request.files['attachment']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create a unique filename
                unique_filename = f"visit_{visit_id}_{int(time.time())}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                field_visit.attachment = f"/static/uploads/{unique_filename}"
        
        # Update timestamp
        field_visit.updated_at = datetime.now()
        
        # Save changes
        db.session.commit()
        
        # Log success
        current_app.logger.info(f"Successfully updated field visit {visit_id}")
        
        return jsonify({
            'success': True,
            'message': 'Field visit updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating field visit: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'An error occurred while updating the field visit: {str(e)}'
        }), 500

@user_bp.route('/api/field-visits/create', methods=['POST'])
@login_required
def create_field_visit():
    """Create a new field visit"""
    try:
        # Get form data
        customer_id = request.form.get('customer_id')
        loan_id = request.form.get('loan_id')
        field_officer_id = request.form.get('field_officer_id')
        supervisor_id = request.form.get('supervisor_id')
        visit_date = request.form.get('visit_date')
        visit_time = request.form.get('visit_time')
        location = request.form.get('location')
        purpose = request.form.get('purpose')
        priority = request.form.get('priority')
        notes = request.form.get('notes')
        
        # Get additional form data
        outstanding_balance = request.form.get('outstanding_balance')
        days_in_arrears = request.form.get('days_in_arrears')
        missed_payments = request.form.get('missed_payments')
        installment_amount = request.form.get('installment_amount')
        
        # Log the received data for debugging
        current_app.logger.info(f"Received field visit data: {request.form}")
        
        # Validate required fields
        required_fields = [customer_id, loan_id, field_officer_id, visit_date, visit_time, location, purpose, priority, notes]
        required_field_names = ['customer_id', 'loan_id', 'field_officer_id', 'visit_date', 'visit_time', 'location', 'purpose', 'priority', 'notes']
        
        if not all(required_fields):
            missing_fields = [field_name for field_name, value in zip(required_field_names, required_fields) if not value]
            current_app.logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({
                "success": False,
                "error": "Missing required fields", 
                "missing_fields": missing_fields
            }), 400
            
        # Validate ID fields specifically
        id_fields = [
            ('customer_id', customer_id),
            ('loan_id', loan_id),
            ('field_officer_id', field_officer_id)
        ]
        
        invalid_ids = []
        for field_name, field_value in id_fields:
            if not field_value or not field_value.strip():
                invalid_ids.append(field_name)
                continue
                
            # Check if value can be converted to integer
            try:
                int(field_value)
            except ValueError:
                invalid_ids.append(field_name)
                
        if invalid_ids:
            current_app.logger.error(f"Invalid ID fields: {invalid_ids}")
            return jsonify({
                "success": False,
                "error": "Invalid ID values provided", 
                "missing_fields": invalid_ids
            }), 400
        
        # Process file attachment if provided
        attachment = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                # Here you would save the file and get the file path
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                
                # Create upload directory if it doesn't exist
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                    
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                attachment = f'/static/uploads/{filename}'  # Store relative path
                current_app.logger.info(f"File saved to {file_path}")
        
        # Get customer name and loan account number from the form
        customer_name = request.form.get('customer_name', 'Unknown Customer')
        loan_account_no = request.form.get('loan_account_no', 'Unknown Loan')
        alternative_contact = request.form.get('alternative_contact')
        special_instructions = request.form.get('special_instructions')
        
        # Use raw numeric values instead of formatted ones with commas
        raw_outstanding_balance = request.form.get('raw_outstanding_balance')
        raw_installment_amount = request.form.get('raw_installment_amount')
        
        # Convert values to appropriate types
        try:
            outstanding_balance = float(raw_outstanding_balance) if raw_outstanding_balance else 0
            days_in_arrears = int(days_in_arrears) if days_in_arrears else 0
            missed_payments = int(missed_payments) if missed_payments else 0
            installment_amount = float(raw_installment_amount) if raw_installment_amount else 0
        except (ValueError, TypeError) as e:
            current_app.logger.error(f"Error converting field visit values: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid numeric values provided'
            }), 400
            
        # FieldVisit model is imported at the top of the file
        
        # Handle current user ID
        current_user_id = 1  # Default value
        if hasattr(current_user, 'id'):
            current_user_id = current_user.id
            
        # Validate that IDs can be converted to integers
        try:
            # The frontend should now be sending these as integers already
            field_officer_id_int = int(field_officer_id)
            supervisor_id_int = int(supervisor_id) if supervisor_id and supervisor_id.strip() else None
            
            # These are still strings in the database
            customer_id_str = customer_id
            loan_id_str = loan_id
            
            # Use a default branch ID
            branch_id_int = int(request.form.get('assigned_branch_id', 1))
            
            # Log the IDs for debugging
            current_app.logger.info(f"Field visit data: field_officer_id={field_officer_id_int}, supervisor_id={supervisor_id_int}, branch_id={branch_id_int}")
        except ValueError as e:
            current_app.logger.error(f"Error converting ID to integer: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid ID format provided. All ID fields must contain valid numeric values.'
            }), 400
            
        # Create new field visit record
        field_visit = FieldVisit(
            # External references - stored as strings
            customer_id=customer_id_str,
            customer_name=customer_name,
            loan_account_no=loan_account_no,
            
            # Staff assignments - using integer IDs
            field_officer_id=field_officer_id_int,
            supervisor_id=supervisor_id_int,
            assigned_branch_id=branch_id_int,
            created_by=current_user.id if hasattr(current_user, 'id') else 1,
            
            # Visit details
            visit_date=datetime.strptime(visit_date, '%Y-%m-%d').date(),
            visit_time=datetime.strptime(visit_time, '%H:%M').time(),
            location=location,
            purpose=purpose,
            priority=priority,
            
            # Loan details
            outstanding_balance=outstanding_balance,
            days_in_arrears=days_in_arrears,
            missed_payments=missed_payments,
            installment_amount=installment_amount,
            
            # Additional information
            alternative_contact=alternative_contact,
            notes=notes,
            special_instructions=special_instructions,
            attachment=attachment,
            status='scheduled'
        )
        
        # Save to database
        try:
            db.session.add(field_visit)
            db.session.commit()
            current_app.logger.info(f"Field visit saved to database with ID: {field_visit.id}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error saving field visit: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Database error: {str(e)}'
            }), 500
        
        # Log the field visit creation
        current_app.logger.info(f"Field visit scheduled for customer {customer_id}, loan {loan_id}, by officer {field_officer_id}")
        
        # For now, just return success
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Field visit scheduled successfully'
            })
        else:
            flash('Field visit scheduled successfully', 'success')
            return redirect(url_for('user.field_visits'))
        
    except Exception as e:
        current_app.logger.error(f"Error creating field visit: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'An error occurred while scheduling the field visit'
            }), 500
        else:
            flash('An error occurred while scheduling the field visit', 'error')
            return redirect(url_for('user.field_visits'))

@user_bp.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    """Get all customers for field visit form"""
    try:
        # Get search term if provided
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Log request parameters for debugging
        current_app.logger.info(f"Customer search request: search='{search}', page={page}, limit={limit}")
        
        # This would be replaced with actual database query
        # Example: 
        # if search:
        #     customers = Customer.query.filter(Customer.name.ilike(f'%{search}%')).paginate(page=page, per_page=limit)
        # else:
        #     customers = Customer.query.paginate(page=page, per_page=limit)
        
        # For now, return sample data with loans
        customers = [
            {
                "id": 1, 
                "name": "Alice Cooper",
                "loans": [
                    {"id": 101, "loan_number": "LN-2025-005", "amount": 50000, "days_in_arrears": 45, "outstanding_balance": 35000, "installment_amount": 1500},
                    {"id": 102, "loan_number": "LN-2025-012", "amount": 75000, "days_in_arrears": 15, "outstanding_balance": 65000, "installment_amount": 2000}
                ]
            },
            {
                "id": 2, 
                "name": "Bob Smith",
                "loans": [
                    {"id": 201, "loan_number": "LN-2025-018", "amount": 30000, "days_in_arrears": 60, "outstanding_balance": 28000, "installment_amount": 1000}
                ]
            },
            {
                "id": 3, 
                "name": "Charlie Brown",
                "loans": [
                    {"id": 301, "loan_number": "LN-2025-023", "amount": 100000, "days_in_arrears": 90, "outstanding_balance": 95000, "installment_amount": 3000},
                    {"id": 302, "loan_number": "LN-2025-024", "amount": 25000, "days_in_arrears": 0, "outstanding_balance": 20000, "installment_amount": 800}
                ]
            },
            {
                "id": 4, 
                "name": "David Jones",
                "loans": [
                    {"id": 401, "loan_number": "LN-2025-030", "amount": 45000, "days_in_arrears": 30, "outstanding_balance": 40000, "installment_amount": 1200}
                ]
            }
        ]
        
        # Filter by search term if provided
        if search:
            customers = [c for c in customers if search.lower() in c['name'].lower()]
        
        # Calculate missed payments based on days in arrears (1 per 30 days)
        for customer in customers:
            for loan in customer['loans']:
                # Calculate missed installments based on days in arrears
                loan['missed_payments'] = max(1, int((loan['days_in_arrears'] + 29) / 30))  # Round up division
        
        # Log the response for debugging
        response_data = {"customers": customers}
        current_app.logger.info(f"Customer search response: {len(customers)} customers found")
        
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"Error fetching customers: {str(e)}")
        return jsonify({"error": "Failed to fetch customers"}), 500

@user_bp.route('/api/customers/<int:customer_id>/loans', methods=['GET'])
@login_required
def get_customer_loans(customer_id):
    """Get loans for a specific customer"""
    try:
        # This would be replaced with actual database query
        # Example: loans = Loan.query.filter_by(customer_id=customer_id).all()
        
        # For now, return sample data
        loans = []
        if customer_id == 1:
            loans = [
                {"id": 101, "loan_number": "LN-2025-005", "amount": 50000, "days_in_arrears": 45, "outstanding_balance": 35000, "installment_amount": 1500},
                {"id": 102, "loan_number": "LN-2025-012", "amount": 75000, "days_in_arrears": 15, "outstanding_balance": 65000, "installment_amount": 2000}
            ]
        elif customer_id == 2:
            loans = [
                {"id": 201, "loan_number": "LN-2025-018", "amount": 30000, "days_in_arrears": 60, "outstanding_balance": 28000, "installment_amount": 1000}
            ]
        elif customer_id == 3:
            loans = [
                {"id": 301, "loan_number": "LN-2025-023", "amount": 100000, "days_in_arrears": 90, "outstanding_balance": 95000, "installment_amount": 3000},
                {"id": 302, "loan_number": "LN-2025-024", "amount": 25000, "days_in_arrears": 0, "outstanding_balance": 20000, "installment_amount": 800}
            ]
        elif customer_id == 4:
            loans = [
                {"id": 401, "loan_number": "LN-2025-030", "amount": 45000, "days_in_arrears": 30, "outstanding_balance": 40000, "installment_amount": 1200}
            ]
        
        # Calculate missed payments based on days in arrears (1 per 30 days)
        for loan in loans:
            # Calculate missed installments based on days in arrears
            loan['missed_payments'] = max(1, int((loan['days_in_arrears'] + 29) / 30))  # Round up division
        
        return jsonify({"loans": loans})
    except Exception as e:
        current_app.logger.error(f"Error fetching loans for customer {customer_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch loans"}), 500

@user_bp.route('/api/field-officers', methods=['GET'])
@login_required
def get_field_officers():
    """Get all field officers"""
    try:
        # Get search term if provided
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Log request parameters for debugging
        current_app.logger.info(f"Field officer search request: search='{search}', page={page}, limit={limit}")
        
        # This would be replaced with actual database query
        # Example: 
        # if search:
        #     officers = User.query.filter(User.role=='field_officer', User.name.ilike(f'%{search}%')).paginate(page=page, per_page=limit)
        # else:
        #     officers = User.query.filter_by(role='field_officer').paginate(page=page, per_page=limit)
        
        # For now, return sample data
        officers = [
            {"id": 101, "name": "John Doe", "text": "John Doe"},
            {"id": 102, "name": "Jane Smith", "text": "Jane Smith"},
            {"id": 103, "name": "Mike Johnson", "text": "Mike Johnson"},
            {"id": 104, "name": "Sarah Williams", "text": "Sarah Williams"}
        ]
        
        # Filter by search term if provided
        if search:
            officers = [o for o in officers if search.lower() in o['name'].lower()]
        
        # Format response for Select2
        results = {
            "results": officers,
            "pagination": {
                "more": False  # No more pages
            }
        }
        
        # Log the response for debugging
        current_app.logger.info(f"Field officer search response: {len(officers)} officers found")
        current_app.logger.info(f"Response data: {results}")
        
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error fetching field officers: {str(e)}")
        return jsonify({"error": "Failed to fetch field officers"}), 500

@user_bp.route('/api/supervisors', methods=['GET'])
@login_required
def get_supervisors():
    """Get all supervisors"""
    try:
        # Get search term if provided
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Log request parameters for debugging
        current_app.logger.info(f"Supervisor search request: search='{search}', page={page}, limit={limit}")
        
        # This would be replaced with actual database query
        # Example: 
        # if search:
        #     supervisors = User.query.filter(User.role=='supervisor', User.name.ilike(f'%{search}%')).paginate(page=page, per_page=limit)
        # else:
        #     supervisors = User.query.filter_by(role='supervisor').paginate(page=page, per_page=limit)
        
        # For now, return sample data
        supervisors = [
            {"id": 201, "name": "Robert Chen", "text": "Robert Chen"},
            {"id": 202, "name": "Emily Davis", "text": "Emily Davis"},
            {"id": 203, "name": "James Wilson", "text": "James Wilson"},
            {"id": 204, "name": "Patricia Moore", "text": "Patricia Moore"}
        ]
        
        # Filter by search term if provided
        if search:
            supervisors = [s for s in supervisors if search.lower() in s['name'].lower()]
        
        # Format response for Select2
        results = {
            "results": supervisors,
            "pagination": {
                "more": False  # No more pages
            }
        }
        
        # Log the response for debugging
        current_app.logger.info(f"Supervisor search response: {len(supervisors)} supervisors found")
        current_app.logger.info(f"Response data: {results}")
        
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error fetching supervisors: {str(e)}")
        return jsonify({"error": "Failed to fetch supervisors"}), 500

# Add the new API routes that match the collection schedule implementation
@user_bp.route('/api/customers/search', methods=['GET'])
@login_required
def search_customers():
    """Search customers for Select2 dropdown"""
    try:
        # Get search term if provided
        search = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Log request parameters for debugging
        current_app.logger.info(f"Customer search request: q='{search}', page={page}, per_page={per_page}")
        
        # Get customers with loans and guarantors from core banking system
        customers = []
        
        # Define module IDs
        loans_module_id = 1  # Module ID for loans
        guarantors_module_id = 11  # Module ID for guarantors
        
        try:
            # Get the active core banking system
            core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
            if not core_system:
                current_app.logger.error("No active core banking system configured")
                return jsonify({"items": [], "has_more": False})
            
            # Get authentication credentials
            try:
                auth_credentials = core_system.auth_credentials_dict
            except (json.JSONDecodeError, TypeError) as e:
                current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
                auth_credentials = {'username': 'root', 'password': ''}
            
            # Set up database connection configuration
            core_banking_config = {
                'host': core_system.base_url,
                'port': core_system.port or 3306,
                'user': auth_credentials.get('username', 'root'),
                'password': auth_credentials.get('password', ''),
                'database': core_system.database_name,
                'auth_plugin': 'mysql_native_password'
            }
            
            # Connect to the core banking system database
            conn = mysql.connector.connect(**core_banking_config)
            cursor = conn.cursor(dictionary=True)
            
            # Function to get mapping for a module
            def get_mapping_for_module(module_id):
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    # Retrieve expected and actual columns as lists
                    expected_columns = expected.columns
                    actual_columns = actual.columns
                    
                    # Create a dictionary mapping expected to actual columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict
                    }
                return mapping
            
            # Get loans mapping
            loans_mapping = get_mapping_for_module(loans_module_id)
            loans_table = loans_mapping.get('Loans', {}).get('actual_table_name')
            loans_columns = loans_mapping.get('Loans', {}).get('columns', {})
            
            # Get guarantors mapping
            guarantors_mapping = get_mapping_for_module(guarantors_module_id)
            guarantors_table = guarantors_mapping.get('Guarantors', {}).get('actual_table_name')
            guarantors_columns = guarantors_mapping.get('Guarantors', {}).get('columns', {})
            
                        # Build query to get customers with loans
            if loans_table and loans_columns:
                # Log the loans mapping
                current_app.logger.info(f"Loans columns mapping: {loans_columns}")
                
                # Define required customer fields
                required_fields = {
                    'MemberID': 'member_id',
                    'FirstName': 'first_name',
                    'LastName': 'last_name',
                    'NationalID': 'national_id',
                    'DateOfBirth': 'date_of_birth',
                    'Gender': 'gender',
                    'PhoneNumber': 'phone_number',
                    'Email': 'email'
                }
                
                # Build SELECT clause for customer fields
                select_clause = []
                for expected_col, default_col in required_fields.items():
                    actual_col = loans_columns.get(expected_col, default_col)
                    select_clause.append(f"{actual_col} AS {expected_col}")
                    current_app.logger.info(f"Mapping {expected_col} to {actual_col}")
                
                # Add loan-specific fields
                loan_fields = ['LoanAppID', 'LoanNo', 'LoanAmount', 'DaysInArrears', 'OutstandingBalance', 'InstallmentAmount']
                for field in loan_fields:
                    if field in loans_columns:
                        select_clause.append(f"{loans_columns[field]} AS {field}")
                        current_app.logger.info(f"Adding loan field {field} -> {loans_columns[field]}")
                
                select_sql = ", ".join(select_clause)
                
                # Add search condition if provided
                where_clause = ""
                if search:
                    search_conditions = []
                    search_fields = ['FirstName', 'LastName', 'NationalID', 'PhoneNumber', 'Email']
                    for field in search_fields:
                        if field in loans_columns:
                            search_conditions.append(f"{loans_columns[field]} LIKE '%{search}%'")
                    if search_conditions:
                        where_clause = "WHERE " + " OR ".join(search_conditions)
                
                # Build the complete query with limit for pagination
                offset = (page - 1) * per_page
                query = f"SELECT {select_sql} FROM {loans_table} {where_clause} LIMIT {per_page} OFFSET {offset}"
                
                # Log the final query
                current_app.logger.info(f"Final SQL query: {query}")
                
                # Execute the query
                cursor.execute(query)
                loans_data = cursor.fetchall()
                
                # Log the fetched data
                current_app.logger.info(f"Fetched loan data: {loans_data}")
                
                # Process loans data to group by customer
                customer_loans = {}
                for loan in loans_data:
                    # Log raw loan data for debugging
                    current_app.logger.info(f"Processing loan row: {loan}")
                    
                    # Get customer ID from loan data
                    customer_id = str(loan.get('CustomerID', loan.get('MemberNo', '')))
                    
                    # Create customer name from FirstName and LastName
                    first_name = loan.get('FirstName', '')
                    last_name = loan.get('LastName', '')
                    customer_name = f"{first_name} {last_name}".strip()
                    
                    # Add customer if not already in the dictionary
                    if customer_id not in customer_loans:
                        # Create customer data dictionary with all fields
                        customer_data = {
                            'id': customer_id,
                            'text': customer_name,
                            'NationalID': str(loan.get('NationalID', '')),
                            'DateOfBirth': str(loan.get('DateOfBirth', '')),
                            'Gender': str(loan.get('Gender', '')),
                            'PhoneNumber': str(loan.get('PhoneNumber', '')),
                            'Email': str(loan.get('Email', '')),
                            'loans': []
                        }
                        
                        # Log customer data for debugging
                        current_app.logger.info(f"Adding new customer: {customer_data}")
                        
                        customer_loans[customer_id] = customer_data
                    
                    # Add loan to customer's loans
                    loan_data = {
                        'LoanAppID': str(loan.get('LoanAppID', '')),
                        'LoanNo': str(loan.get('LoanNo', '')),
                        'LoanAmount': float(loan.get('LoanAmount', 0) or 0),
                        'DaysInArrears': int(loan.get('DaysInArrears', 0) or 0),
                        'OutstandingBalance': float(loan.get('OutstandingBalance', 0) or 0),
                        'InstallmentAmount': float(loan.get('InstallmentAmount', 0) or 0)
                    }
                    
                    # Log loan data for debugging
                    current_app.logger.info(f"Adding loan to customer {customer_id}: {loan_data}")
                    customer_loans[customer_id]['loans'].append(loan_data)
                
                # Now get guarantors for these loans
                if guarantors_table and guarantors_columns:
                    # Build SELECT clause for guarantors
                    guarantor_select_clause = []
                    for expected_col, actual_col in guarantors_columns.items():
                        guarantor_select_clause.append(f"{actual_col} AS {expected_col}")
                    
                    guarantor_select_sql = ", ".join(guarantor_select_clause)
                    
                    # Get loan IDs to filter guarantors
                    loan_ids = []
                    for customer in customer_loans.values():
                        for loan in customer['loans']:
                            if loan.get('LoanAppID'):
                                loan_ids.append(str(loan['LoanAppID']))
                    
                    if loan_ids:
                        # Build query to get guarantors for these loans
                        loan_app_id_col = guarantors_columns.get('LoanAppID', 'loan_app_id')
                        guarantor_query = f"SELECT {guarantor_select_sql} FROM {guarantors_table} WHERE {loan_app_id_col} IN ({','.join(loan_ids)})"
                        
                        # Execute the query
                        cursor.execute(guarantor_query)
                        guarantors_data = cursor.fetchall()
                        
                        # Add guarantors to respective customers
                        for guarantor in guarantors_data:
                            loan_app_id = guarantor.get('LoanAppID')
                            if not loan_app_id:
                                continue
                            
                            # Format guarantor name
                            guarantor_first_name = guarantor.get('FirstName', '')
                            guarantor_middle_name = guarantor.get('MiddleName', '')
                            guarantor_last_name = guarantor.get('LastName', '')
                            guarantor['GuarantorName'] = f"{guarantor_first_name} {guarantor_middle_name or ''} {guarantor_last_name}".strip()
                            
                            # Add guarantor to each customer that has this loan
                            for customer in customer_loans.values():
                                for loan in customer['loans']:
                                    if loan.get('LoanAppID') == loan_app_id:
                                        if 'guarantors' not in customer:
                                            customer['guarantors'] = []
                                        customer['guarantors'].append(guarantor)
                
                # Convert dictionary to list for the response
                customers = list(customer_loans.values())
            
            # Close database connections
            cursor.close()
            conn.close()
            
        except Exception as e:
            current_app.logger.error(f"Error fetching customers with loans and guarantors: {str(e)}")
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
                
            # Fallback to sample data if there's an error
            customers = [
                {
                    "id": 1, 
                    "text": "Alice Cooper",
                    "loans": [
                        {"LoanAppID": 101, "LoanNo": "LN-2025-005", "LoanAmount": 50000, "DaysInArrears": 45, "OutstandingBalance": 35000, "InstallmentAmount": 1500}
                    ],
                    "guarantors": [
                        {"GuarantorID": 1001, "GuarantorName": "John Doe", "LoanAppID": 101, "GuaranteedAmount": 25000, "Status": "Active"}
                    ]
                },
                {
                    "id": 2, 
                    "text": "Bob Smith",
                    "loans": [
                        {"LoanAppID": 201, "LoanNo": "LN-2025-018", "LoanAmount": 30000, "DaysInArrears": 60, "OutstandingBalance": 28000, "InstallmentAmount": 1000}
                    ],
                    "guarantors": [
                        {"GuarantorID": 2001, "GuarantorName": "Jane Smith", "LoanAppID": 201, "GuaranteedAmount": 15000, "Status": "Active"}
                    ]
                }
            ]
        
        # Filter by search term if provided
        if search:
            customers = [c for c in customers if search.lower() in c['text'].lower()]
        
        # Log the customer data before formatting response
        current_app.logger.info(f"Raw customer data before response: {customers}")
        
        # Format response for Select2
        response = {
            "items": customers,
            "has_more": False  # No more pages
        }
        
        # Log the response for debugging
        current_app.logger.info(f"Customer search response: {len(customers)} customers found")
        current_app.logger.info(f"Final response data: {response}")
        
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Error searching customers: {str(e)}")
        return jsonify({"error": "Failed to search customers"}), 500

@user_bp.route('/api/guarantors/by-loan', methods=['GET'])
@login_required
def get_guarantors_by_loan():
    """Get guarantors for a specific loan"""
    try:
        # Get loan ID from request
        loan_id = request.args.get('loan_id')
        if not loan_id:
            return jsonify({"error": "Loan ID is required"}), 400
            
        current_app.logger.info(f"Fetching guarantors for loan ID: {loan_id}")
        
        # Define module ID for guarantors
        module_id = 11
        
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({"error": "No active core banking system configured"}), 500
            
        # Get authentication credentials
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}
            
        # Set up database connection configuration
        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }
        
        # Connect to the core banking system database
        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get the mapping data for guarantors
        expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
        mapping = {}
        for expected in expected_mappings:
            actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
            if not actual:
                continue
                
            # Retrieve expected and actual columns as lists
            expected_columns = expected.columns
            actual_columns = actual.columns
                
            # Create a dictionary mapping expected to actual columns
            columns_dict = dict(zip(expected_columns, actual_columns))
                
            mapping[expected.table_name] = {
                "actual_table_name": actual.table_name,
                "columns": columns_dict
            }
            
        # Get guarantors table mapping
        guarantors_mapping = mapping.get('Guarantors', {})
        if not guarantors_mapping:
            return jsonify({"error": "Guarantors table mapping not found"}), 500
            
        guarantors_table = guarantors_mapping.get('actual_table_name')
        columns_mapping = guarantors_mapping.get('columns', {})
        
        # Check if we have Members table mapping
        members_mapping = mapping.get('Members', {})
        members_table = members_mapping.get('actual_table_name') if members_mapping else None
        members_columns = members_mapping.get('columns', {}) if members_mapping else {}
        
        # Build SELECT clause for guarantors
        select_clause = []
        for expected_col, actual_col in columns_mapping.items():
            select_clause.append(f"{guarantors_table}.{actual_col} AS {expected_col}")
        
        # Add member name fields if available
        if members_table and members_columns:
            # Add member name fields to select clause
            member_name_fields = ['FirstName', 'MiddleName', 'LastName', 'MemberName', 'Name']
            for field in member_name_fields:
                if field in members_columns:
                    select_clause.append(f"{members_table}.{members_columns[field]} AS Member{field}")
        
        select_sql = ", ".join(select_clause)
        
        # Get loan app ID column and member ID columns
        loan_app_id_col = columns_mapping.get('LoanAppID', 'loan_app_id')
        guarantor_member_id_col = columns_mapping.get('GuarantorMemberID', 'guarantor_member_id')
        member_id_col = members_columns.get('MemberID', 'member_id') if members_columns else None
        
        # Build the query with JOIN if members table is available
        if members_table and member_id_col and guarantor_member_id_col:
            query = f"SELECT {select_sql} FROM {guarantors_table} "
            query += f"LEFT JOIN {members_table} ON {guarantors_table}.{guarantor_member_id_col} = {members_table}.{member_id_col} "
            query += f"WHERE {guarantors_table}.{loan_app_id_col} = %s"
        else:
            # Fallback to simple query without join
            query = f"SELECT {select_sql} FROM {guarantors_table} WHERE {loan_app_id_col} = %s"
        
        # Execute the query
        cursor.execute(query, (loan_id,))
        guarantors = cursor.fetchall()
        
        # Format guarantor names
        for guarantor in guarantors:
            # First try to use Member name fields from the join
            if 'MemberFirstName' in guarantor or 'MemberLastName' in guarantor:
                # Format guarantor name from member components
                first_name = guarantor.get('MemberFirstName', '')
                middle_name = guarantor.get('MemberMiddleName', '')
                last_name = guarantor.get('MemberLastName', '')
                guarantor['GuarantorName'] = f"{first_name} {middle_name or ''} {last_name}".strip()
            # Then try MemberName field
            elif 'MemberName' in guarantor and guarantor['MemberName']:
                guarantor['GuarantorName'] = guarantor['MemberName']
            # Then try guarantor name components
            elif 'FirstName' in guarantor or 'LastName' in guarantor:
                # Format guarantor name from components
                first_name = guarantor.get('FirstName', '')
                middle_name = guarantor.get('MiddleName', '')
                last_name = guarantor.get('LastName', '')
                guarantor['GuarantorName'] = f"{first_name} {middle_name or ''} {last_name}".strip()
            else:
                # Try to get name from other fields
                for name_field in ['GuarantorName', 'Name']:
                    if name_field in guarantor and guarantor[name_field]:
                        guarantor['GuarantorName'] = guarantor[name_field]
                        break
            
            # If still no name, fetch from database using member ID
            if not guarantor.get('GuarantorName') or not guarantor['GuarantorName'].strip():
                member_id = guarantor.get('GuarantorMemberID')
                if member_id:
                    try:
                        # Try to get member from local database
                        member = Client.query.filter_by(member_no=str(member_id)).first()
                        if member:
                            guarantor['GuarantorName'] = f"{member.first_name or ''} {member.middle_name or ''} {member.last_name or ''}".strip()
                            current_app.logger.info(f"Found member name from database: {guarantor['GuarantorName']}")
                    except Exception as e:
                        current_app.logger.error(f"Error fetching member data: {str(e)}")
                        
            # Last resort fallback - use Member ID
            if not guarantor.get('GuarantorName') or not guarantor['GuarantorName'].strip():
                member_id = guarantor.get('GuarantorMemberID', guarantor.get('MemberID', ''))
                guarantor['GuarantorName'] = f"Member {member_id}" if member_id else "Unknown Guarantor"
            
            # Format amounts
            if 'GuaranteedAmount' in guarantor and guarantor['GuaranteedAmount']:
                guarantor['FormattedAmount'] = f"{float(guarantor['GuaranteedAmount']):,.2f}"
        
        cursor.close()
        conn.close()
        
        return jsonify({"guarantors": guarantors})
        
    except Exception as e:
        current_app.logger.error(f"Error fetching guarantors for loan: {str(e)}")
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
        return jsonify({"error": f"Failed to fetch guarantors: {str(e)}"}), 500

@user_bp.route('/api/staff/search', methods=['GET'])
def search_staff():
    # Get actual staff from the database
    query = request.args.get('q', '')
    role = request.args.get('role', '')
    page = int(request.args.get('page', 1))
    
    try:
        # Query the database for actual staff members
        staff_list = Staff.query.filter(Staff.is_active == True).all()
        
        # Format staff data for Select2
        items = []
        for staff in staff_list:
            # Only include staff that match the role filter if specified
            if not role or (hasattr(staff, 'role') and staff.role and role.lower() in staff.role.name.lower()):
                items.append({
                    'id': str(staff.id),  # Convert ID to string for Select2
                    'text': f"{staff.first_name} {staff.last_name}"
                })
        
        # Return formatted response for Select2
        return jsonify({
            'items': items,
            'has_more': False  # No pagination for now
        })
    except Exception as e:
        current_app.logger.error(f"Error searching staff: {str(e)}")
        # Fallback to sample data with valid staff IDs from the database
        return jsonify({
            'items': [
                {'id': '1', 'text': 'Admin User'},
                {'id': '2', 'text': 'John Doe'},
                {'id': '3', 'text': 'Alice Johnson'},
                {'id': '4', 'text': 'Emily Davis'},
                {'id': '5', 'text': 'Michael Brown'},
                {'id': '6', 'text': 'Sarah Wilson'}
            ],
            'has_more': False
        })
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
    # Get any status updates from the session
    claim_status_updates = session.get('claim_status_updates', {})
    
    return render_with_modules('user/reports/guarantor_claims.html', claim_status_updates=claim_status_updates)

@user_bp.route('/api/reports/guarantor-claims/data', methods=['POST'])
@login_required
def get_guarantor_claims_data():
    filters = request.get_json()
    
    # Sample data based on the actual database structure
    claims = [
        {
            'id': '1',
            'loan_id': '5',
            'loan_no': 'L005/2023',
            'borrower_id': '5',
            'borrower_name': 'Michael Kiprop',
            'guarantor_id': '6',
            'guarantor_name': 'Samuel Kimani',
            'claim_amount': 200000,
            'claim_date': '2025-01-16 15:33:25',
            'status': 'Pending',
            'notes': '',
            'document_path': 'uploads/claims/AccountOpeningForm_801033.pdf',
            'created_by': '1',
            'created_at': '2025-01-16 15:33:25'
        },
        {
            'id': '2',
            'loan_id': '1',
            'loan_no': 'L001/2023',
            'borrower_id': '1',
            'borrower_name': 'Samuel Kimani',
            'guarantor_id': '1',
            'guarantor_name': 'Elizabeth Njeri',
            'claim_amount': 100000,
            'claim_date': '2025-04-23 12:59:48',
            'status': 'Pending',
            'notes': '',
            'document_path': 'uploads/claims/sample_1.pdf',
            'created_by': '1',
            'created_at': '2025-04-23 12:59:48'
        }
    ]
    
    # Apply status updates from session if available
    status_updates = session.get('claim_status_updates', {})
    for claim in claims:
        claim_id = claim['id']
        if claim_id in status_updates:
            claim['status'] = status_updates[claim_id]['status']
    
    # Calculate statistics based on current data (including session updates)
    statistics = calculate_claim_statistics(claims)
    
    # Pagination logic
    page = int(filters.get('page', 1))
    items_per_page = 10
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_claims = claims[start_idx:end_idx]
    
    data = {
        'items': paginated_claims,
        'statistics': statistics,
        'pagination': {
            'page': page,
            'start': start_idx + 1 if paginated_claims else 0,
            'end': start_idx + len(paginated_claims),
            'total': len(claims),
            'totalPages': (len(claims) + items_per_page - 1) // items_per_page
        }
    }
    
    return jsonify(data)

@user_bp.route('/api/reports/guarantor-claims/statistics', methods=['GET'])
@login_required
def get_guarantor_claims_statistics():
    # Sample data based on the actual database structure
    claims = [
        {
            'id': '1',
            'loan_id': '5',
            'loan_no': 'L005/2023',
            'borrower_id': '5',
            'borrower_name': 'Michael Kiprop',
            'guarantor_id': '6',
            'guarantor_name': 'Samuel Kimani',
            'claim_amount': 200000,
            'claim_date': '2025-01-16 15:33:25',
            'status': 'Pending',
            'notes': '',
            'document_path': 'uploads/claims/AccountOpeningForm_801033.pdf',
            'created_by': '1',
            'created_at': '2025-01-16 15:33:25'
        },
        {
            'id': '2',
            'loan_id': '1',
            'loan_no': 'L001/2023',
            'borrower_id': '1',
            'borrower_name': 'Samuel Kimani',
            'guarantor_id': '1',
            'guarantor_name': 'Elizabeth Njeri',
            'claim_amount': 100000,
            'claim_date': '2025-04-23 12:59:48',
            'status': 'Pending',
            'notes': '',
            'document_path': 'uploads/claims/sample_1.pdf',
            'created_by': '1',
            'created_at': '2025-04-23 12:59:48'
        }
    ]
    
    # Log the session data for debugging
    status_updates = session.get('claim_status_updates', {})
    current_app.logger.info(f"Session status updates: {status_updates}")
    
    # Apply status updates from session if available
    for claim in claims:
        claim_id = claim['id']
        if claim_id in status_updates:
            original_status = claim['status']
            claim['status'] = status_updates[claim_id]['status']
            current_app.logger.info(f"Updated claim {claim_id} status from {original_status} to {claim['status']}")
    
    # Calculate statistics based on current data (including session updates)
    statistics = calculate_claim_statistics(claims)
    
    return jsonify(statistics)

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


# Helper function to calculate claim statistics
def calculate_claim_statistics(claims):
    # Initialize counters
    total = len(claims)
    pending = 0
    approved = 0
    rejected = 0
    pending_amount = 0
    approved_amount = 0
    
    # Debug information
    current_app.logger.info(f"Calculating statistics for {len(claims)} claims")
    
    # Count claims by status and sum amounts
    for claim in claims:
        # Handle case-insensitive status comparison
        status = claim['status'].lower() if isinstance(claim['status'], str) else ''
        current_app.logger.info(f"Claim {claim['id']} has status: {status}")
        
        # Handle claim amount - could be string with commas or numeric
        if 'claim_amount' in claim:
            amount_str = str(claim['claim_amount']).replace(',', '')
            try:
                amount = float(amount_str)
            except ValueError:
                amount = 0
        else:
            amount = 0
        
        # Print the exact status for debugging
        current_app.logger.info(f"Exact status for claim {claim['id']}: '{claim['status']}'")
        
        # Use case-insensitive comparison to be safe
        if status in ['pending', 'pendiente']:
            pending += 1
            pending_amount += amount
            current_app.logger.info(f"Added to pending: {claim['id']} with amount {amount}")
        elif status in ['approved', 'aprobado', 'aprovado']:
            approved += 1
            approved_amount += amount
            current_app.logger.info(f"Added to approved: {claim['id']} with amount {amount}")
        elif status == 'rejected':
            rejected += 1
            current_app.logger.info(f"Added to rejected: {claim['id']}")
    
    # Return statistics
    return {
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'pending_amount': pending_amount,
        'approved_amount': approved_amount
    }

@user_bp.route('/api/guarantor-claims/<claim_id>', methods=['GET'])
@login_required
def get_guarantor_claim(claim_id):
    """Get details of a specific guarantor claim"""
    try:
        # Import the necessary models
        from models.guarantor_claim import GuarantorClaim
        
        # Get the claim
        claim = GuarantorClaim.query.get_or_404(claim_id)
        
        # Return the claim data
        return jsonify({
            'success': True,
            'claim': {
                'id': claim.id,
                'loan_no': claim.loan_no,
                'borrower_name': claim.borrower_name,
                'guarantor_name': claim.guarantor_name,
                'claim_amount': float(claim.claim_amount),
                'claim_date': claim.claim_date.isoformat() if claim.claim_date else None,
                'status': claim.status,
                'notes': claim.notes
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching guarantor claim: {str(e)}")
        return jsonify({"error": f"Failed to fetch claim: {str(e)}"}), 500

@user_bp.route('/reports/uploads/claims/<path:filename>')
@login_required
def serve_claim_document(filename):
    """Serve claim documents from the uploads directory"""
    try:
        uploads_dir = os.path.join(current_app.static_folder, 'uploads', 'claims')
        return send_from_directory(uploads_dir, filename, as_attachment=False)
    except Exception as e:
        current_app.logger.error(f"Error serving claim document: {str(e)}")
        abort(404)

@user_bp.route('/api/guarantor-claims/<claim_id>/status', methods=['POST'])
@login_required
def update_guarantor_claim_status(claim_id):
    """API endpoint to update the status of a guarantor claim"""
    try:
        # Import the necessary models
        from models.guarantor_claim import GuarantorClaim
        from sqlalchemy import text
        
        # Get the data from the request
        data = request.form
        new_status = data.get('new_status')
        notes = data.get('notes', '')
        
        if not new_status:
            return jsonify({"error": "New status is required"}), 400
            
        # Validate the status
        valid_statuses = ['Pending', 'In Progress', 'Approved', 'Rejected', 'Settled']
        if new_status not in valid_statuses:
            return jsonify({"error": "Invalid status"}), 400
            
        # Get current timestamp
        current_time = datetime.utcnow()
        
        # Update the claim directly in the database
        update_query = text("""
            UPDATE guarantor_claims 
            SET status = :status,
                notes = :notes,
                updated_by = :updated_by,
                updated_at = :updated_at
            WHERE id = :claim_id
        """)
        
        # Execute the update
        db.session.execute(
            update_query,
            {
                'status': new_status,
                'notes': notes,
                'updated_by': current_user.id,
                'updated_at': current_time,
                'claim_id': claim_id
            }
        )
        
        # Fetch the updated row
        select_query = text("""
            SELECT id, status, notes, updated_at 
            FROM guarantor_claims 
            WHERE id = :claim_id
        """)
        
        result = db.session.execute(select_query, {'claim_id': claim_id})
        updated_row = result.fetchone()
        
        if not updated_row:
            return jsonify({"error": "Claim not found"}), 404
            
        # Commit the transaction
        db.session.commit()
            
        # Log the update
        current_app.logger.info(f"Successfully updated guarantor claim {claim_id} status to {new_status}")
        
        # Return success response with updated data
        return jsonify({
            'success': True,
            'message': f"Claim status updated successfully to {new_status}",
            'claim': {
                'id': updated_row.id,
                'status': updated_row.status,
                'notes': updated_row.notes,
                'updated_at': updated_row.updated_at.isoformat() if updated_row.updated_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating guarantor claim status: {str(e)}")
        return jsonify({"error": f"Failed to update claim status: {str(e)}"}), 500

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
        # Get form data from FormData
        data = {}
        for key, value in request.form.items():
            data[key] = value
        
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
            next_hearing_date=next_hearing_date,
            legal_officer_id=data.get('legal_officer_id'),
            legal_officer_name=data.get('legal_officer_name'),
            supervisor_id=data.get('supervisor_id'),
            supervisor_name=data.get('supervisor_name'),
            assigned_branch=data.get('assigned_branch')
        )
        
        # Add and commit to database
        db.session.add(new_case)
        db.session.commit()
        
        # Handle file upload if present
        attachment_file = request.files.get('attachment')
        if attachment_file and attachment_file.filename:
            try:
                # Create a secure filename
                filename = secure_filename(attachment_file.filename)
                
                # Create the uploads directory if it doesn't exist
                uploads_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'legal_cases', str(new_case.id))
                os.makedirs(uploads_dir, exist_ok=True)
                
                # Generate a unique filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(uploads_dir, unique_filename)
                
                # Save the file
                attachment_file.save(file_path)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                # Get file type
                file_type = attachment_file.content_type
                
                # Create attachment record
                attachment = LegalCaseAttachment(
                    legal_case_id=new_case.id,
                    file_name=filename,
                    file_path=file_path,
                    file_type=file_type,
                )
                db.session.add(attachment)
                db.session.commit()
                
            except Exception as e:
                current_app.logger.error(f"Error saving attachment: {str(e)}")
                db.session.rollback()
                return jsonify({
                    'error': 'Failed to save attachment',
                    'details': str(e)
                }), 500
        
        return jsonify({
            'message': 'Legal case created successfully', 
            'case_id': new_case.id
        }), 201
    
    except ValueError as ve:
        current_app.logger.error(f"Value error creating legal case: {str(ve)}")
        return jsonify({'error': 'Invalid date format'}), 400
    
    except Exception as e:
        current_app.logger.error(f"Error creating legal case: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({
            'error': 'An error occurred while creating the legal case',
            'details': str(e)
        }), 500
@user_bp.route('/legal-cases/<int:case_id>/attachments')
@login_required
def get_legal_case_attachments(case_id):
    try:
        # Get all attachments for the case
        attachments = LegalCaseAttachment.query.filter_by(legal_case_id=case_id).all()
        
        # Convert attachments to dictionary format
        attachment_list = []
        for attachment in attachments:
            attachment_dict = {
                'id': attachment.id,
                'filename': attachment.file_name,
                'upload_date': attachment.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                'file_type': attachment.file_type,
                'file_path': attachment.file_path
            }
            attachment_list.append(attachment_dict)
        
        return jsonify({
            'attachments': attachment_list,
            'total_attachments': len(attachment_list)
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching case attachments: {str(e)}")
        return jsonify({'error': 'Failed to fetch case attachments'}), 500

@user_bp.route('/legal-cases/<int:case_id>/attachments/<int:attachment_id>/download')
@login_required
def download_legal_case_attachment(case_id, attachment_id):
    try:
        # Get the attachment
        attachment = LegalCaseAttachment.query.get_or_404(attachment_id)
        
        # Verify that the attachment belongs to the specified case
        if attachment.legal_case_id != case_id:
            abort(404)
            
        # Check if file exists
        if not os.path.exists(attachment.file_path):
            return jsonify({
                'success': False,
                'message': 'Attachment file not found'
            }), 404
        
        # Return the file for download
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.file_name,
            mimetype=attachment.file_type or 'application/octet-stream'
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading legal case attachment: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while downloading the attachment'
        }), 500

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

        # Get case history
        history_query = """
            SELECT 
                ch.id,
                ch.action,
                ch.action_date,
                ch.notes,
                ch.status,
                ch.created_at
            FROM case_history ch
            WHERE ch.case_id = %s
            ORDER BY ch.created_at DESC
        """
        
        cursor.execute(history_query, (case_id,))
        history = cursor.fetchall()

        # Format dates for history entries
        for entry in history:
            if entry.get('action_date'):
                entry['action_date'] = entry['action_date'].isoformat()
            if entry.get('created_at'):
                entry['created_at'] = entry['created_at'].isoformat()

        # Get attachments for each history entry
        for entry in history:
            attachments_query = """
                SELECT 
                    a.id,
                    a.file_name,
                    a.file_path,
                    a.file_type,
                    a.uploaded_at
                FROM case_history_attachments a
                WHERE a.case_history_id = %s
                ORDER BY a.uploaded_at DESC
            """
            cursor.execute(attachments_query, (entry['id'],))
            entry['attachments'] = cursor.fetchall()
            
            # Format dates for attachments
            for attachment in entry.get('attachments', []):
                if attachment.get('uploaded_at'):
                    attachment['uploaded_at'] = attachment['uploaded_at'].isoformat()

        # Get case attachments
        case_attachments_query = """
            SELECT 
                a.id,
                a.file_name,
                a.file_path,
                a.file_type,
                a.uploaded_at
            FROM legal_case_attachments a
            WHERE a.legal_case_id = %s
            ORDER BY a.uploaded_at DESC
        """
        
        cursor.execute(case_attachments_query, (case_id,))
        case['attachments'] = cursor.fetchall()
        
        # Format dates for case attachments
        for attachment in case.get('attachments', []):
            if attachment.get('uploaded_at'):
                attachment['uploaded_at'] = attachment['uploaded_at'].isoformat()

        cursor.close()
        conn.close()

        return jsonify(case)

    except mysql.connector.Error as e:
        current_app.logger.error(f"Database error in get_legal_case: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        current_app.logger.error(f"Error in get_legal_case: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, TextAreaField, SelectField

class CaseHistoryForm(FlaskForm):
    case_id = StringField('Case ID')
    action = StringField('Action')
    action_date = DateTimeField('Action Date')
    notes = TextAreaField('Notes')
    status = SelectField('Status', choices=[('Active', 'Active'), ('Pending', 'Pending'), ('Closed', 'Closed')])

@user_bp.route('/add_case_history', methods=['POST'])
@login_required
def add_case_history():
    try:
        # Log all form data
        current_app.logger.debug(f"Form data received: {dict(request.form)}")
        current_app.logger.debug(f"Files received: {request.files}")
        
        # Get form data from FormData
        form_data = request.form
        case_id = form_data.get('case_id')
        action = form_data.get('action') or form_data.get('actionType')  # Use actionType if action is not present
        action_date = form_data.get('actionDate')
        notes = form_data.get('notes', '')
        status = form_data.get('status')

        # Log specific field values
        current_app.logger.debug(f"case_id: {case_id} (type: {type(case_id)})")
        current_app.logger.debug(f"action: {action}")
        current_app.logger.debug(f"action_date: {action_date}")
        current_app.logger.debug(f"status: {status}")

        # Validate required fields
        if not all([case_id, action, action_date, status]):
            current_app.logger.debug("Validation failed: Missing required fields")
            return jsonify({'error': 'All required fields must be filled'}), 400

        try:
            # Parse action date
            action_date = datetime.strptime(action_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            current_app.logger.debug(f"Invalid date format: {action_date}")
            return jsonify({'error': 'Invalid date format'}), 400

        # Create case history record
        try:
            case_history = CaseHistory(
                case_id=int(case_id),  # Convert to int since it comes as string
                action=action,
                action_date=action_date,
                notes=notes,
                status=status,
                created_by=current_user.id
            )
            current_app.logger.debug("Case history object created successfully")
        except Exception as e:
            current_app.logger.error(f"Error creating case history object: {str(e)}")
            return jsonify({'error': f'Failed to create case history: {str(e)}'}), 400
        
        # Add to database
        try:
            db.session.add(case_history)
            db.session.commit()
            current_app.logger.debug("Case history added to database successfully")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500

        # Handle file attachments
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'case_attachments')
            os.makedirs(upload_dir, exist_ok=True)

            for file in files:
                if file and file.filename:
                    # Generate a unique UUID for the filename
                    unique_id = str(uuid.uuid4())
                    filename = secure_filename(file.filename)
                    unique_filename = f"{unique_id}_{filename}"
                    file_path = os.path.join(upload_dir, unique_filename)

                    # Save the file first
                    file.save(file_path)
                    
                    # Create attachment record using ORM
                    attachment = CaseHistoryAttachment(
                        case_history_id=case_history.id,
                        file_name=unique_filename,
                        file_path=file_path,
                        file_type=file.content_type,
                        file_size=os.path.getsize(file_path)
                    )
                    
                    # Add to session
                    db.session.add(attachment)      
            db.session.commit()

        return jsonify({'message': 'Case history added successfully'}), 200

    except Exception as e:
        current_app.logger.error(f"Error adding case history: {str(e)}")
        return jsonify({'error': 'Failed to add case history'}), 500
        
@user_bp.route('/legal-cases/<int:case_id>/delete', methods=['DELETE'])
@login_required
def delete_legal_case(case_id):
    try:
        # First check if the case exists
        case = LegalCase.query.get(case_id)
        if not case:
            return jsonify({'error': 'Legal case not found'}), 404

        # Delete case history and its attachments
        history_records = CaseHistory.query.filter_by(case_id=case_id).all()
        for history in history_records:
            # Delete attachments first
            for attachment in history.history_attachments:
                db.session.delete(attachment)
            db.session.delete(history)

        # Delete legal case attachments
        attachments = LegalCaseAttachment.query.filter_by(legal_case_id=case_id).all()
        for attachment in attachments:
            db.session.delete(attachment)
        for history in history_records:
            db.session.delete(history)

        # Delete the case
        db.session.delete(case)
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({'message': 'Legal case deleted successfully'}), 200

    except Exception as e:
        # Rollback on error
        db.session.rollback()
        current_app.logger.error(f"Error deleting legal case: {str(e)}")
        return jsonify({'error': 'Failed to delete legal case'}), 500
@user_bp.route('/auction/<int:auction_id>/attachments/<int:attachment_id>/view')
@login_required
def view_auction_attachment_direct(auction_id, attachment_id):
    try:
        # Get the auction and attachment
        auction = Auction.query.get_or_404(auction_id)
        attachment = AuctionAttachment.query.get_or_404(attachment_id)
        
        # Verify the attachment belongs to this auction
        if attachment.auction_id != auction_id:
            abort(404)
            
        # Get the base upload folder from config
        base_upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # Construct the full file path
        full_file_path = os.path.join(base_upload_folder, attachment.file_path)
            
        if not os.path.exists(full_file_path):
            current_app.logger.error(f"File not found at path: {full_file_path}")
            abort(404)
        
        try:
            # Get the MIME type of the file
            mime_type = mimetypes.guess_type(attachment.file_name)[0]
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # Send the file for viewing in browser
            return send_file(
                full_file_path,
                mimetype=mime_type,
                as_attachment=False,  # This allows the file to be viewed in browser
                download_name=attachment.file_name
            )
        except Exception as e:
            current_app.logger.error(f"Error sending file {full_file_path}: {str(e)}")
            abort(404)
            
    except Exception as e:
        current_app.logger.error(f"Error serving auction attachment: {str(e)}")
        abort(404)

@user_bp.route('/auction/<int:auction_id>/attachments/<int:attachment_id>/download')
@login_required
def download_auction_attachment_direct(auction_id, attachment_id):
    try:
        # Get the auction and attachment
        auction = Auction.query.get_or_404(auction_id)
        attachment = AuctionAttachment.query.get_or_404(attachment_id)
        
        # Verify the attachment belongs to this auction
        if attachment.auction_id != auction_id:
            abort(404)
        
        # Get the base upload folder from config
        base_upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # Construct the full file path
        full_file_path = os.path.join(base_upload_folder, attachment.file_path)
        
        if not os.path.exists(full_file_path):
            current_app.logger.error(f"File not found at path: {full_file_path}")
            abort(404)
        
        try:
            return send_from_directory(
                os.path.dirname(full_file_path),
                os.path.basename(full_file_path),
                as_attachment=True,
                download_name=attachment.file_name
            )
        except Exception as e:
            current_app.logger.error(f"Error sending file {full_file_path}: {str(e)}")
            abort(404)
            
    except Exception as e:
        current_app.logger.error(f"Error downloading auction attachment: {str(e)}")
        abort(404)

@user_bp.route('/auction/<int:auction_id>')
@login_required
def get_auction_details(auction_id):
    try:
        auction = Auction.query.get_or_404(auction_id)
        
        # Get attachments
        attachments = [{
            'id': attachment.id,
            'file_name': attachment.file_name,
            'file_path': attachment.file_path
        } for attachment in auction.attachments]
        
        return jsonify({
            'id': auction.id,
            'loan_id': auction.loan_id,
            'client_name': auction.client_name,
            'property_description': auction.property_description,
            'property_type': auction.property_type,
            'property_location': auction.property_location,
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
        auction.property_location = data.get('property_location', auction.property_location)
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

    # Enhanced prompt with support for complex multi-part queries and user preferences
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
   - For complex multi-part queries, generate multiple separate SQL statements separated by semicolons
   - When InstallmentAmount is not available, use OutstandingBalance as a substitute rather than PenaltyAmount
   - For missed payments, calculate based on the number of missed installments rather than using raw days in arrears

4. Response Format:
   - Always put SQL queries inside ```sql and ``` tags
   - Make SQL the PRIMARY content of your response
   - For multiple queries, include all of them within a single code block, separated by semicolons
   - After the SQL, provide a brief explanation (no more than 2 sentences)
   - NEVER say "Here's a SQL query that..." - just provide the SQL directly

5. Error Prevention:
   - Always include all necessary JOINs
   - Always check column names against the schema
   - Use aliases for clarity when joining tables
   - Verify that tables exist before referencing them

6. Complex Query Handling:
   - For borrower history and character queries, provide multiple queries that cover:
     a) Basic customer information
     b) Loan summary data
     c) Borrowing history details
     d) Repayment patterns
   - For queries about missed payments, focus on number of installments missed rather than days
   - For loan data, when InstallmentAmount is not available, use OutstandingBalance instead

Example good response for a complex query:
```sql
SELECT sacco_db.members.name, sacco_db.members.phone, sacco_db.members.email 
FROM sacco_db.members 
WHERE sacco_db.members.id = 123;

SELECT loan_system.loans.loan_id, loan_system.loans.amount, loan_system.loans.status 
FROM loan_system.loans 
WHERE loan_system.loans.member_id = 123;

SELECT loan_system.repayments.date, loan_system.repayments.amount 
FROM loan_system.repayments 
JOIN loan_system.loans ON loan_system.repayments.loan_id = loan_system.loans.loan_id 
WHERE loan_system.loans.member_id = 123
```
These queries retrieve the member's information, loan details, and repayment history.
"""
    return system_prompt

def call_mistral_api(user_input, preferred_db=None, conversation_history=None):
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
    
    # Check for specific query types that need special handling
    is_complex_borrower_query = any(term in user_input.lower() for term in [
        "borrowing history", "repayment history", "borrowing character", "credit history", "loan summary"
    ])
    
    is_missed_payment_query = any(term in user_input.lower() for term in [
        "missed payment", "late payment", "arrears", "overdue", "delinquent", "deliquent", 
        "defaulted", "default", "behind on", "top arrears", "highest arrears", "most overdue",
        "past due", "non-performing", "npl"
    ])
    
    # Detect account summary requests
    is_account_summary = any(pattern in user_input.lower() for pattern in [
        "account summary", "customer summary", "member summary", 
        "account details for", "summary for", "information about",
        "tell me about", "show me details for", "give me account",
        "account history", "transaction history", "payment history"
    ])
    
    # Detect loan performance and monitoring queries
    is_loan_monitoring_query = any(pattern in user_input.lower() for pattern in [
        "outstanding balance", "due this week", "due next week", "due soon", "due date",
        "disbursed in", "disbursed last", "recently disbursed", "new loans",
        "active loans", "current status", "loan status", "loan id", "loan account",
        "not received", "no repayment", "restructured", "rescheduled"
    ])
    
    # Detect repayment and schedule queries
    is_repayment_query = any(pattern in user_input.lower() for pattern in [
        "repayment schedule", "payment schedule", "installment schedule", "amortization",
        "missed installment", "missed payment", "next repayment", "next payment", "next installment",
        "partial repayment", "partial payment", "received payment", "received repayment",
        "repayments made", "payments made", "repayment pattern", "payment pattern", "irregular payment"
    ])
    
    # Detect portfolio analytics queries
    is_portfolio_analytics_query = any(pattern in user_input.lower() for pattern in [
        "portfolio value", "total portfolio", "delinquency rate", "breakdown of loans",
        "top clients", "top borrowers", "top loans", "loans by branch", "branch performance",
        "disbursement trends", "loan trends", "average loan", "loan officer", "portfolio at risk",
        "par report", "par30", "par60", "par90", "loan portfolio", "product type"
    ])
    
    # Detect client/member queries
    is_client_query = any(pattern in user_input.lower() for pattern in [
        "loan history", "member id", "client id", "contact information", "phone number", "email",
        "multiple loans", "active loans", "cleared loans", "paid off", "settled", "credit score",
        "risk rating", "collateral", "guarantor", "member details", "client details", "borrower details"
    ]) or re.search(r'\bmember\s+\w+\s+\w+', user_input.lower()) is not None
    
    # Detect alerts and exceptions queries
    is_alert_query = any(pattern in user_input.lower() for pattern in [
        "exceeded", "grace period", "without guarantors", "no guarantor", "missing guarantor",
        "less than scheduled", "underpayment", "no follow-up", "incomplete documentation",
        "missing document", "not yet disbursed", "system mismatch", "cbs", "exception",
        "alert", "violation", "deficiency", "irregularity", "compliance issue"
    ])
    
    # Detect guarantors and collateral queries
    is_guarantor_collateral_query = any(pattern in user_input.lower() for pattern in [
        "guarantor", "guarantors", "collateral", "security", "secured by", "backed by",
        "loan security", "asset", "pledge", "pledged", "guarantee", "guaranteed by"
    ])
    
    # Detect rescheduling, top-ups, and restructuring queries
    is_loan_modification_query = any(pattern in user_input.lower() for pattern in [
        "topped up", "top-up", "topup", "top up", "additional loan", "loan extension",
        "rescheduled", "reschedule", "restructured", "restructuring", "restructure",
        "modified", "modification", "refinanced", "refinance", "eligible for"
    ])
    
    # Detect officer/branch performance queries
    is_performance_query = any(pattern in user_input.lower() for pattern in [
        "officer", "branch", "managed by", "handled by", "performance", "npl ratio",
        "non-performing", "disbursed by", "portfolio quality", "portfolio size",
        "repayment performance", "collection rate", "disbursement target", "highest", "lowest"
    ])
    
    # Add special instructions based on query type
    special_instructions = ""
    
    # Add naming convention guidance to the prompt
    enhanced_input = f"{enhanced_input}\n\nIMPORTANT: Use the EXACT table and column names as they appear in the schema. Examples of actual table names: {example_tables}."
    
    # Add instructions for complex queries
    if is_complex_borrower_query:
        special_instructions += "\n\nThis appears to be a complex query about a borrower's history and character. Please generate multiple SQL queries separated by semicolons to provide a comprehensive view including:\n1. Basic customer information\n2. Loan summary data\n3. Borrowing history details\n4. Repayment patterns\nEach query should be complete and executable on its own."
    
    # Add instructions for account summary requests
    if is_account_summary:
        special_instructions += "\n\nThis appears to be a request for an account summary. Please generate multiple SQL queries separated by semicolons to provide a comprehensive view including:\n1. Basic customer information (name, contact details)\n2. Account details (balance, shares)\n3. Loan information (amount, status, application date, repayment period, interest rate)\n4. Loan ledger details (disbursed amount, outstanding balance, next repayment date, missed installments)\nEach query should be complete and executable on its own."
    
    # Add instructions for officer/branch performance queries
    elif is_performance_query:
        # Check for specific performance query types
        if re.search(r'(officer|managed by|handled by)\s+\w+\s+\w+', user_input.lower()):
            special_instructions += "\n\nThis appears to be a query about loans managed by a specific loan officer. Please generate SQL queries to:\n1. Find the loan officer by name or ID\n2. Retrieve all loans managed or handled by this officer\n3. Include loan details, customer information, and current status\n4. Order by disbursement date (most recent first)\nEach query should be complete and executable on its own."
        elif "repayment performance" in user_input.lower() or ("performance" in user_input.lower() and "officer" in user_input.lower()):
            special_instructions += "\n\nThis appears to be a query about repayment performance by loan officer. Please generate SQL queries to:\n1. Calculate repayment performance metrics for each loan officer\n2. Include metrics such as collection rate, on-time payment percentage, and PAR ratio\n3. Include the number and value of loans managed by each officer\n4. Order by performance metric (best performing first)\nEach query should be complete and executable on its own."
        elif "disbursed by branch" in user_input.lower() or ("branch" in user_input.lower() and "last 3 months" in user_input.lower()):
            special_instructions += "\n\nThis appears to be a query about loans disbursed by a specific branch in a time period. Please generate SQL queries to:\n1. Find the branch by name or ID\n2. Retrieve all loans disbursed by this branch within the specified time period\n3. Calculate the time period based on the current date minus the specified months\n4. Include loan details, customer information, and disbursement amounts\n5. Order by disbursement date (most recent first)\nEach query should be complete and executable on its own."
        elif "npl ratio" in user_input.lower() or "non-performing" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about officers with the highest NPL (Non-Performing Loan) ratio. Please generate SQL queries to:\n1. Calculate the NPL ratio for each loan officer\n2. Include the total portfolio value and non-performing loan value for each officer\n3. Include the number of loans and number of non-performing loans\n4. Order by NPL ratio (highest first)\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a query about officer or branch performance. Please generate SQL queries to:\n1. Calculate the relevant performance metrics based on the query\n2. Include appropriate aggregations by officer or branch\n3. Include portfolio size, quality metrics, and other relevant indicators\n4. Order results in a logical manner based on the query context\nEach query should be complete and executable on its own."
    
    # Add instructions for rescheduling, top-ups, and restructuring queries
    elif is_loan_modification_query:
        # Check for specific loan modification query types
        if any(term in user_input.lower() for term in ["topped up", "top-up", "topup", "top up"]) and re.search(r'loan\s+\d+', user_input.lower()):
            special_instructions += "\n\nThis appears to be a query about whether a specific loan has been topped up. Please generate SQL queries to:\n1. Find the loan by its ID or other identifiers\n2. Check if there are any top-up records associated with this loan\n3. Include details of the original loan and any top-ups (amount, date, etc.)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["rescheduled", "reschedule"]) and "past 6 months" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about rescheduled loans in the past 6 months. Please generate SQL queries to:\n1. Find loans that have been rescheduled within the past 6 months\n2. Include loan details, customer information, original terms, and new terms\n3. Calculate the time period based on the current date minus 6 months\n4. Order by rescheduling date (most recent first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["restructuring", "restructure"]) and "pending" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about loans with pending restructuring requests. Please generate SQL queries to:\n1. Find loans that have pending restructuring requests\n2. Include loan details, customer information, current terms, and proposed terms\n3. Include the date the restructuring was requested\n4. Order by request date (oldest first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["eligible", "qualify"]) and any(term in user_input.lower() for term in ["top-up", "topup", "top up"]):
            special_instructions += "\n\nThis appears to be a query about loans eligible for top-up. Please generate SQL queries to:\n1. Find active loans that meet the criteria for top-up eligibility\n2. Include loan details, customer information, and repayment history\n3. Calculate eligibility based on factors like percentage repaid, time elapsed, and payment history\n4. Order by eligibility score or potential top-up amount (highest first)\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a query about loan modifications (top-ups, rescheduling, or restructuring). Please generate SQL queries to:\n1. Find loans that match the modification criteria specified in the query\n2. Include loan details, customer information, and modification history\n3. Order results in a logical manner based on the query context\nEach query should be complete and executable on its own."
    
    # Add instructions for guarantors and collateral queries
    elif is_guarantor_collateral_query:
        # Check for specific guarantor/collateral query types
        if re.search(r'guarantors?\s+for\s+loan', user_input.lower()):
            special_instructions += "\n\nThis appears to be a query about guarantors for a specific loan. Please generate SQL queries to:\n1. Find the loan by its ID or other identifiers\n2. Retrieve all guarantors associated with this loan\n3. Include guarantor details (name, ID, relationship to borrower, etc.)\n4. Include the guaranteed amount or percentage for each guarantor if available\nEach query should be complete and executable on its own."
        elif re.search(r'guarantors?\s+to\s+multiple', user_input.lower()) or "multiple loans" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about members who are guarantors to multiple loans. Please generate SQL queries to:\n1. Find members who are guarantors for more than one loan\n2. Count the number of loans each member is guaranteeing\n3. Include guarantor details and basic information about each guaranteed loan\n4. Order by the number of loans guaranteed (highest first)\nEach query should be complete and executable on its own."
        elif re.search(r'value\s+of\s+collateral', user_input.lower()):
            special_instructions += "\n\nThis appears to be a query about collateral value for a specific loan. Please generate SQL queries to:\n1. Find the loan by its ID or other identifiers\n2. Retrieve all collateral items associated with this loan\n3. Include collateral details (type, description, valuation, etc.)\n4. Calculate the total collateral value and compare it to the loan amount\nEach query should be complete and executable on its own."
        elif "backed only by guarantors" in user_input.lower() or "no collateral" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about loans backed only by guarantors with no collateral. Please generate SQL queries to:\n1. Find loans that have guarantors but no collateral recorded\n2. Include loan details, borrower information, and guarantor details\n3. Order by loan amount (highest first)\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a query about loan guarantors or collateral. Please generate SQL queries to:\n1. Retrieve the relevant guarantor or collateral information based on the query\n2. Include loan details and borrower information where appropriate\n3. Ensure results are ordered in a logical manner (e.g., by loan amount or date)\nEach query should be complete and executable on its own."
    
    # Add instructions for alerts and exceptions queries
    elif is_alert_query:
        # Check for specific alert/exception query types
        if any(term in user_input.lower() for term in ["exceeded", "grace period"]):
            special_instructions += "\n\nThis appears to be a query about loans that have exceeded their grace period. Please generate SQL queries to:\n1. Find loans where the grace period has been exceeded but no action has been taken\n2. Include loan details, customer information, and the number of days past the grace period\n3. Calculate the days beyond grace period using the appropriate date fields\n4. Order by days past grace period (highest first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["without guarantors", "no guarantor", "missing guarantor"]):
            special_instructions += "\n\nThis appears to be a query about loans disbursed without guarantors. Please generate SQL queries to:\n1. Find loans that have been disbursed but have no guarantors recorded\n2. Include loan details, customer information, and disbursement date\n3. Order by loan amount (highest first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["less than scheduled", "underpayment"]):
            special_instructions += "\n\nThis appears to be a query about loans with repayment amounts less than scheduled. Please generate SQL queries to:\n1. Find loans where actual repayment amounts are less than scheduled amounts\n2. Calculate the shortfall amount and percentage\n3. Include loan details, customer information, and payment history\n4. Order by shortfall percentage (highest first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["no follow-up", "follow up"]):
            special_instructions += "\n\nThis appears to be a query about overdue loans with no follow-up records. Please generate SQL queries to:\n1. Find overdue loans where no follow-up actions have been recorded\n2. Include loan details, customer information, and days overdue\n3. Order by days overdue (highest first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["incomplete documentation", "missing document"]):
            special_instructions += "\n\nThis appears to be a query about loans with incomplete documentation. Please generate SQL queries to:\n1. Find loans where required documentation is incomplete or missing\n2. Include loan details, customer information, and missing document types\n3. Order by loan amount (highest first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["not yet disbursed", "system mismatch", "cbs"]):
            special_instructions += "\n\nThis appears to be a query about system synchronization issues. Please generate SQL queries to:\n1. Find loans that show as disbursed in the loan system but not in the core banking system (CBS)\n2. Include loan details, customer information, and disbursement date\n3. Order by disbursement date (most recent first)\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a query about loan exceptions or alerts. Please generate SQL queries to:\n1. Find loans that match the exception criteria specified in the query\n2. Include loan details, customer information, and relevant exception data\n3. Order results by severity or risk level (highest first)\nEach query should be complete and executable on its own."
    
    # Add instructions for client/member queries
    elif is_client_query:
        # Check for specific client/member query types
        if any(term in user_input.lower() for term in ["loan history", "loan details"]):
            special_instructions += "\n\nThis appears to be a query about a member's loan history. Please generate SQL queries to:\n1. Find the member by ID or name\n2. Retrieve their complete loan history including active and closed loans\n3. Include loan details such as amount, disbursement date, status, and repayment history\n4. Order by disbursement date (most recent first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["contact information", "phone number", "email", "address"]):
            special_instructions += "\n\nThis appears to be a query about a member's contact information. Please generate SQL queries to:\n1. Find the member by ID or name\n2. Retrieve their contact information including name, phone number, email, and address\n3. Include only essential personal information and avoid retrieving sensitive data\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["multiple loans", "active loans", "more than one"]):
            special_instructions += "\n\nThis appears to be a query about members with multiple loans. Please generate SQL queries to:\n1. Find members who have more than one active loan\n2. Include member details and basic information about each of their loans\n3. Order by the number of active loans (highest first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["cleared loans", "paid off", "settled", "completed"]):
            special_instructions += "\n\nThis appears to be a query about members who have cleared their loans. Please generate SQL queries to:\n1. Find members who have paid off or settled their loans within the specified time period\n2. Include member details and information about the cleared loans\n3. Order by clearance date (most recent first)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["credit score", "risk rating", "creditworthiness"]):
            special_instructions += "\n\nThis appears to be a query about a member's credit score or risk rating. Please generate SQL queries to:\n1. Find the member by ID or name\n2. Retrieve their credit score, risk rating, or creditworthiness assessment\n3. Include relevant loan history information that might affect their rating\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["collateral", "security", "guarantee", "guarantor"]):
            special_instructions += "\n\nThis appears to be a query about loans with collateral. Please generate SQL queries to:\n1. Find members or loans with collateral or guarantors\n2. Include member details, loan information, and collateral details\n3. Order by loan amount (highest first)\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a query about specific members or clients. Please generate SQL queries to:\n1. Find the relevant member(s) based on the query\n2. Retrieve the appropriate member and loan information\n3. Ensure results are ordered in a logical manner\n4. Include only essential personal information and avoid retrieving sensitive data\nEach query should be complete and executable on its own."
    
    # Add instructions for portfolio analytics queries
    elif is_portfolio_analytics_query:
        # Check for specific portfolio analytics query types
        if any(term in user_input.lower() for term in ["portfolio value", "total portfolio", "loan portfolio"]):
            special_instructions += "\n\nThis appears to be a query about the total loan portfolio value. Please generate SQL queries to:\n1. Calculate the sum of all outstanding loan balances\n2. Group by loan status if relevant (active, closed, etc.)\n3. Include the total number of loans in the portfolio\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["delinquency rate"]):
            special_instructions += "\n\nThis appears to be a query about delinquency rate. Please generate SQL queries to:\n1. Calculate the total value of all loans in the portfolio\n2. Calculate the value of loans in arrears (days_in_arrears > 0)\n3. Calculate the delinquency rate using the formula: (Value of Loans in Arrears / Total Portfolio Value) * 100\n4. If the query specifies a time period (e.g., this quarter), filter the data accordingly\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["breakdown", "by product", "product type"]):
            special_instructions += "\n\nThis appears to be a query about loan breakdown by product type. Please generate SQL queries to:\n1. Count the number of loans by product type or category\n2. Calculate the total value of loans by product type or category\n3. Calculate the percentage of the total portfolio for each product type\n4. Order by loan value (descending)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["top clients", "top borrowers", "top loans"]):
            special_instructions += "\n\nThis appears to be a query about top clients or loans. Please generate SQL queries to:\n1. Find the clients with the highest outstanding loan balances\n2. Include client name, loan details, and outstanding balance\n3. Limit results to 10 records (or as specified in the query)\n4. Order by outstanding balance (descending)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["by branch", "branch performance"]):
            special_instructions += "\n\nThis appears to be a query about branch performance. Please generate SQL queries to:\n1. Count the number of loans disbursed by branch\n2. Calculate the total value of loans disbursed by branch\n3. Include branch name and any other relevant branch details\n4. Order by number of loans or total value (descending)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["trends", "past 6 months", "over time"]):
            special_instructions += "\n\nThis appears to be a query about loan trends over time. Please generate SQL queries to:\n1. Count the number of loans disbursed by month/period\n2. Calculate the total value of loans disbursed by month/period\n3. Limit to the time period specified in the query (e.g., past 6 months)\n4. Order by date (ascending)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["average loan", "loan officer", "by officer"]):
            special_instructions += "\n\nThis appears to be a query about loan officer performance. Please generate SQL queries to:\n1. Calculate the average loan amount by loan officer\n2. Count the number of loans handled by each loan officer\n3. Calculate the total value of loans handled by each loan officer\n4. Include loan officer name and ID\n5. Order by average loan amount (descending)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["portfolio at risk", "par report", "par30", "par60", "par90"]):
            special_instructions += "\n\nThis appears to be a query about Portfolio at Risk (PAR). Please generate SQL queries to:\n1. Calculate the total value of all loans in the portfolio\n2. Calculate the value of loans with arrears > 30 days (PAR30)\n3. Calculate the value of loans with arrears > 60 days (PAR60)\n4. Calculate the value of loans with arrears > 90 days (PAR90)\n5. Calculate the PAR ratios using the formula: (Value of Loans with Arrears > X days / Total Portfolio Value) * 100\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a portfolio analytics query. Please generate SQL queries to:\n1. Retrieve the relevant portfolio metrics based on the query\n2. Include appropriate aggregations (sum, count, average, etc.)\n3. Group by relevant dimensions (product, branch, officer, etc.)\n4. Order results logically based on the query context\nEach query should be complete and executable on its own."
    
    # Add instructions for repayment and schedule queries
    elif is_repayment_query:
        # Check for specific repayment query types
        if any(term in user_input.lower() for term in ["repayment schedule", "payment schedule", "installment schedule", "amortization"]):
            special_instructions += "\n\nThis appears to be a query about a loan's repayment schedule. Please generate SQL queries to:\n1. Find the loan by its ID or account number\n2. Retrieve the complete repayment schedule including payment dates, installment amounts, and payment status\n3. Include loan details such as disbursement date, loan amount, and interest rate for context\n4. Order by payment date (ascending)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["missed installment", "missed payment", "missed their last"]):
            special_instructions += "\n\nThis appears to be a query about missed installments. Please generate a SIMPLE SQL query to:\n1. Find loans or members where the most recent scheduled payment was not made\n2. Join the customers/members table to get member names\n3. Include only essential columns: member name, loan ID, due date, days overdue, amount\n4. Limit results to 20 records maximum\n5. Order by days overdue (descending)\nKeep the query simple and avoid complex subqueries or analytics."

        elif any(term in user_input.lower() for term in ["next repayment", "next payment", "next installment"]):
            special_instructions += "\n\nThis appears to be a query about upcoming repayment dates. Please generate SQL queries to:\n1. Find the specified loan or member\n2. Retrieve the next scheduled payment date, amount, and status\n3. Include loan details and previous payment history for context\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["partial repayment", "partial payment"]):
            special_instructions += "\n\nThis appears to be a query about partial repayments. Please generate SQL queries to:\n1. Find partial payments within the specified time period\n2. Include customer information, loan details, payment amount, and scheduled amount\n3. Calculate the difference between scheduled and actual payment amounts\n4. Order by payment date (descending)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["received payment", "received repayment", "repayments made", "payments made"]):
            special_instructions += "\n\nThis appears to be a query about received payments. Please generate SQL queries to:\n1. Find payments received within the specified time period\n2. Include customer information, loan details, payment amount, and payment date\n3. Order by payment date (descending)\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["repayment pattern", "payment pattern", "irregular payment"]):
            special_instructions += "\n\nThis appears to be a query about repayment patterns. Please generate SQL queries to:\n1. Analyze payment history for loans to identify irregular patterns\n2. Include customer information, loan details, and payment history\n3. Look for inconsistencies in payment dates or amounts\n4. Order by irregularity severity (most irregular first)\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a query about loan repayments or schedules. Please generate SQL queries to:\n1. Retrieve the relevant payment information based on the query\n2. Include customer details and loan information where appropriate\n3. Ensure results are ordered in a logical manner (e.g., by date or amount)\n4. Limit results if necessary to avoid overwhelming output\nEach query should be complete and executable on its own."
    
    # Add instructions for loan monitoring queries
    elif is_loan_monitoring_query:
        # Check for specific loan monitoring query types
        if "outstanding balance" in user_input.lower() or "loan account" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about a specific loan's outstanding balance. Please generate SQL queries to:\n1. Find the loan by its ID or account number\n2. Retrieve the loan details including outstanding_balance, disbursed_amount, and repayment_status\n3. Include customer information if available\nEach query should be complete and executable on its own."
        elif any(term in user_input.lower() for term in ["due this week", "due next week", "due soon", "due date"]):
            special_instructions += "\n\nThis appears to be a query about loans due soon. Please generate SQL queries to:\n1. Find loans with upcoming due dates (within the next 7 days)\n2. Include loan details, customer information, and payment amounts\n3. Order by due date (ascending)\nEach query should be complete and executable on its own."
        elif "disbursed" in user_input.lower() or "new loans" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about recently disbursed loans. Please generate SQL queries to:\n1. Find loans disbursed within the specified time period\n2. Include loan details, disbursement date, and customer information\n3. Order by disbursement date (descending)\nEach query should be complete and executable on its own."
        elif "active loans" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about active loans for a specific member. Please generate SQL queries to:\n1. Find all active loans for the specified member\n2. Include loan details, disbursement date, outstanding balance, and next payment date\n3. Order by disbursement date (descending)\nEach query should be complete and executable on its own."
        elif "status" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about a loan's current status. Please generate SQL queries to:\n1. Find the specific loan by ID\n2. Retrieve comprehensive loan details including status, outstanding balance, days in arrears, and payment history\n3. Include customer information\nEach query should be complete and executable on its own."
        elif "not received" in user_input.lower() or "no repayment" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about loans without recent repayments. Please generate SQL queries to:\n1. Find loans that have not received payments within the specified time period\n2. Include loan details, customer information, outstanding balance, and last payment date\n3. Order by last payment date (ascending)\nEach query should be complete and executable on its own."
        elif "restructured" in user_input.lower() or "rescheduled" in user_input.lower():
            special_instructions += "\n\nThis appears to be a query about restructured loans. Please generate SQL queries to:\n1. Find loans that have been restructured within the specified time period\n2. Include loan details, customer information, restructuring date, and terms\n3. Order by restructuring date (descending)\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a loan monitoring query. Please generate SQL queries to:\n1. Retrieve the relevant loan information based on the query\n2. Include customer details where appropriate\n3. Ensure results are ordered in a logical manner (e.g., by date, amount, or status)\n4. Limit results if necessary to avoid overwhelming output\nEach query should be complete and executable on its own."
    
    # Add instructions for missed payment queries based on user preferences
    if is_missed_payment_query:
        # Check if this is a ranking query (top N delinquent loans)
        is_ranking_query = any(term in user_input.lower() for term in ["top", "highest", "most", "worst", "ranking", "list"])
        
        if is_ranking_query:
            special_instructions += "\n\nThis appears to be a query about ranking delinquent loans. Please generate SQL queries to:\n1. Find customers with loans in arrears\n2. Include customer name, loan details, days_in_arrears, and outstanding_balance\n3. Order by days_in_arrears in descending order (highest first)\n4. Limit the results to 5-10 records\n5. IMPORTANT: In your response, include both the actual days in arrears AND the calculated missed installments (using Math.ceil(days_in_arrears / 30))\nEach query should be complete and executable on its own."
        else:
            special_instructions += "\n\nThis appears to be a query about missed payments or arrears. Please generate SQL queries to:\n1. Find the customer's basic information\n2. Retrieve their loan details including the days_in_arrears column and outstanding_balance column\n3. IMPORTANT: In your response, include both the actual days in arrears AND the calculated missed installments (using Math.ceil(days_in_arrears / 30))\nEach query should be complete and executable on its own."
    
    # Add general instruction about InstallmentAmount based on user preferences
    special_instructions += "\n\nIMPORTANT: When InstallmentAmount is not available in the database schema, use OutstandingBalance as a substitute rather than PenaltyAmount."
    
    # Add instructions for multi-part queries
    special_instructions += "\n\nFor complex queries that require multiple pieces of information, generate multiple SQL queries separated by semicolons. Each query should be complete and executable on its own."
    
    # Combine all instructions
    enhanced_input = f"{enhanced_input}{special_instructions}"
    
    # Include conversation history for context if available
    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history and len(conversation_history) > 0:
        # Add a note about conversation history
        enhanced_input = f"{enhanced_input}\n\nPlease consider our previous conversation for context."
        
        # Add previous messages to the conversation
        for exchange in conversation_history:
            messages.append({"role": "user", "content": exchange['user_message']})
            messages.append({"role": "assistant", "content": exchange['assistant_response']})
    
    # Add the current user message
    messages.append({"role": "user", "content": f"Convert this to SQL (respond with SQL code only): {enhanced_input}"})

    data = {
        'model': MODEL_NAME,
        'messages': messages,
        'max_tokens': 600,
        'temperature': 0.2
    }

    max_retries = 5  # Increased from 3 to 5
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            # Adjust timeout based on query complexity
            timeout_value = 30 if any(term in user_input.lower() for term in ["missed installment", "missed payment", "missed their last"]) else 20
            response = requests.post(MISTRAL_API_URL, headers=headers, json=data, timeout=timeout_value)
            
            if response.status_code == 200:
                api_response = response.json()
                if 'choices' in api_response and api_response['choices']:
                    return api_response['choices'][0]['message']['content'].strip()
                else:
                    error_msg = "Mistral API returned an empty response"
                    current_app.logger.error(error_msg)
                    last_error = error_msg
            else:
                error_msg = f"Mistral API error: {response.status_code} - {response.text}"
                current_app.logger.error(error_msg)
                last_error = error_msg
                
                # For certain status codes, don't retry (e.g., 400 Bad Request)
                if response.status_code == 400:
                    break
            
            # If we get here, something went wrong
            retry_count += 1
            wait_time = 2 ** retry_count  # Exponential backoff
            if retry_count < max_retries:
                current_app.logger.warning(f"Retrying API call ({retry_count}/{max_retries}) in {wait_time}s")
                time.sleep(wait_time)
            
        except requests.exceptions.Timeout as e:
            error_msg = f"API request timeout: {str(e)}"
            current_app.logger.error(error_msg)
            last_error = error_msg
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                current_app.logger.warning(f"Retrying after timeout ({retry_count}/{max_retries}) in {wait_time}s")
                time.sleep(wait_time)
                
        except Exception as e:
            error_msg = f"API request error: {str(e)}"
            current_app.logger.error(error_msg)
            last_error = error_msg
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                current_app.logger.warning(f"Retrying after error ({retry_count}/{max_retries}) in {wait_time}s")
                time.sleep(wait_time)
    
    return None


def clean_sql_response(response):
    """Extract SQL code block from the AI response with improved pattern matching.
    Now supports multiple SQL queries separated by semicolons."""
    if not response:
        return ""
    
    # First, try to extract code blocks
    code_block_patterns = [
        r"```sql\s+(.*?)\s+```",  # Standard SQL code block
        r"```\s+(.*?)\s+```",  # Generic code block
        r"```(.*?)```"  # No whitespace
    ]
    
    for pattern in code_block_patterns:
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            # Join all matched code blocks
            sql_code = '\n'.join(matches)
            # Clean up any extra backticks that might have been captured
            sql_code = re.sub(r'```.*?```', '', sql_code, flags=re.DOTALL)
            return sql_code.strip()
    
    # If no code blocks found, try to extract complete SQL queries from the response
    # The best approach is to extract code between SQL markers if they exist
    if '```sql' in response and '```' in response.split('```sql', 1)[1]:
        # Extract everything between ```sql and the next ```
        sql_block = response.split('```sql', 1)[1].split('```', 1)[0].strip()
        
        # Split the SQL block into individual queries by semicolons
        queries = []
        current_query = []
        paren_count = 0  # To track nested parentheses for subqueries
        
        for line in sql_block.split('\n'):
            # Count opening and closing parentheses to track nesting level
            paren_count += line.count('(') - line.count(')')
            current_query.append(line)
            
            # Only split on semicolons when we're at the top level (not in a subquery)
            if ';' in line and paren_count <= 0:
                queries.append('\n'.join(current_query))
                current_query = []
                paren_count = 0  # Reset for safety
        
        # Add the last query if there's anything left
        if current_query:
            queries.append('\n'.join(current_query))
        
        # Clean up the queries and ensure they end with semicolons
        clean_queries = []
        for query in queries:
            query = query.strip()
            if query and not query.isspace():
                if not query.endswith(';'):
                    query += ';'
                clean_queries.append(query)
        
        if clean_queries:
            return '\n'.join(clean_queries)
    
    # Fallback: try to extract complete SQL statements with regex
    # This pattern needs to be more robust to handle nested subqueries
    complete_sql_pattern = r"(SELECT[\s\S]*?FROM[\s\S]*?(?:WHERE[\s\S]*?)?(?:GROUP BY[\s\S]*?)?(?:HAVING[\s\S]*?)?(?:ORDER BY[\s\S]*?)?(?:LIMIT[\s\S]*?)?(?:;|$))"
    
    # Find all complete SQL statements in the response
    all_queries = []
    
    # Try to extract complete SQL statements
    matches = re.findall(complete_sql_pattern, response, re.IGNORECASE)
    if matches:
        for match in matches:
            sql = match.strip()
            if sql and not sql.isspace():
                # Make sure the SQL statement ends with a semicolon
                if not sql.rstrip().endswith(';'):
                    sql = sql.rstrip() + ';'
                all_queries.append(sql)
    
    # If we found complete queries, return them joined
    if all_queries:
        return '\n'.join(all_queries)
        
    # Fallback: try to extract SQL queries with more specific patterns
    sql_patterns = [
        r"(SELECT[\s\S]*?FROM[\s\S]*?)(?=SELECT|$)",  # Match SELECT queries up to the next SELECT or end
        r"(SHOW[\s\S]*?)(?=SELECT|SHOW|DESCRIBE|$)",  # SHOW queries
        r"(DESCRIBE[\s\S]*?)(?=SELECT|SHOW|DESCRIBE|$)"  # DESCRIBE queries
    ]
    
    all_queries = []
    for pattern in sql_patterns:
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        if matches:
            for match in matches:
                sql = match.strip()
                if sql and not sql.isspace():
                    # Make sure the SQL statement ends with a semicolon
                    if not sql.rstrip().endswith(';'):
                        sql = sql.rstrip() + ';'
                    all_queries.append(sql)
    
    # If we found queries with the fallback patterns, return them joined
    if all_queries:
        return '\n'.join(all_queries)
    
    # If no SQL found using patterns, check if it's a raw SQL query
    if response.strip().upper().startswith("SELECT"):
        # Extract the SQL query up to a natural boundary
        lines = response.strip().split('\n')
        sql_lines = []
        for line in lines:
            sql_lines.append(line)
            if line.strip().endswith(';'):
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
    """Validate SQL with enhanced security checks and better handling of multi-line queries and subqueries."""
    if not query:
        return False
    
    # Normalize query - remove trailing semicolon and extra whitespace
    query = query.strip()
    if query.endswith(';'):
        query = query[:-1].strip()
    
    # Check if query is empty after normalization
    if not query:
        return False
    
    # Basic structure validation - must contain SELECT and FROM
    if 'SELECT' not in query.upper() or 'FROM' not in query.upper():
        current_app.logger.warning(f"SQL validation failed: Missing SELECT or FROM in query: {query}")
        return False
    
    # Check for balanced parentheses to ensure complete subqueries
    if query.count('(') != query.count(')'):
        current_app.logger.warning(f"SQL validation failed: Unbalanced parentheses in query: {query}")
        return False
    
    # Remove all known database prefixes from table references for validation
    original_query = query
    for db in databases.values():
        db_name = db['database']
        # Use regex to replace all instances of 'db_name.' with empty string
        query = re.sub(r'\b' + re.escape(db_name) + r'\.', '', query)
    
    if original_query != query:
        current_app.logger.debug(f"SQL before prefix stripping: {original_query}")
        current_app.logger.debug(f"SQL after prefix stripping (validation): {query}")
    
    # Convert to uppercase for keyword checking, preserving the original for logging
    q_upper = query.upper()
    
    # Expanded security checks - comprehensive list of forbidden SQL keywords
    forbidden_keywords = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", 
        "RENAME", "GRANT", "REVOKE", "--", "/*", "*/", "EXEC", "EXECUTE",
        "UNION", "INTO OUTFILE", "LOAD_FILE"
    }
    
    # Check for forbidden keywords - using word boundary checks to avoid false positives
    for kw in forbidden_keywords:
        # Use word boundary regex to avoid matching substrings within column names
        # For example, 'CREATE' shouldn't match 'CreatedBy' or 'CreatedAt'
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, q_upper):
            current_app.logger.warning(f"SQL validation failed: Forbidden keyword '{kw}' detected in: {query}")
            return False
    
    # Ensure query starts with SELECT (after normalization and whitespace removal)
    if not re.match(r'^\s*SELECT\b', query, re.IGNORECASE):
        current_app.logger.warning(f"SQL validation failed: Query does not start with SELECT: {query}")
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
    """Execute query with improved error handling and result processing.
    Now supports multiple SQL queries separated by semicolons."""
    if not query:
        return None
    
    # Check if we have multiple queries (separated by semicolons or newlines with SELECT)
    # First, normalize the query by ensuring semicolons at the end of each statement
    normalized_query = query.strip()
    
    # Add semicolons if missing at the end of statements
    if not normalized_query.endswith(';'):
        normalized_query += ';'
    
    # Split by semicolons but preserve complete SQL statements
    queries = []
    current_query = ''
    
    # Split the query more intelligently
    lines = normalized_query.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
            
        # If this is a new SELECT statement after we've already collected some SQL
        if line.upper().startswith('SELECT') and current_query.strip():
            # Ensure the previous query ends with a semicolon
            if not current_query.strip().endswith(';'):
                current_query += ';'
            queries.append(current_query.strip())
            current_query = line
        else:
            # Continue building the current query
            if current_query:
                current_query += '\n' + line
            else:
                current_query = line
    
    # Add the last query if it exists
    if current_query.strip():
        if not current_query.strip().endswith(';'):
            current_query += ';'
        queries.append(current_query.strip())
    
    # Alternative approach: split by semicolons and clean up
    if not queries:
        queries = [q.strip() for q in normalized_query.split(';') if q.strip()]
    
    # Log the detected queries
    if len(queries) > 1:
        current_app.logger.info(f"Processing multiple SQL queries: {len(queries)} queries detected")
        for i, q in enumerate(queries):
            current_app.logger.debug(f"Query {i+1}: {q}")
        
        # Execute each query and combine results
        all_results = []
        for i, single_query in enumerate(queries):
            current_app.logger.debug(f"Executing query {i+1}/{len(queries)}")
            result = execute_sql_query(single_query, params, preferred_db)
            if result:
                all_results.append(result)  # Keep each result set separate
        
        return all_results
    
    # Single query processing
    query = query.strip()
    if query.endswith(';'):
        query = query[:-1].strip()  # Remove trailing semicolon
        
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
    """Generate a natural language response with context about the query.
    Enhanced to handle complex multi-part queries and incorporate user preferences."""
    headers = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Check if we have multiple result sets from multiple queries
    is_multi_query = False
    if isinstance(query_result, list) and len(query_result) > 0:
        # Check if this is a list of result sets (each being a list)
        if all(isinstance(item, list) for item in query_result):
            is_multi_query = True
            current_app.logger.info(f"Processing response for multiple query results: {len(query_result)} result sets")

    # Enhanced system prompt for better responses
    system_prompt = """You are a helpful financial database assistant that explains results clearly. Follow these rules:
1. Respond in complete, friendly sentences that directly answer the user's question
2. NEVER mention SQL syntax or column names directly
3. Translate technical database terms into user-friendly language
4. For numerical results, format large numbers with commas (e.g., 1,234,567) but DO NOT include currency symbols
5. For empty results, explain possible reasons why no data was found
6. For complex queries with multiple parts, address each part of the question systematically
7. If there are multiple rows, summarize the overall pattern or highlight key findings
8. Avoid technical jargon unless the user specifically asks for technical details
9. ALWAYS be consistent in your response style and tone
10. For financial data, explain what the numbers represent but WITHOUT using currency terms
11. If the query is about a specific person, mention their name in the response
12. NEVER say 'I found X results' - instead provide the actual information
13. For loan data, when InstallmentAmount is not available, use OutstandingBalance as a substitute rather than PenaltyAmount
14. When discussing missed payments, ALWAYS include both the actual days in arrears AND the calculated number of missed installments (calculated as Math.ceil(days_in_arrears / 30))
15. For complex queries about borrowers, provide a comprehensive view including summary, history and character assessment when requested

# ACCOUNT SUMMARY FORMATTING RULES
When providing an account summary, use the following consistent format with clear section headers:

Here is the account summary for [Full Name]:

**Personal Information:**
- **Full Name:** [Name]
- **Phone Number:** [Phone]
- **Email:** [Email]

**Account Details:**
- **Account Balance:** [Balance with commas]
- **Shares:** [Shares with commas]

**Loan Information:**
- **Loan Amount:** [Amount with commas]
- **Loan Status:** [Status]
- **Application Date:** [Date]
- **Repayment Period:** [Period] months
- **Interest Rate:** [Rate]%

**Loan Ledger:**
- **Disbursed Amount:** [Amount with commas]
- **Outstanding Balance:** [Balance with commas]
- **Next Repayment Due Date:** [Date]
- **Missed Installments:** [Number]

Remember: When InstallmentAmount is not available, use OutstandingBalance as a substitute rather than PenaltyAmount. For missed payments, calculate based on the number of missed installments rather than using raw days in arrears."""

    # Add context about the number of results
    if is_multi_query:
        # For multiple result sets, provide context for each
        result_counts = [len(result_set) if result_set else 0 for result_set in query_result]
        result_preview = str([result_set[:2] if result_set else [] for result_set in query_result])
        result_count_str = f"Multiple result sets with counts: {result_counts}"
        full_results = json.dumps(query_result, default=str)
    else:
        # Single result set
        result_count = len(query_result) if query_result else 0
        result_preview = str(query_result[:3]) if query_result else "[]"
        result_count_str = f"Number of results: {result_count}"
        full_results = json.dumps(query_result, default=str)
    
    # Extract key entities from the user's question for better context
    user_question = user_input.strip()
    
    # Check for specific query types that need special handling
    is_complex_borrower_query = any(term in user_question.lower() for term in [
        "borrowing history", "repayment history", "borrowing character", "credit history", "loan summary"
    ])
    
    # Detect account summary requests
    is_account_summary = any(pattern in user_question.lower() for pattern in [
        "account summary", "customer summary", "member summary", 
        "account details for", "summary for", "information about",
        "tell me about", "show me details for", "give me account",
        "account history", "transaction history", "payment history"
    ])
    
    # Determine if this is a query about missed payments or delinquent loans
    is_missed_payment_query = any(term in user_question.lower() for term in [
        "missed payment", "late payment", "arrears", "overdue", "delinquent", "deliquent", 
        "defaulted", "default", "behind on", "top arrears", "highest arrears", "most overdue",
        "past due", "non-performing", "npl"
    ])
    
    # Detect loan performance and monitoring queries
    is_loan_monitoring_query = any(pattern in user_question.lower() for pattern in [
        "outstanding balance", "due this week", "due next week", "due soon", "due date",
        "disbursed in", "disbursed last", "recently disbursed", "new loans",
        "active loans", "current status", "loan status", "loan id", "loan account",
        "not received", "no repayment", "restructured", "rescheduled"
    ])
    
    # Detect repayment and schedule queries
    is_repayment_query = any(pattern in user_question.lower() for pattern in [
        "repayment schedule", "payment schedule", "installment schedule", "amortization",
        "missed installment", "missed payment", "next repayment", "next payment", "next installment",
        "partial repayment", "partial payment", "received payment", "received repayment",
        "repayments made", "payments made", "repayment pattern", "payment pattern", "irregular payment"
    ])
    
    # Detect portfolio analytics queries
    is_portfolio_analytics_query = any(pattern in user_question.lower() for pattern in [
        "portfolio value", "total portfolio", "delinquency rate", "breakdown of loans",
        "top clients", "top borrowers", "top loans", "loans by branch", "branch performance",
        "disbursement trends", "loan trends", "average loan", "loan officer", "portfolio at risk",
        "par report", "par30", "par60", "par90", "loan portfolio", "product type"
    ])
    
    # Detect client/member queries
    is_client_query = any(pattern in user_question.lower() for pattern in [
        "loan history", "member id", "client id", "contact information", "phone number", "email",
        "multiple loans", "active loans", "cleared loans", "paid off", "settled", "credit score",
        "risk rating", "collateral", "guarantor", "member details", "client details", "borrower details"
    ]) or re.search(r'\bmember\s+\w+\s+\w+', user_question.lower()) is not None
    
    # Detect alerts and exceptions queries
    is_alert_query = any(pattern in user_question.lower() for pattern in [
        "exceeded", "grace period", "without guarantors", "no guarantor", "missing guarantor",
        "less than scheduled", "underpayment", "no follow-up", "incomplete documentation",
        "missing document", "not yet disbursed", "system mismatch", "cbs", "exception",
        "alert", "violation", "deficiency", "irregularity", "compliance issue"
    ])
    
    # Detect guarantors and collateral queries
    is_guarantor_collateral_query = any(pattern in user_question.lower() for pattern in [
        "guarantor", "guarantors", "collateral", "security", "secured by", "backed by",
        "loan security", "asset", "pledge", "pledged", "guarantee", "guaranteed by"
    ])
    
    # Detect rescheduling, top-ups, and restructuring queries
    is_loan_modification_query = any(pattern in user_question.lower() for pattern in [
        "topped up", "top-up", "topup", "top up", "additional loan", "loan extension",
        "rescheduled", "reschedule", "restructured", "restructuring", "restructure",
        "modified", "modification", "refinanced", "refinance", "eligible for"
    ])
    
    # Detect officer/branch performance queries
    is_performance_query = any(pattern in user_question.lower() for pattern in [
        "officer", "branch", "managed by", "handled by", "performance", "npl ratio",
        "non-performing", "disbursed by", "portfolio quality", "portfolio size",
        "repayment performance", "collection rate", "disbursement target", "highest", "lowest"
    ])
    
    # Add special instructions based on query type
    special_instructions = ""
    
    # For account summaries
    if is_account_summary:
        special_instructions = """This appears to be a request for an account summary. 
Please provide a comprehensive summary that includes:
1. Personal information (name, contact details, etc.)
2. Account details (balance, shares, etc.)
3. Loan information (amount, status, terms, etc.)
4. Loan ledger details (outstanding balance, next payment, etc.)

IMPORTANT: 
- When InstallmentAmount is not available, use OutstandingBalance as a substitute rather than PenaltyAmount
- For missed payments, calculate based on the number of missed installments rather than using raw days in arrears
- Format the response as a structured account summary with clear sections"""
    
    # For officer/branch performance queries
    elif is_performance_query:
        # Check for specific performance query types
        if re.search(r'(officer|managed by|handled by)\s+\w+\s+\w+', user_question.lower()):
            special_instructions = """This appears to be a query about loans managed by a specific loan officer.

IMPORTANT:
- Present the officer information at the top (name, ID, branch, etc.)
- List all loans in a clear, structured format
- For each loan, include loan ID, borrower name, amount, disbursement date, and current status
- Format large numbers with commas (e.g., 1,234,567)
- Order by disbursement date (most recent first)
- Include summary statistics (total number of loans, total portfolio value, etc.)
- Highlight any non-performing loans in the officer's portfolio"""
        elif "repayment performance" in user_question.lower() or ("performance" in user_question.lower() and "officer" in user_question.lower()):
            special_instructions = """This appears to be a query about repayment performance by loan officer.

IMPORTANT:
- Present the results as a clear, structured table or list of officers
- For each officer, include name, ID, and key performance metrics
- Include metrics such as collection rate, on-time payment percentage, and PAR ratio
- Format percentages with one decimal place (e.g., 95.5%)
- Format large numbers with commas (e.g., 1,234,567)
- Order by performance metric (best performing first)
- Include the number and value of loans managed by each officer
- Highlight top performers and those needing improvement"""
        elif "disbursed by branch" in user_question.lower() or ("branch" in user_question.lower() and "last 3 months" in user_question.lower()):
            special_instructions = """This appears to be a query about loans disbursed by a specific branch in a time period.

IMPORTANT:
- Present the branch information at the top (name, location, etc.)
- List all loans in a clear, structured format
- For each loan, include loan ID, borrower name, amount, and disbursement date
- Format large numbers with commas (e.g., 1,234,567)
- Order by disbursement date (most recent first)
- Include summary statistics (total number of loans, total disbursed amount, etc.)
- Compare to previous periods if data is available"""
        elif "npl ratio" in user_question.lower() or "non-performing" in user_question.lower():
            special_instructions = """This appears to be a query about officers with the highest NPL (Non-Performing Loan) ratio.

IMPORTANT:
- Present the results as a clear, structured table or list of officers
- For each officer, include name, ID, NPL ratio, and portfolio details
- Calculate NPL ratio as (Value of Non-Performing Loans / Total Portfolio Value) * 100
- Format percentages with one decimal place (e.g., 5.2%)
- Format large numbers with commas (e.g., 1,234,567)
- Order by NPL ratio (highest first)
- Include the number of loans and number of non-performing loans
- Highlight officers with concerning NPL ratios"""
        else:
            special_instructions = """This appears to be a query about officer or branch performance.

IMPORTANT:
- Present the results in a clear, structured format appropriate to the query
- Include relevant performance metrics based on the query context
- Format percentages with one decimal place (e.g., 95.5%)
- Format large numbers with commas (e.g., 1,234,567)
- Order results in a logical manner based on the query context
- Include summary statistics where appropriate
- Highlight notable performers (both positive and concerning)"""
    
    # For rescheduling, top-ups, and restructuring queries
    elif is_loan_modification_query:
        # Check for specific loan modification query types
        if any(term in user_question.lower() for term in ["topped up", "top-up", "topup", "top up"]) and re.search(r'loan\s+\d+', user_question.lower()):
            special_instructions = """This appears to be a query about whether a specific loan has been topped up.

IMPORTANT:
- Present the original loan information at the top (loan ID, amount, borrower, etc.)
- Clearly state whether the loan has been topped up or not
- If topped up, provide details of each top-up (amount, date, purpose)
- Calculate and show the total loan amount (original + top-ups)
- Format large numbers with commas (e.g., 1,234,567)
- Include the current status of the loan after top-ups
- If not topped up, indicate if the loan is eligible for top-up"""
        elif any(term in user_question.lower() for term in ["rescheduled", "reschedule"]) and "past 6 months" in user_question.lower():
            special_instructions = """This appears to be a query about rescheduled loans in the past 6 months.

IMPORTANT:
- Present the results as a clear, numbered list of rescheduled loans
- For each loan, include loan ID, borrower name, original terms, and new terms
- Show the rescheduling date and reason (if available)
- Format large numbers with commas (e.g., 1,234,567)
- Order by rescheduling date (most recent first)
- Include the total number of rescheduled loans in the specified period
- Highlight any loans that have been rescheduled multiple times"""
        elif any(term in user_question.lower() for term in ["restructuring", "restructure"]) and "pending" in user_question.lower():
            special_instructions = """This appears to be a query about loans with pending restructuring requests.

IMPORTANT:
- Present the results as a clear, numbered list of loans with pending restructuring
- For each loan, include loan ID, borrower name, current terms, and proposed terms
- Show the date the restructuring was requested and current status
- Format large numbers with commas (e.g., 1,234,567)
- Order by request date (oldest first)
- Include the total number of pending restructuring requests
- Highlight requests that have been pending for an extended period"""
        elif any(term in user_question.lower() for term in ["eligible", "qualify"]) and any(term in user_question.lower() for term in ["top-up", "topup", "top up"]):
            special_instructions = """This appears to be a query about loans eligible for top-up.

IMPORTANT:
- Present the results as a clear, numbered list of eligible loans
- For each loan, include loan ID, borrower name, current loan amount, and potential top-up amount
- Show the eligibility criteria that have been met (e.g., percentage repaid, time elapsed)
- Format large numbers with commas (e.g., 1,234,567)
- Order by potential top-up amount (highest first)
- Include the total number of loans eligible for top-up
- Highlight high-value top-up opportunities"""
        else:
            special_instructions = """This appears to be a query about loan modifications (top-ups, rescheduling, or restructuring).

IMPORTANT:
- Present the results in a clear, structured format appropriate to the query
- Include all relevant loan and modification details based on the query context
- Format large numbers with commas (e.g., 1,234,567)
- Order results in a logical manner based on the query context
- Include summary statistics where appropriate (totals, averages, etc.)
- Highlight any unusual or significant modifications"""
    
    # For guarantors and collateral queries
    elif is_guarantor_collateral_query:
        # Check for specific guarantor/collateral query types
        if re.search(r'guarantors?\s+for\s+loan', user_question.lower()):
            special_instructions = """This appears to be a query about guarantors for a specific loan.

IMPORTANT:
- Present the loan information at the top (loan ID, amount, borrower, etc.)
- List all guarantors in a clear, structured format
- For each guarantor, include name, ID, relationship to borrower, and contact details
- Include the guaranteed amount or percentage for each guarantor if available
- Format large numbers with commas (e.g., 1,234,567)
- Indicate whether the guarantor coverage is sufficient for the loan amount
- Protect sensitive personal information"""
        elif re.search(r'guarantors?\s+to\s+multiple', user_question.lower()) or "multiple loans" in user_question.lower():
            special_instructions = """This appears to be a query about members who are guarantors to multiple loans.

IMPORTANT:
- Present the results as a clear, numbered list of guarantors
- For each guarantor, include name, ID, and the number of loans guaranteed
- Provide a brief summary of each guaranteed loan (borrower, amount, status)
- Format large numbers with commas (e.g., 1,234,567)
- Order by number of loans guaranteed (highest first)
- Include the total exposure for each guarantor (sum of guaranteed amounts)
- Protect sensitive personal information"""
        elif re.search(r'value\s+of\s+collateral', user_question.lower()):
            special_instructions = """This appears to be a query about collateral value for a specific loan.

IMPORTANT:
- Present the loan information at the top (loan ID, amount, borrower, etc.)
- List all collateral items in a clear, structured format
- For each collateral item, include type, description, and valuation
- Calculate and show the total collateral value prominently
- Format large numbers with commas (e.g., 1,234,567)
- Compare the total collateral value to the loan amount (as a percentage)
- Indicate whether the collateral coverage is sufficient for the loan amount"""
        elif "backed only by guarantors" in user_question.lower() or "no collateral" in user_question.lower():
            special_instructions = """This appears to be a query about loans backed only by guarantors with no collateral.

IMPORTANT:
- Present the results as a clear, numbered list of loans
- For each loan, include loan ID, borrower name, loan amount, and disbursement date
- List the guarantors for each loan with their guaranteed amounts
- Format large numbers with commas (e.g., 1,234,567)
- Order by loan amount (highest first)
- Include the total number and value of loans backed only by guarantors
- Highlight high-value loans with insufficient guarantor coverage"""
        else:
            special_instructions = """This appears to be a query about loan guarantors or collateral.

IMPORTANT:
- Present the results in a clear, structured format appropriate to the query
- Include all relevant guarantor or collateral details based on the query context
- Format large numbers with commas (e.g., 1,234,567)
- Order results in a logical manner based on the query context
- Highlight any security coverage issues or discrepancies
- Protect sensitive personal information"""
    
    # For alerts and exceptions queries
    elif is_alert_query:
        # Check for specific alert/exception query types
        if any(term in user_question.lower() for term in ["exceeded", "grace period"]):
            special_instructions = """This appears to be a query about loans that have exceeded their grace period.

IMPORTANT:
- Present the results as a clear, numbered list with a warning header
- For each loan, include loan ID, customer name, grace period end date, and days past grace period
- Format large numbers with commas (e.g., 1,234,567)
- Order by days past grace period (highest first)
- Include the total number of loans that have exceeded the grace period
- Highlight loans that are significantly past the grace period (e.g., >30 days)
- Include recommended actions for follow-up"""
        elif any(term in user_question.lower() for term in ["without guarantors", "no guarantor", "missing guarantor"]):
            special_instructions = """This appears to be a query about loans disbursed without guarantors.

IMPORTANT:
- Present the results as a clear, numbered list with a warning header
- For each loan, include loan ID, customer name, loan amount, and disbursement date
- Format large numbers with commas (e.g., 1,234,567)
- Order by loan amount (highest first)
- Include the total number and value of loans without guarantors
- Highlight high-value loans (e.g., top 25% by amount)
- Include recommended actions for compliance"""
        elif any(term in user_question.lower() for term in ["less than scheduled", "underpayment"]):
            special_instructions = """This appears to be a query about loans with repayment amounts less than scheduled.

IMPORTANT:
- Present the results as a clear, numbered list with a warning header
- For each loan, include loan ID, customer name, scheduled amount, actual amount, and shortfall
- Calculate and show the shortfall percentage
- Format large numbers with commas (e.g., 1,234,567)
- Order by shortfall percentage (highest first)
- Include the total number of loans with underpayments
- Highlight loans with significant shortfalls (e.g., >25%)
- Include recommended actions for collection"""
        elif any(term in user_question.lower() for term in ["no follow-up", "follow up"]):
            special_instructions = """This appears to be a query about overdue loans with no follow-up records.

IMPORTANT:
- Present the results as a clear, numbered list with a warning header
- For each loan, include loan ID, customer name, days overdue, and last contact date (if available)
- Format large numbers with commas (e.g., 1,234,567)
- Order by days overdue (highest first)
- Include the total number of overdue loans without follow-up
- Highlight loans that are significantly overdue (e.g., >30 days)
- Include recommended actions for immediate follow-up"""
        elif any(term in user_question.lower() for term in ["incomplete documentation", "missing document"]):
            special_instructions = """This appears to be a query about loans with incomplete documentation.

IMPORTANT:
- Present the results as a clear, numbered list with a warning header
- For each loan, include loan ID, customer name, loan amount, and missing document types
- Format large numbers with commas (e.g., 1,234,567)
- Order by loan amount (highest first)
- Include the total number of loans with incomplete documentation
- Highlight loans with critical missing documents
- Include recommended actions for document collection"""
        elif any(term in user_question.lower() for term in ["not yet disbursed", "system mismatch", "cbs"]):
            special_instructions = """This appears to be a query about system synchronization issues.

IMPORTANT:
- Present the results as a clear, numbered list with a warning header
- For each loan, include loan ID, customer name, loan amount, and disbursement date
- Format large numbers with commas (e.g., 1,234,567)
- Order by disbursement date (most recent first)
- Include the total number and value of loans with synchronization issues
- Highlight loans disbursed more than 7 days ago
- Include recommended actions for system reconciliation"""
        else:
            special_instructions = """This appears to be a query about loan exceptions or alerts.

IMPORTANT:
- Present the results as a clear, numbered list with a warning header
- For each exception, include loan ID, customer name, and specific exception details
- Format large numbers with commas (e.g., 1,234,567)
- Order by severity or risk level (highest first)
- Include the total number of exceptions found
- Highlight high-risk or urgent exceptions
- Include recommended actions for resolution"""
    
    # For client/member queries
    elif is_client_query:
        # Check for specific client/member query types
        if any(term in user_question.lower() for term in ["loan history", "loan details"]):
            special_instructions = """This appears to be a query about a member's loan history.

IMPORTANT:
- Present the member's information at the top (name, ID, etc.)
- List their loans in chronological order (most recent first)
- For each loan, include loan ID, amount, disbursement date, status, and repayment status
- Format large numbers with commas (e.g., 1,234,567)
- Include a summary of their overall borrowing history (total loans, repayment performance)
- Highlight any current active loans
- Protect sensitive personal information"""
        elif any(term in user_question.lower() for term in ["contact information", "phone number", "email", "address"]):
            special_instructions = """This appears to be a query about a member's contact information.

IMPORTANT:
- Present the member's basic information clearly (name, ID, etc.)
- Include contact details in a structured format
- Protect sensitive personal information
- Do not include financial details unless specifically requested
- Format phone numbers consistently
- If multiple contact methods are available, include all of them"""
        elif any(term in user_question.lower() for term in ["multiple loans", "active loans", "more than one"]):
            special_instructions = """This appears to be a query about members with multiple loans.

IMPORTANT:
- Present the results as a clear, numbered list of members
- For each member, include name, ID, and the number of active loans
- Provide a brief summary of each loan (amount, purpose, status)
- Format large numbers with commas (e.g., 1,234,567)
- Order by number of active loans (highest first)
- Include the total number of members with multiple loans
- Protect sensitive personal information"""
        elif any(term in user_question.lower() for term in ["cleared loans", "paid off", "settled", "completed"]):
            special_instructions = """This appears to be a query about members who have cleared their loans.

IMPORTANT:
- Present the results as a clear, numbered list of members
- For each member, include name, ID, and details of the cleared loan
- Include the date when the loan was fully paid off
- Format large numbers with commas (e.g., 1,234,567)
- Order by clearance date (most recent first)
- Include the total number of members who cleared loans in the specified period
- Protect sensitive personal information"""
        elif any(term in user_question.lower() for term in ["credit score", "risk rating", "creditworthiness"]):
            special_instructions = """This appears to be a query about a member's credit score or risk rating.

IMPORTANT:
- Present the member's basic information at the top (name, ID, etc.)
- Show their credit score or risk rating prominently
- Explain what the score/rating means in simple terms
- Include relevant factors that contribute to the rating
- Summarize their loan repayment history if available
- Protect sensitive personal information
- Do not make subjective judgments about the member's creditworthiness"""
        elif any(term in user_question.lower() for term in ["collateral", "security", "guarantee", "guarantor"]):
            special_instructions = """This appears to be a query about loans with collateral.

IMPORTANT:
- Present the results as a clear, numbered list of members or loans
- For each entry, include member name, loan details, and collateral information
- Format large numbers with commas (e.g., 1,234,567)
- Include the type and value of collateral for each loan
- If guarantors are involved, include their relationship to the borrower
- Order by loan amount (highest first)
- Protect sensitive personal information"""
        else:
            special_instructions = """This appears to be a query about specific members or clients.

IMPORTANT:
- Present the member information in a clear, structured format
- Include only the information specifically requested in the query
- Format large numbers with commas (e.g., 1,234,567)
- Order results in a logical manner based on the query context
- Protect sensitive personal information
- For financial data, explain what the numbers represent"""
    
    # For portfolio analytics queries
    elif is_portfolio_analytics_query:
        # Check for specific portfolio analytics query types
        if any(term in user_question.lower() for term in ["portfolio value", "total portfolio", "loan portfolio"]):
            special_instructions = """This appears to be a query about the total loan portfolio value.

IMPORTANT:
- Present the total portfolio value prominently at the beginning of your response
- Format large numbers with commas (e.g., 1,234,567)
- Include a breakdown by loan status if available (active, closed, etc.)
- Include the total number of loans in the portfolio
- If relevant, include a brief comparison to previous periods"""
        elif any(term in user_question.lower() for term in ["delinquency rate"]):
            special_instructions = """This appears to be a query about delinquency rate.

IMPORTANT:
- Present the delinquency rate prominently as a percentage
- Include the formula used: Delinquency Rate = (Value of Loans in Arrears / Total Portfolio Value) * 100
- Include the total value of loans in arrears and the total portfolio value
- Format large numbers with commas (e.g., 1,234,567)
- If the query specifies a time period, clearly indicate this in your response
- If available, include a comparison to previous periods or industry benchmarks"""
        elif any(term in user_question.lower() for term in ["breakdown", "by product", "product type"]):
            special_instructions = """This appears to be a query about loan breakdown by product type.

IMPORTANT:
- Present the results as a clear, structured table or list
- For each product type, include the number of loans, total value, and percentage of portfolio
- Order by loan value (highest first)
- Format large numbers with commas (e.g., 1,234,567)
- Include totals at the end
- Highlight the product types with the highest concentration"""
        elif any(term in user_question.lower() for term in ["top clients", "top borrowers", "top loans"]):
            special_instructions = """This appears to be a query about top clients or loans.

IMPORTANT:
- Present the results as a clear, numbered list (1 to 10 or as specified)
- For each client/loan, include client name, loan details, and outstanding balance
- Format large numbers with commas (e.g., 1,234,567)
- Include the percentage of the total portfolio for each top client
- Order by outstanding balance (highest first)"""
        elif any(term in user_question.lower() for term in ["by branch", "branch performance"]):
            special_instructions = """This appears to be a query about branch performance.

IMPORTANT:
- Present the results as a clear, structured table or list
- For each branch, include the number of loans disbursed and total value
- Calculate and show the percentage of total disbursements for each branch
- Format large numbers with commas (e.g., 1,234,567)
- Order by number of loans or total value (highest first)
- Highlight the top performing branches"""
        elif any(term in user_question.lower() for term in ["trends", "past 6 months", "over time"]):
            special_instructions = """This appears to be a query about loan trends over time.

IMPORTANT:
- Present the results as a clear, chronological table or list
- For each period (month/quarter), include the number of loans disbursed and total value
- Calculate and show the percentage change between periods
- Format large numbers with commas (e.g., 1,234,567)
- Highlight significant trends or changes
- Summarize the overall trend at the beginning or end of your response"""
        elif any(term in user_question.lower() for term in ["average loan", "loan officer", "by officer"]):
            special_instructions = """This appears to be a query about loan officer performance.

IMPORTANT:
- Present the results as a clear, structured table or list
- For each loan officer, include name, number of loans, total value, and average loan amount
- Format large numbers with commas (e.g., 1,234,567)
- Order by average loan amount or total value (highest first)
- Highlight top performing loan officers
- Include overall averages for comparison"""
        elif any(term in user_question.lower() for term in ["portfolio at risk", "par report", "par30", "par60", "par90"]):
            special_instructions = """This appears to be a query about Portfolio at Risk (PAR).

IMPORTANT:
- Present the PAR values prominently as percentages
- Include the formula used: PAR = (Value of Loans with Arrears > X days / Total Portfolio Value) * 100
- Show PAR30, PAR60, and PAR90 values separately
- Include the total value of at-risk loans for each PAR category
- Format large numbers with commas (e.g., 1,234,567)
- If available, include a comparison to previous periods or industry benchmarks
- Highlight any concerning trends or values"""
        else:
            special_instructions = """This appears to be a portfolio analytics query.

IMPORTANT:
- Present the results in a clear, structured format appropriate to the query
- Include relevant metrics and calculations based on the query context
- Format large numbers with commas (e.g., 1,234,567)
- Highlight key insights or findings
- Include totals and percentages where relevant
- Order results logically based on the query context"""
    
    # For repayment and schedule queries
    elif is_repayment_query:
        # Check for specific repayment query types
        if any(term in user_question.lower() for term in ["repayment schedule", "payment schedule", "installment schedule", "amortization"]):
            special_instructions = """This appears to be a query about a loan's repayment schedule.

IMPORTANT:
- Present the repayment schedule as a clear, chronological table or list
- Include payment number, due date, installment amount, principal, interest, and balance
- Highlight any missed or upcoming payments
- Format large numbers with commas (e.g., 1,234,567)
- Include loan summary information (amount, term, interest rate) at the beginning"""
        elif any(term in user_question.lower() for term in ["missed installment", "missed payment", "missed their last"]):
            special_instructions = """This appears to be a query about missed installments.

IMPORTANT:
- Present the results as a clear, numbered list of members with missed installments
- For each member, include name, loan ID, due date, days overdue, and installment amount
- Include both the actual days in arrears AND the calculated number of missed installments (using Math.ceil(days_in_arrears / 30))
- Format large numbers with commas (e.g., 1,234,567)
- Order the results by severity (most overdue first)
- If the list is long, summarize the total number of members with missed installments
- Keep the response concise and focused on the most critical information"""
        elif any(term in user_question.lower() for term in ["next repayment", "next payment", "next installment"]):
            special_instructions = """This appears to be a query about upcoming repayment dates.

IMPORTANT:
- Present the next repayment information in a clear, structured format
- Include member name, loan ID, next payment date, and installment amount
- If available, include the loan balance and payment history summary
- Format large numbers with commas (e.g., 1,234,567)
- Clearly indicate how many days until the next payment is due"""
        elif any(term in user_question.lower() for term in ["partial repayment", "partial payment"]):
            special_instructions = """This appears to be a query about partial repayments.

IMPORTANT:
- Present the results as a clear, numbered list of partial payments
- For each payment, include member name, loan ID, payment date, actual amount, and scheduled amount
- Calculate and show the shortfall amount and percentage
- Format large numbers with commas (e.g., 1,234,567)
- Include the total number and value of partial payments in the specified period"""
        elif any(term in user_question.lower() for term in ["received payment", "received repayment", "repayments made", "payments made"]):
            special_instructions = """This appears to be a query about received payments.

IMPORTANT:
- Present the results as a clear, numbered list of received payments
- For each payment, include member name, loan ID, payment date, and amount
- Format large numbers with commas (e.g., 1,234,567)
- Include the total number and value of payments in the specified period
- Group by loan or member if there are multiple payments for the same loan"""
        elif any(term in user_question.lower() for term in ["repayment pattern", "payment pattern", "irregular payment"]):
            special_instructions = """This appears to be a query about repayment patterns.

IMPORTANT:
- Present the results as a clear, numbered list of loans with irregular patterns
- For each loan, include member name, loan ID, and description of the irregularity
- Include specific examples of irregular payments (late, early, partial, etc.)
- Format large numbers with commas (e.g., 1,234,567)
- Summarize the overall pattern and potential concerns"""
        else:
            special_instructions = """This appears to be a query about loan repayments or schedules.

IMPORTANT:
- Present the results in a clear, structured format appropriate to the query
- Include all relevant payment details based on the query context
- Format large numbers with commas (e.g., 1,234,567)
- Order the results in a logical manner (by date, amount, or status as appropriate)
- For queries involving missed payments, include both days in arrears AND missed installments"""
    
    # For loan monitoring queries
    elif is_loan_monitoring_query:
        # Check for specific loan monitoring query types
        if "outstanding balance" in user_question.lower() or "loan account" in user_question.lower():
            special_instructions = """This appears to be a query about a specific loan's outstanding balance.

IMPORTANT:
- Present the loan information in a clear, structured format
- Include the loan account number, customer name, and outstanding balance
- Format large numbers with commas (e.g., 1,234,567)
- If available, include the original loan amount and disbursement date for context
- When InstallmentAmount is not available, use OutstandingBalance as a substitute"""
        elif any(term in user_question.lower() for term in ["due this week", "due next week", "due soon", "due date"]):
            special_instructions = """This appears to be a query about loans due soon.

IMPORTANT:
- Present the results as a clear, numbered list of upcoming loan payments
- For each loan, include customer name, loan ID, due date, and payment amount
- Order the results by due date (earliest first)
- Format large numbers with commas (e.g., 1,234,567)
- Include the total number of loans due in the specified period"""
        elif "disbursed" in user_question.lower() or "new loans" in user_question.lower():
            special_instructions = """This appears to be a query about recently disbursed loans.

IMPORTANT:
- Present the results as a clear, numbered list of recently disbursed loans
- For each loan, include customer name, loan ID, disbursement date, and loan amount
- Order the results by disbursement date (most recent first)
- Format large numbers with commas (e.g., 1,234,567)
- Include the total number and value of loans disbursed in the specified period"""
        elif "active loans" in user_question.lower():
            special_instructions = """This appears to be a query about active loans for a specific member.

IMPORTANT:
- Present the results as a clear, numbered list of active loans
- For each loan, include loan ID, disbursement date, loan amount, and outstanding balance
- Order the results by disbursement date (most recent first)
- Format large numbers with commas (e.g., 1,234,567)
- Include the total number and combined outstanding balance of all active loans"""
        elif "status" in user_question.lower():
            special_instructions = """This appears to be a query about a loan's current status.

IMPORTANT:
- Present the loan information in a clear, structured format with sections
- Include comprehensive loan details: ID, customer name, status, disbursement date, etc.
- If in arrears, include both days in arrears AND missed installments (calculated as Math.ceil(days_in_arrears / 30))
- Format large numbers with commas (e.g., 1,234,567)
- Include payment history summary if available"""
        elif "not received" in user_question.lower() or "no repayment" in user_question.lower():
            special_instructions = """This appears to be a query about loans without recent repayments.

IMPORTANT:
- Present the results as a clear, numbered list of loans without recent payments
- For each loan, include customer name, loan ID, last payment date, and outstanding balance
- Order the results by last payment date (oldest first)
- Format large numbers with commas (e.g., 1,234,567)
- Include both days since last payment AND missed installments (calculated as Math.ceil(days_in_arrears / 30))"""
        elif "restructured" in user_question.lower() or "rescheduled" in user_question.lower():
            special_instructions = """This appears to be a query about restructured loans.

IMPORTANT:
- Present the results as a clear, numbered list of restructured loans
- For each loan, include customer name, loan ID, restructuring date, and new terms
- Order the results by restructuring date (most recent first)
- Format large numbers with commas (e.g., 1,234,567)
- Include the original loan terms for comparison where available"""
        else:
            special_instructions = """This appears to be a loan monitoring query.

IMPORTANT:
- Present the results in a clear, structured format (numbered list or sections as appropriate)
- Include all relevant loan details based on the query context
- Order the results in a logical manner (by date, amount, or status as appropriate)
- Format large numbers with commas (e.g., 1,234,567)
- For queries involving arrears, include both days in arrears AND missed installments (calculated as Math.ceil(days_in_arrears / 30))"""

    
    # For complex borrower queries
    elif is_complex_borrower_query:
        special_instructions = """This appears to be a complex query about a borrower's history and character. 
Please provide a comprehensive response that includes:
1. A summary of their borrowing activity
2. Their repayment behavior and any patterns
3. An assessment of their borrowing character based on the data
4. Any notable trends or concerns

IMPORTANT: 
- When InstallmentAmount is not available, use OutstandingBalance as a substitute rather than PenaltyAmount
- For missed payments, calculate based on the number of missed installments rather than using raw days in arrears"""
    
    # For missed payment queries
    elif is_missed_payment_query:
        # Check if this is a ranking query (top N delinquent loans)
        is_ranking_query = any(term in user_question.lower() for term in ["top", "highest", "most", "worst", "ranking", "list"])
        
        if is_ranking_query:
            special_instructions = """This appears to be a query about ranking delinquent loans.

IMPORTANT: 
- Present the results as a ranked list of delinquent borrowers
- For each borrower, include their name, loan details, days in arrears, and missed installments
- ALWAYS include both the actual days in arrears value AND the calculated number of missed installments
- Calculate missed installments using the formula: Math.ceil(days_in_arrears / 30)
- Include the outstanding balance for each loan
- Format the response as a clear, numbered list
- When InstallmentAmount is not available, use OutstandingBalance as a substitute rather than PenaltyAmount"""
        else:
            special_instructions = """This appears to be a query about missed payments or arrears.

IMPORTANT: 
- ALWAYS include both the actual days in arrears value AND the calculated number of missed installments
- Calculate missed installments using the formula: Math.ceil(days_in_arrears / 30)
- Include the outstanding balance in your response
- When InstallmentAmount is not available, use OutstandingBalance as a substitute rather than PenaltyAmount"""
    
    user_content = f"""Original question: {user_question}
SQL query executed: {sql_query}
{result_count_str}
Database results preview: {result_preview}
Full results: {full_results}
{special_instructions}

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

# Import the ChatMessage model
from models.chat_message import ChatMessage
from models.legal_case import CaseHistory
from models.case_history_attachment import CaseHistoryAttachment

# Chat history table creation
def ensure_chat_tables_exist():
    """Ensure that the chat_messages table exists in the database."""
    try:
        # Use SQLAlchemy to create the table
        db.create_all()
        return True
    except Exception as e:
        current_app.logger.error(f"Error creating chat tables: {str(e)}")
        return False

# Note: Chat tables will be created when the app starts in app.py

def save_chat_message(user_id, conversation_id, message, response, sql_query=None, database_used=None):
    """Save a chat message and its response to the database using the ChatMessage model."""
    try:
        # Create a new ChatMessage instance
        chat_message = ChatMessage(
            user_id=user_id,
            conversation_id=conversation_id,
            message=message,
            response=response,
            sql_query=sql_query,
            database_used=database_used
        )
        
        # Add to the database and commit
        db.session.add(chat_message)
        db.session.commit()
        
        # Log successful save
        current_app.logger.info(
            f"Chat message saved successfully: ID={chat_message.id}, "
            f"conversation_id={conversation_id}, user_id={user_id}"
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving chat message: {str(e)}")
        db.session.rollback()
        return False

def get_conversation_history(conversation_id, limit=10):
    """Get the conversation history for a specific conversation ID using the ChatMessage model."""
    try:
        # Query the database using SQLAlchemy
        messages = ChatMessage.query.filter_by(conversation_id=conversation_id).order_by(ChatMessage.timestamp.asc()).limit(limit).all()
        
        # Convert to dictionaries for JSON serialization
        return [message.to_dict() for message in messages]
    except Exception as e:
        current_app.logger.error(f"Error retrieving conversation history: {str(e)}")
        return []

@user_bp.route('/chat_history', methods=['GET'])
def get_chat_history():
    """Get chat history for a user or conversation using the ChatMessage model."""
    conversation_id = request.args.get('conversation_id')
    user_id = request.args.get('user_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    
    try:
        if conversation_id:
            # Get messages for a specific conversation
            messages = ChatMessage.query.filter_by(conversation_id=conversation_id).order_by(ChatMessage.timestamp.asc()).limit(limit).all()
            results = [message.to_dict() for message in messages]
        elif user_id:
            # Get all conversations for a user
            # Using SQLAlchemy to get distinct conversations with metadata
            from sqlalchemy import func, desc
            conversations = db.session.query(
                ChatMessage.conversation_id,
                func.min(ChatMessage.timestamp).label('started_at'),
                func.max(ChatMessage.timestamp).label('last_message'),
                func.count(ChatMessage.id).label('message_count')
            ).filter(
                ChatMessage.user_id == user_id
            ).group_by(
                ChatMessage.conversation_id
            ).order_by(
                desc('last_message')
            ).limit(limit).all()
            
            # Convert to dictionary format
            results = []
            for conv in conversations:
                results.append({
                    'conversation_id': conv.conversation_id,
                    'started_at': conv.started_at.isoformat() if conv.started_at else None,
                    'last_message': conv.last_message.isoformat() if conv.last_message else None,
                    'message_count': conv.message_count
                })
        else:
            return jsonify({'error': 'Missing conversation_id or user_id parameter'}), 400
        
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error retrieving chat history: {str(e)}")
        return jsonify({'error': 'Failed to retrieve chat history'}), 500



@user_bp.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400

    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
        
    # Get conversation ID (create a new one if not provided)
    conversation_id = request.json.get('conversation_id')
    if not conversation_id:
        conversation_id = f"conv_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Get user ID (default to 1 if not provided)
    user_id = request.json.get('user_id', 1)

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

        # Get conversation history for context
        conversation_history = get_conversation_history(conversation_id, limit=5)
        
        # Format conversation history for the API
        chat_context = []
        for msg in conversation_history:
            chat_context.append({
                'user_message': msg['message'],
                'assistant_response': msg['response']
            })
            
        # Step 1: Get raw AI response with database preference and conversation history
        # Add retry logic at this level too for more resilience
        retry_attempts = 2  # Number of retries at this level
        for attempt in range(retry_attempts + 1):
            raw_response = call_mistral_api(user_input, preferred_db, chat_context)
            if raw_response:
                break  # Success, exit the retry loop
            elif attempt < retry_attempts:
                # Log the retry attempt
                current_app.logger.warning(f"API call failed, retrying at chat level ({attempt+1}/{retry_attempts})...")
                time.sleep(3)  # Wait before retrying
                
        # If still no response after all retries
        if not raw_response:
            # Provide a more helpful error message
            error_msg = f"Failed to process: \"{user_input}\". The system is experiencing high load or connectivity issues. Please try again in a few moments."
            current_app.logger.error(error_msg)
            return jsonify({
                'type': 'error',
                'content': error_msg
            }), 503  # Service Unavailable status code

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
        # Check if we have multiple queries (separated by semicolons)
        queries = [q.strip() for q in cleaned_sql.split(';') if q.strip()]
        is_multi_query = len(queries) > 1
        
        if is_multi_query:
            current_app.logger.info(f"Processing complex multi-part query with {len(queries)} sub-queries")
            
            # Validate each query individually
            for i, single_query in enumerate(queries):
                if not is_valid_sql(single_query, preferred_db):
                    current_app.logger.warning(f"Invalid SQL sub-query {i+1}: {single_query}")
                    return jsonify({
                        'type': 'error',
                        'content': f"Part {i+1} of your complex query was invalid. Please try rephrasing your question.",
                        'debug_info': {
                            'query': single_query,
                            'raw_response': raw_response
                        }
                    }), 400
        else:
            # Single query validation
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
        
        # Step 6: Generate natural language response based on query results
        # For complex multi-part queries, we need a more comprehensive response
        natural_response = generate_natural_response(user_input, db_response, cleaned_sql)
        
        # Step 7: Save the chat message and response to the database
        save_result = save_chat_message(
            user_id=user_id,
            conversation_id=conversation_id,
            message=user_input,
            response=natural_response,
            sql_query=cleaned_sql,
            database_used=database_hint
        )
        
        if not save_result:
            current_app.logger.warning(
                f"Failed to save chat message for conversation {conversation_id}. "
                f"The response will still be returned to the user."
            )
        
        # Step 8: Return comprehensive response with enhanced metadata
        # Check if we have multiple result sets from multiple queries
        is_multi_result = isinstance(db_response, list) and len(db_response) > 0 and all(isinstance(item, list) for item in db_response)
        
        # Calculate row count appropriately based on result type
        if is_multi_result:
            total_row_count = sum(len(result_set) if result_set else 0 for result_set in db_response)
            individual_counts = [len(result_set) if result_set else 0 for result_set in db_response]
            row_count_info = {
                'total': total_row_count,
                'individual': individual_counts
            }
        else:
            row_count_info = {
                'total': len(db_response) if db_response else 0,
                'individual': [len(db_response) if db_response else 0]
            }
        
        # Check for specific query types that need special frontend handling
        is_complex_borrower_query = any(term in user_input.lower() for term in [
            "borrowing history", "repayment history", "borrowing character", "credit history", "loan summary"
        ])
        
        # Determine if this is a query about missed payments (for special handling)
        is_missed_payment_query = any(term in user_input.lower() for term in [
            "missed payment", "late payment", "arrears", "overdue"
        ])
        
        # Detect account summary requests
        is_account_summary = any(pattern in user_input.lower() for pattern in [
            "account summary", "customer summary", "member summary", 
            "account details for", "summary for", "information about",
            "tell me about", "show me details for", "give me account",
            "account history", "transaction history", "payment history"
        ])
        
        return jsonify({
            'type': 'data_response',
            'content': natural_response,
            'sql': cleaned_sql,
            'data': db_response,
            'conversation_id': conversation_id,
            'database': database_hint,
            'row_count': row_count_info,
            'metadata': {
                'is_complex_query': is_multi_result,
                'is_borrower_query': is_complex_borrower_query,
                'is_missed_payment_query': is_missed_payment_query,
                'is_account_summary': is_account_summary,
                'query_count': len(queries) if 'queries' in locals() else 1
            }
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


