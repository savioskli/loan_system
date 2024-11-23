from models.system_settings import SystemSettings
from werkzeug.utils import secure_filename
import os
from extensions import db

class SettingsService:
    @staticmethod
    def get_all_settings():
        """Get all system settings as a dictionary."""
        try:
            settings = {
                'site_name': SystemSettings.get_setting('site_name', 'Loan System'),
                'site_description': SystemSettings.get_setting('site_description', ''),
                'theme_mode': SystemSettings.get_setting('theme_mode', 'light'),
                'primary_color': SystemSettings.get_setting('primary_color', '#3B82F6'),
                'secondary_color': SystemSettings.get_setting('secondary_color', '#1E40AF'),
                'site_logo': SystemSettings.get_setting('site_logo', None)
            }
            return settings
        except Exception as e:
            print(f"Error getting all settings: {str(e)}")
            return {
                'site_name': 'Loan System',
                'site_description': '',
                'theme_mode': 'light',
                'primary_color': '#3B82F6',
                'secondary_color': '#1E40AF',
                'site_logo': None
            }

    @staticmethod
    def update_settings(settings_data, user_id):
        """Update multiple settings at once."""
        try:
            updates = {}
            for key, value in settings_data.items():
                if value is not None:  # Only update if value is provided
                    SystemSettings.set_setting(key, value, user_id)
                    updates[key] = value
            db.session.commit()
            return updates
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def handle_logo_upload(logo_file, app, user_id):
        """Handle logo file upload and update settings."""
        if not logo_file:
            return None

        try:
            # Secure the filename
            filename = secure_filename(logo_file.filename)
            
            # Ensure the upload directory exists
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'logos')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate the file path and save the file
            file_path = os.path.join(upload_dir, filename)
            logo_file.save(file_path)
            
            # Store the relative path in the settings
            logo_url = os.path.join('uploads', 'logos', filename).replace('\\', '/')
            SystemSettings.set_setting('site_logo', logo_url, user_id)
            db.session.commit()
            
            return logo_url
        except Exception as e:
            db.session.rollback()
            print(f"Error handling logo upload: {str(e)}")
            return None

    @staticmethod
    def get_theme_settings():
        """Get theme-related settings."""
        try:
            return {
                'theme_mode': SystemSettings.get_setting('theme_mode', 'light'),
                'primary_color': SystemSettings.get_setting('primary_color', '#3B82F6'),
                'secondary_color': SystemSettings.get_setting('secondary_color', '#1E40AF')
            }
        except Exception as e:
            print(f"Error getting theme settings: {str(e)}")
            return {
                'theme_mode': 'light',
                'primary_color': '#3B82F6',
                'secondary_color': '#1E40AF'
            }

    @staticmethod
    def get_site_settings():
        """Get site-related settings."""
        try:
            return {
                'site_name': SystemSettings.get_setting('site_name', 'Loan System'),
                'site_description': SystemSettings.get_setting('site_description', ''),
                'site_logo': SystemSettings.get_setting('site_logo', None)
            }
        except Exception as e:
            print(f"Error getting site settings: {str(e)}")
            return {
                'site_name': 'Loan System',
                'site_description': '',
                'site_logo': None
            }
