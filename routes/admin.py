from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
import traceback
from forms.general_settings import GeneralSettingsForm
from services.settings_service import SettingsService
from extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/system-settings', methods=['GET', 'POST'])
@login_required
def system_settings():
    form = GeneralSettingsForm()
    current_logo = None
    settings = None
    
    try:
        # Get current settings
        settings = SettingsService.get_all_settings()
        if settings:
            current_logo = settings.get('site_logo')
        
        if form.validate_on_submit():
            # Update settings using service
            settings_data = {
                'site_name': form.site_name.data,
                'site_description': form.site_description.data,
                'theme_mode': form.theme_mode.data,
                'primary_color': form.primary_color.data,
                'secondary_color': form.secondary_color.data
            }
            
            # Update general settings
            SettingsService.update_settings(settings_data, current_user.id)
            
            # Handle logo upload if provided
            if form.site_logo.data:
                SettingsService.handle_logo_upload(form.site_logo.data, current_app, current_user.id)

            flash('Settings updated successfully!', 'success')
            return redirect(url_for('admin.system_settings'))

        # Pre-fill form with existing settings
        if request.method == 'GET' and settings:
            form.site_name.data = settings.get('site_name', '')
            form.site_description.data = settings.get('site_description', '')
            form.theme_mode.data = settings.get('theme_mode', 'light')
            form.primary_color.data = settings.get('primary_color', '#3B82F6')
            form.secondary_color.data = settings.get('secondary_color', '#1E40AF')
        
        return render_template('admin/general_settings/form.html', 
                             form=form,
                             current_logo=current_logo)
                             
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        traceback.print_exc()  # Print the full traceback for debugging
        return redirect(url_for('admin.dashboard'))
