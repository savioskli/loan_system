import sys
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, migrate, login_manager, init_extensions
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms_components import DateField as ComponentsDateField
import pytz
from urllib.parse import urlparse
from utils.logging_utils import log_activity
from flask_wtf.csrf import CSRFProtect
from flask import g
from services.scheduler import init_scheduler
from utils.audit_middleware import init_audit_middleware

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import models
from models.staff import Staff
from models.system_settings import SystemSettings
from models.activity_log import ActivityLog
from models.branch import Branch
from models.role import Role
from models.module import Module, FormField
from models.sms_template import SMSTemplate, TemplateType
from models.email_template import EmailTemplate, EmailTemplateType
from models.sms_log import SMSLog
from models.post_disbursement_modules import PostDisbursementModule
from models.audit import AuditLog
from models.impact import ImpactCategory

# Import routes
from routes.branch_routes import branch_bp
from routes.client_types import client_types_bp
from routes.main import main_bp
from routes.auth import auth_bp
from routes.user_management import bp as user_management_bp
from routes.role_routes import bp as role_bp
from routes.admin import admin_bp
from routes.modules import modules_bp
from routes.user import user_bp
from routes.products import products_bp
from routes.section_routes import sections_bp
from routes.impact import impact_bp
from routes.post_disbursement_modules import post_disbursement_modules_bp
from routes.post_disbursement_workflows import post_disbursement_workflows_bp
from routes.progress_update import progress_update_bp
from routes.settings import settings_bp
from routes.field_dependencies import dependencies_bp
from routes.integrations import integrations_bp
from routes.correspondence import correspondence_bp
from routes.thresholds import thresholds_bp
from routes.collection_schedule import collection_schedule_bp
from routes.core_banking import bp as core_banking_bp
from routes.api import api_bp
from routes.audit import audit_bp

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/loan_system.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Initialize CSRF protection
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['DEBUG'] = True

    # Load configuration
    app.config.from_object('config.Config')

    # Configure Flask logger
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'DEBUG'))
    app.logger.setLevel(log_level)
    
    # Clear existing handlers
    app.logger.handlers = []
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)
    
    # Add file handler
    log_file = app.config.get('LOG_FILE', 'logs/loan_system.log')
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=app.config.get('LOG_MAX_BYTES', 10485760),
        backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)
    
    # Log that logging has been configured
    app.logger.info('Logging configured - writing to console and %s', log_file)

    # APScheduler settings
    app.config['SCHEDULER_API_ENABLED'] = True
    app.config['SCHEDULER_TIMEZONE'] = 'Africa/Nairobi'

    # Initialize extensions
    init_extensions(app)
    csrf.init_app(app)

    # Initialize scheduler
    init_scheduler(app)

    # Initialize audit middleware
    init_audit_middleware(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(modules_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(products_bp)
    app.register_blueprint(sections_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(dependencies_bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(correspondence_bp)
    app.register_blueprint(branch_bp)
    app.register_blueprint(client_types_bp)
    app.register_blueprint(collection_schedule_bp)
    app.register_blueprint(core_banking_bp)
    app.register_blueprint(post_disbursement_modules_bp)
    app.register_blueprint(post_disbursement_workflows_bp)
    app.register_blueprint(progress_update_bp)
    app.register_blueprint(api_bp)  # Register the API blueprint
    app.register_blueprint(audit_bp)  # Register the Audit blueprint
    app.register_blueprint(impact_bp)  # Register the Impact blueprint

    # Import and register SMS templates blueprint after all models are loaded
    from routes.sms_templates import sms_templates_bp
    app.register_blueprint(sms_templates_bp)

    # Import and register email templates blueprint
    from routes.email_templates import email_templates_bp
    app.register_blueprint(email_templates_bp)

    # Import and register thresholds blueprint
    from routes.thresholds import thresholds_bp
    app.register_blueprint(thresholds_bp)

    # Register context processors
    from context_processors import inject_settings, inject_navigation
    app.context_processor(inject_settings)
    app.context_processor(inject_navigation)

    # Initialize database models
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if inspector.has_table("system_settings"):
            db.Model.metadata.clear()
            # Re-import all models to ensure they're properly registered
            from models.system_settings import SystemSettings
            from models.staff import Staff
            from models.role import Role
            from models.module import Module, FormField
            from models.sms_template import SMSTemplate, TemplateType
            from models.email_template import EmailTemplate, EmailTemplateType
            from models.sms_log import SMSLog
            from models.post_disbursement_modules import PostDisbursementModule
            from models.audit import AuditLog
            db.create_all()
            
        # Initialize chat tables
        from routes.user import ensure_chat_tables_exist
        ensure_chat_tables_exist()

    # Register template filters
    @app.template_filter('datetime')
    def format_datetime(value):
        if value is None:
            return ""
        return value.strftime('%Y-%m-%d %H:%M:%S')

    @app.template_filter('format_datetime')
    def format_datetime_filter(value):
        if value is None:
            return ""
        return value.strftime('%Y-%m-%d %H:%M:%S')

    @app.template_filter('currency')
    def currency_filter(value):
        """
        Format a numeric value as currency.

        :param value: Numeric value to format
        :return: Formatted currency string
        """
        try:
            # Convert to float to handle both int and float
            value = float(value)
            # Format with 2 decimal places and comma as thousands separator
            return f"{value:,.2f}"
        except (ValueError, TypeError):
            # Return original value if conversion fails
            return value

    # Exempt CSRF for API routes
    csrf.exempt(modules_bp)
    csrf.exempt(dependencies_bp)
    csrf.exempt(integrations_bp)
    csrf.exempt(sms_templates_bp)
    csrf.exempt(email_templates_bp)
    csrf.exempt(thresholds_bp)
    csrf.exempt(user_bp)
    csrf.exempt(api_bp)

    # Flask-Login configuration
    @login_manager.user_loader
    def load_user(user_id):
        return Staff.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('auth.login', next=request.url))

    # Timezone configuration
    TIMEZONE = pytz.timezone('Africa/Nairobi')

    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Context processors
    @app.context_processor
    def inject_system_settings():
        try:
            return dict(
                system_name=SystemSettings.get_setting('system_name', 'Loan System'),
                system_description=SystemSettings.get_setting('system_description', ''),
                system_logo=SystemSettings.get_setting('system_logo')
            )
        except Exception as e:
            logger.error(f"Error injecting system settings: {e}")
            return dict(
                system_name="Loan System",
                system_description="",
                system_logo=None
            )

    @app.context_processor
    def inject_theme_settings():
        try:
            return dict(
                theme_primary_color=SystemSettings.get_setting('theme_primary_color', '#3B82F6'),
                theme_secondary_color=SystemSettings.get_setting('theme_secondary_color', '#1E40AF'),
                theme_mode=SystemSettings.get_setting('theme_mode', 'light')
            )
        except Exception as e:
            logger.error(f"Error injecting theme settings: {e}")
            return dict(
                theme_primary_color='#3B82F6',
                theme_secondary_color='#1E40AF',
                theme_mode='light'
            )

    # Debug route to list all registered routes
    @app.route('/debug/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': ','.join(rule.methods),
                'route': str(rule)
            })
        return jsonify(routes)

    # Error handlers
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 error: {str(error)}")
        app.logger.error(traceback.format_exc())
        db.session.rollback()

        wants_json = (
            request.headers.get('Content-Type', '').startswith('application/json') or
            request.headers.get('Accept', '').startswith('application/json') or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.path.startswith('/api/')
        )

        if wants_json:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(405)
    def method_not_allowed(error):
        app.logger.error(f"405 error: {str(error)}")

        wants_json = (
            request.headers.get('Content-Type', '').startswith('application/json') or
            request.headers.get('Accept', '').startswith('application/json') or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.path.startswith('/api/')
        )

        if wants_json:
            return jsonify({'error': 'Method not allowed'}), 405
        return render_template('errors/405.html'), 405

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5002)
