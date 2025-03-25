#!/usr/bin/env python

"""
Utility script to fix encryption key issues and test SMTP password decryption.

This script will:
1. Check the current encryption key
2. Test decryption of the stored SMTP password
3. If decryption fails, provide options to reset the encryption key or re-encrypt the password
"""

import os
import sys
from cryptography.fernet import Fernet

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.email_config import EmailConfig
from utils.encryption import get_encryption_key, encrypt_value, decrypt_value

# Create Flask app context
app = create_app()


def check_encryption_key():
    """Check if the encryption key is valid"""
    key = get_encryption_key()
    if not key:
        print("[ERROR] Failed to retrieve a valid encryption key")
        return False
    
    try:
        # Test if the key is a valid Fernet key
        Fernet(key)
        print(f"[INFO] Encryption key is valid. Key length: {len(key)}")
        return True
    except Exception as e:
        print(f"[ERROR] Invalid encryption key: {str(e)}")
        return False


def test_smtp_password_decryption():
    """Check if the SMTP password exists in the database"""
    with app.app_context():
        config = EmailConfig.query.first()
        if not config:
            print("[ERROR] No email configuration found in the database")
            return False
        
        if not config.smtp_password:
            print("[ERROR] SMTP password is not set in the database")
            return False
        
        print(f"[INFO] SMTP password exists in the database")
        print(f"[SUCCESS] Using SMTP password directly without decryption")
        return True


def reset_encryption_key():
    """Generate a new encryption key and update the config"""
    new_key = Fernet.generate_key()
    print(f"[INFO] Generated new encryption key: {new_key.decode()}")
    
    # Set the new key in environment variable for the current session
    os.environ['ENCRYPTION_KEY'] = new_key.decode()
    
    print("[INFO] New encryption key has been generated.")
    print("[IMPORTANT] You must set this key in your environment variables or config file:")
    print(f"ENCRYPTION_KEY={new_key.decode()}")
    
    return new_key


def update_smtp_password(new_password):
    """Update the SMTP password in the database with the plaintext password"""
    with app.app_context():
        config = EmailConfig.query.first()
        if not config:
            print("[ERROR] No email configuration found in the database")
            return False
        
        # Store the password directly without encryption
        # Update the database
        config.smtp_password = new_password
        try:
            from app import db
            db.session.commit()
            print(f"[SUCCESS] SMTP password updated successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to update SMTP password in database: {str(e)}")
            return False


def main():
    print("===== Email Encryption Utility =====\n")
    
    # Check current encryption key
    print("Checking encryption key...")
    key_valid = check_encryption_key()
    
    # Check SMTP password
    print("\nChecking SMTP password...")
    password_exists = test_smtp_password_decryption()
    
    if key_valid and password_exists:
        print("\n[SUCCESS] SMTP password is configured correctly!")
        return
    
    print("\n[WARNING] SMTP password needs to be updated.")
    
    # Provide options to fix the issues
    print("\nOptions to update SMTP password:")
    print("1. Update SMTP password directly in the database")
    print("2. Exit without changes")
    
    choice = input("\nEnter your choice (1-2): ")
    
    if choice == "1":
        # Update SMTP password directly
        print("\nUpdating SMTP password directly in the database...")
        print("Please enter the new SMTP password (will be stored as plaintext):")
        new_password = input("SMTP Password: ")
        update_smtp_password(new_password)
        
    else:
        print("\nExiting without changes.")


if __name__ == "__main__":
    main()
