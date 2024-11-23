from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models.client_type import ClientType
from forms.client_type import ClientTypeForm
from extensions import db, csrf
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from datetime import datetime, date
import traceback
from sqlalchemy import text

client_types_bp = Blueprint('client_types', __name__, url_prefix='/admin/client-types')

@client_types_bp.route('/')
@login_required
def manage_client_types():
    try:
        client_types = ClientType.query.order_by(ClientType.created_at.desc()).all()
        return render_template('admin/client_types/index.html', client_types=client_types)
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in manage_client_types: {str(e)}")
        flash('An error occurred while loading client types. Please try again.', 'error')
        return redirect(url_for('main.index'))
    except Exception as e:
        current_app.logger.error(f"Unexpected error in manage_client_types: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('main.index'))

@client_types_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_client_type():
    try:
        form = ClientTypeForm()
        if form.validate_on_submit():
            try:
                # Log form data
                current_app.logger.info(f"Form data received: {form.data}")
                
                # Create client type with user tracking
                client_type = ClientType(
                    client_code=form.client_code.data,
                    client_name=form.client_name.data,
                    effective_from=form.effective_from.data,
                    effective_to=form.effective_to.data,
                    status=form.status.data,
                    created_by=current_user.id,
                    updated_by=current_user.id
                )
                
                # Log object data
                current_app.logger.info(f"Client type object created: {client_type.__dict__}")
                
                db.session.add(client_type)
                db.session.flush()  # Flush to catch any database errors before commit
                
                # Log database representation
                current_app.logger.info("Database flush successful")
                
                db.session.commit()
                flash('Client type created successfully!', 'success')
                return redirect(url_for('client_types.manage_client_types'))
                
            except IntegrityError as e:
                db.session.rollback()
                error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
                current_app.logger.error(f"Database integrity error: {error_msg}")
                if 'Duplicate entry' in error_msg:
                    flash('A client type with this code already exists.', 'error')
                else:
                    flash(f'Database integrity error: {error_msg}', 'error')
                    
            except SQLAlchemyError as e:
                db.session.rollback()
                error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
                current_app.logger.error(f"Database error details: {error_msg}")
                flash(f'Database error: {error_msg}', 'error')
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
                flash(f'Error details: {str(e)}', 'error')
        
        if form.errors:
            current_app.logger.error(f"Form validation errors: {form.errors}")
            
        return render_template('admin/client_types/form.html', form=form, title='New Client Type')
        
    except Exception as e:
        current_app.logger.error(f"Route error: {str(e)}\n{traceback.format_exc()}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('client_types.manage_client_types'))

@client_types_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client_type(id):
    try:
        client_type = ClientType.query.get_or_404(id)
        
        if request.method == 'GET':
            # Initialize form with client type data
            form = ClientTypeForm()
            form.client_code.data = client_type.client_code
            form.client_name.data = client_type.client_name
            form.status.data = client_type.status
            
            # Handle dates carefully
            if client_type.effective_from:
                try:
                    form.effective_from.data = client_type.effective_from
                except Exception as e:
                    current_app.logger.error(f"Error setting effective_from: {str(e)}")
                    form.effective_from.data = datetime.now().date()
            
            if client_type.effective_to:
                try:
                    form.effective_to.data = client_type.effective_to
                except Exception as e:
                    current_app.logger.error(f"Error setting effective_to: {str(e)}")
                    form.effective_to.data = None
        else:
            form = ClientTypeForm()
        
        if form.validate_on_submit():
            try:
                client_type.client_code = form.client_code.data
                client_type.client_name = form.client_name.data
                client_type.effective_from = form.effective_from.data
                client_type.effective_to = form.effective_to.data
                client_type.status = form.status.data
                
                db.session.commit()
                flash('Client type updated successfully!', 'success')
                return redirect(url_for('client_types.manage_client_types'))
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(f"Database error in edit_client_type: {str(e)}")
                flash('Error updating client type. Please try again.', 'error')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Unexpected error in edit_client_type update: {str(e)}\n{traceback.format_exc()}")
                flash('An unexpected error occurred while updating. Please try again.', 'error')
        
        return render_template('admin/client_types/form.html', form=form, title='Edit Client Type')
    except Exception as e:
        current_app.logger.error(f"Error in edit_client_type route: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while loading the client type. Please try again.', 'error')
        return redirect(url_for('client_types.manage_client_types'))

@client_types_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_client_type(id):
    client_type = ClientType.query.get_or_404(id)
    try:
        db.session.delete(client_type)
        db.session.commit()
        flash('Client type deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('Error deleting client type. Please try again.', 'error')
        return jsonify({'success': False}), 500
