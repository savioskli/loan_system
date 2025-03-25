#!/usr/bin/env python
"""
Script to update the SMTP password in the email configuration.
This script will generate a new encryption key and encrypt the provided password.
"""

import os
import sys
import sqlite3
from cryptography.fernet import Fernet

# Generate a new encryption key
def generate_key():
    return Fernet.generate_key()

# Encrypt a value with the given key
def encrypt_value(value, key):
    if not value:
        return None
    
    try:
        f = Fernet(key)
        return f.encrypt(value.encode()).decode()
    except Exception as e:
        print(f"Error encrypting value: {str(e)}")
        return None

# Update the SMTP password in the database
def update_smtp_password(db_path, password, key):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Encrypt the password
        encrypted_password = encrypt_value(password, key)
        if not encrypted_password:
            print("Failed to encrypt password.")
            return False
        
        # Update the email_config table
        cursor.execute("UPDATE email_config SET smtp_password = ?", (encrypted_password,))
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT COUNT(*) FROM email_config WHERE smtp_password = ?", (encrypted_password,))
        count = cursor.fetchone()[0]
        
        conn.close()
        
        if count > 0:
            return True
        else:
            print("Password updated but verification failed.")
            return False
    except Exception as e:
        print(f"Database error: {str(e)}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python update_smtp_password.py <database_path> <smtp_password>")
        print("Example: python update_smtp_password.py instance/loan_system.db mypassword")
        return
    
    db_path = sys.argv[1]
    password = sys.argv[2]
    
    # Generate a new encryption key
    key = generate_key()
    print(f"\nGenerated new encryption key: {key.decode()}")
    
    # Update the password in the database
    success = update_smtp_password(db_path, password, key)
    
    if success:
        print("\nSMTP password updated successfully!")
        print("\nIMPORTANT: You must set this encryption key in your environment:")
        print(f"ENCRYPTION_KEY={key.decode()}")
        print("\nAdd this to your .env file or set it as an environment variable.")
    else:
        print("\nFailed to update SMTP password.")

if __name__ == "__main__":
    main()
