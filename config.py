import os
from datetime import timedelta

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
    
    # Application
    SYSTEM_NAME = "Loan Management System"
    THEME_MODE = "light"  # or "dark"
    THEME_PRIMARY_COLOR = "#4f46e5"    # Indigo-600
    THEME_SECONDARY_COLOR = "#7c3aed"  # Violet-600
