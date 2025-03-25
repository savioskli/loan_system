from cryptography.fernet import Fernet
import base64
import os
from config import Config

def get_encryption_key():
    """Get or create encryption key"""
    # Try to get the key from environment variables first
    key = os.getenv('ENCRYPTION_KEY')
    if key:
        try:
            # Ensure the key is valid by attempting to create a Fernet instance
            key_bytes = key.encode() if isinstance(key, str) else key
            Fernet(key_bytes)  # This will raise an error if the key is invalid
            print(f"[INFO] Using encryption key from environment variable")
            return key_bytes
        except Exception as e:
            print(f"[ERROR] Invalid encryption key from environment: {str(e)}")
            # Try the default key as a fallback
            default_key = b'ys1ez5tkBQHElxQvNNBk41aHyJlHuZtkxzc2tZn43SQ='  # This is the key we generated earlier
            try:
                Fernet(default_key)
                print(f"[INFO] Using default encryption key as fallback")
                return default_key
            except Exception as e:
                print(f"[ERROR] Default key also invalid: {str(e)}")
    
    # If not in env, try to get from Config
    try:
        key = getattr(Config, 'ENCRYPTION_KEY', None)
        if key:
            # Ensure the key is in bytes format
            key_bytes = key if isinstance(key, bytes) else key.encode()
            # Validate the key
            Fernet(key_bytes)  # This will raise an error if the key is invalid
            print(f"[INFO] Using encryption key from Config")
            return key_bytes
    except Exception as e:
        print(f"[ERROR] Invalid encryption key from Config: {str(e)}")
        # Try the default key as a fallback
        default_key = b'ys1ez5tkBQHElxQvNNBk41aHyJlHuZtkxzc2tZn43SQ='
        try:
            Fernet(default_key)
            print(f"[INFO] Using default encryption key as fallback")
            return default_key
        except Exception as e:
            print(f"[ERROR] Default key also invalid: {str(e)}")
    
    # If we reach here, we need to generate a new key
    try:
        print(f"[WARNING] No valid encryption key found, generating a new one")
        key = Fernet.generate_key()
        # In production, this key should be stored securely (e.g., environment variable)
        Config.ENCRYPTION_KEY = key
        return key
    except Exception as e:
        print(f"[ERROR] Failed to generate encryption key: {str(e)}")
        # As a last resort, use the default key
        default_key = b'ys1ez5tkBQHElxQvNNBk41aHyJlHuZtkxzc2tZn43SQ='
        try:
            Fernet(default_key)
            print(f"[WARNING] Using default encryption key as last resort")
            return default_key
        except Exception as e:
            print(f"[ERROR] All key attempts failed: {str(e)}")
            return None

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
        print(f"[WARNING] Cannot decrypt empty value")
        return None
    
    try:
        key = get_encryption_key()
        if not key:
            print(f"[ERROR] Encryption key is not available")
            return None
            
        print(f"[DEBUG] Attempting to decrypt value with key length: {len(key)}")
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_value.encode()).decode()
        print(f"[INFO] Successfully decrypted value")
        return decrypted
    except Exception as e:
        print(f"[ERROR] Failed to decrypt value: {str(e)}")
        return None
