import os
from datetime import timedelta

# Database configuration for direct MySQL connections
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'loan_system',
    'auth_plugin': 'mysql_native_password'
}

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://root:@localhost:3306/loan_system?auth_plugin=mysql_native_password'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Core Banking API
    CORE_BANKING_URL = 'http://localhost:5003'  # Base URL for core banking
    CORE_BANKING_API_KEY = 'dev-token'  # API key for authentication
    
    # Application
    SYSTEM_NAME = "Loan Management System"
    THEME_MODE = "light"  # or "dark"
    THEME_PRIMARY_COLOR = "#4f46e5"    # Indigo-600
    THEME_SECONDARY_COLOR = "#7c3aed"  # Violet-600
    
    # Encryption
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'u8BtMHHQNtisWw1uqKPHu6jCRzk_20csT0zhvXCBJrg='  # Default key if not set in env
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/loan_system.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 10
