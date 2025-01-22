from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required
from utils.decorators import admin_required
from models.credit_bureau import CreditBureau
from forms.credit_bureau_forms import CreditBureauForm
from extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/credit-bureau')
@login_required
@admin_required
def credit_bureau():
    """Render the credit bureau configuration page"""
    form = CreditBureauForm()
    configurations = CreditBureau.query.all()
    return render_template('admin/credit_bureau.html', form=form, configurations=configurations)

@admin_bp.route('/credit-bureau/add', methods=['POST'])
@login_required
@admin_required
def add_configuration():
    """Add a new credit bureau configuration"""
    form = CreditBureauForm()
    
    if form.validate_on_submit():
        try:
            config = CreditBureau(
                name=form.name.data,
                provider=form.provider.data,
                base_url=form.base_url.data,
                api_key=form.api_key.data,
                username=form.username.data,
                password=form.password.data,
                is_active=form.is_active.data
            )
            db.session.add(config)
            db.session.commit()
            
            flash('Configuration added successfully!', 'success')
            return redirect(url_for('admin.credit_bureau'))
            
        except Exception as e:
            current_app.logger.error(f"Error adding configuration: {str(e)}")
            db.session.rollback()
            flash('Failed to add configuration. Please try again.', 'error')
    
    return render_template('admin/credit_bureau.html', form=form)

@admin_bp.route('/credit-bureau/<int:config_id>')
@login_required
@admin_required
def get_configuration(config_id):
    """Get a specific credit bureau configuration"""
    config = CreditBureau.query.get_or_404(config_id)
    return jsonify({
        'id': config.id,
        'name': config.name,
        'provider': config.provider,
        'base_url': config.base_url,
        'api_key': config.api_key,
        'username': config.username,
        'is_active': config.is_active
    })

@admin_bp.route('/credit-bureau/<int:config_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_configuration(config_id):
    """Edit a credit bureau configuration"""
    config = CreditBureau.query.get_or_404(config_id)
    form = CreditBureauForm()
    
    if form.validate_on_submit():
        try:
            config.name = form.name.data
            config.provider = form.provider.data
            config.base_url = form.base_url.data
            config.api_key = form.api_key.data
            config.username = form.username.data
            if form.password.data:  # Only update password if provided
                config.password = form.password.data
            config.is_active = form.is_active.data
            
            db.session.commit()
            flash('Configuration updated successfully!', 'success')
            return redirect(url_for('admin.credit_bureau'))
            
        except Exception as e:
            current_app.logger.error(f"Error updating configuration: {str(e)}")
            db.session.rollback()
            flash('Failed to update configuration. Please try again.', 'error')
    
    return render_template('admin/credit_bureau.html', form=form)

@admin_bp.route('/credit-bureau/<int:config_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_configuration(config_id):
    """Toggle a configuration's active status"""
    try:
        config = CreditBureau.query.get_or_404(config_id)
        config.is_active = not config.is_active
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Configuration {"activated" if config.is_active else "deactivated"} successfully'
        })
    except Exception as e:
        current_app.logger.error(f"Error toggling configuration: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update configuration status'
        }), 500

@admin_bp.route('/credit-bureau/active')
@login_required
@admin_required
def get_active_configuration():
    """Get the currently active credit bureau configuration"""
    config = CreditBureau.query.filter_by(is_active=True).first()
    if not config:
        return jsonify({'error': 'No active configuration found'}), 404
        
    return jsonify({
        'id': config.id,
        'name': config.name,
        'provider': config.provider,
        'base_url': config.base_url,
        'api_key': config.api_key,
        'username': config.username
    })
