from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def init_extensions(app):
    """Initialize Flask extensions"""
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Specify the login view endpoint with correct blueprint prefix
    login_manager.login_message = 'Please log in to access this page.'  # Custom message
    login_manager.login_message_category = 'info'  # Message category for flash
    
    # Initialize CSRF Protection
    csrf.init_app(app)
    
    return app