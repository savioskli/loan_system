from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, migrate, login_manager, init_extensions
from datetime import datetime, timedelta
import logging
import os
from werkzeug.utils import secure_filename
from functools import wraps
from models.staff import Staff
from models.system_settings import SystemSettings
from models.activity_log import ActivityLog
from models.branch import Branch
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms_components import DateField as ComponentsDateField
import pytz
from routes.branch_routes import branch_bp
from routes import client_types_bp
from routes.main import main_bp
from routes.auth import auth_bp
from routes.user_management import bp as user_management_bp
from routes.role_routes import bp as role_bp
from routes.admin import admin_bp
from urllib.parse import urlparse
from utils.logging_utils import log_activity
from routes.modules import modules_bp
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

# Initialize CSRF protection
csrf = CSRFProtect()

# Initialize application
def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL query logging
    app.config['DEBUG'] = True  # Enable debug mode

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize extensions
    init_extensions(app)
    csrf.init_app(app)

    # Register context processors
    from context_processors import inject_settings, inject_navigation
    app.context_processor(inject_settings)
    app.context_processor(inject_navigation)

    # Clear SQLAlchemy model registry to ensure fresh model definitions
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if inspector.has_table("system_settings"):
            db.Model.metadata.clear()
            from models.settings import SystemSettings
            from models.staff import Staff
            from models.role import Role
            db.create_all()

    # Register template filters
    @app.template_filter('format_datetime')
    def format_datetime_filter(value):
        if value is None:
            return ""
        return value.strftime('%Y-%m-%d %H:%M:%S')

    # Register blueprints
    app.register_blueprint(auth_bp)  # Register auth_bp first for landing page
    app.register_blueprint(main_bp)  # Remove url_prefix for simpler URLs
    app.register_blueprint(user_management_bp)  # URL prefix is already in blueprint
    app.register_blueprint(role_bp)  # Register the roles blueprint
    app.register_blueprint(branch_bp, url_prefix='/branches')
    app.register_blueprint(client_types_bp)
    app.register_blueprint(modules_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Register admin blueprint

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

    def get_current_time():
        """Get current time in UTC"""
        return datetime.utcnow()

    def format_datetime(dt):
        """Convert UTC datetime to local timezone and format it"""
        if dt is None:
            return ''
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        local_dt = dt.astimezone(TIMEZONE)
        return local_dt.strftime('%Y-%m-%d %H:%M:%S')

    # Make format_datetime available to templates
    @app.context_processor
    def utility_processor():
        return dict(format_datetime=format_datetime)

    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.context_processor
    def inject_system_settings():
        """Inject system settings into all templates"""
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
        """Inject theme settings into all templates"""
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

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5002)
