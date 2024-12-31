"""
Service for handling encryption and decryption of sensitive data
"""
from cryptography.fernet import Fernet
import json
import os
from base64 import b64encode, b64decode

class EncryptionService:
    def __init__(self):
        """Initialize encryption service with a key"""
        # Generate a default key if not provided
        self.key = os.getenv('ENCRYPTION_KEY', 'ZrOOSJpEiMhqO8r33FOcI2zWdNSIffwDQW8hkNqtumE=').encode()
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data):
        """Encrypt data"""
        if not data:
            return None
        
        # Convert data to JSON string if it's a dict
        if isinstance(data, dict):
            data = json.dumps(data)
        
        # Convert to bytes if it's a string
        if isinstance(data, str):
            data = data.encode()
            
        # Encrypt the data
        encrypted_data = self.cipher_suite.encrypt(data)
        
        # Return base64 encoded string
        return b64encode(encrypted_data).decode('utf-8')

    def decrypt(self, encrypted_data):
        """Decrypt data"""
        if not encrypted_data:
            return None
            
        try:
            # Decode base64 string
            encrypted_bytes = b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt the data
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError:
                return decrypted_data.decode('utf-8')
                
        except Exception as e:
            raise Exception(f"Failed to decrypt data: {str(e)}")

# Create a singleton instance
_encryption_service = EncryptionService()

def encrypt_credentials(credentials):
    """Encrypt credentials"""
    return _encryption_service.encrypt(credentials)

def decrypt_credentials(encrypted_credentials):
    """Decrypt credentials"""
    return _encryption_service.decrypt(encrypted_credentials)
