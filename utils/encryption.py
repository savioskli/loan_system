from cryptography.fernet import Fernet
import base64
import os
from config import Config

def get_encryption_key():
    """Get or create encryption key"""
    key = getattr(Config, 'ENCRYPTION_KEY', None)
    if not key:
        # Generate a new key if none exists
        key = Fernet.generate_key()
        # In production, this key should be stored securely (e.g., environment variable)
        Config.ENCRYPTION_KEY = key
    return key

def encrypt_value(value):
    """Encrypt a string value"""
    if not value:
        return None
    
    try:
        f = Fernet(get_encryption_key())
        return f.encrypt(value.encode()).decode()
    except Exception as e:
        # Log error in production
        return None

def decrypt_value(encrypted_value):
    """Decrypt an encrypted string value"""
    if not encrypted_value:
        return None
    
    try:
        f = Fernet(get_encryption_key())
        return f.decrypt(encrypted_value.encode()).decode()
    except Exception as e:
        # Log error in production
        return None
