import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cryptography.fernet import Fernet
import json
from config import Config
from extensions import db
from models.core_banking import CoreBankingSystem
from app import create_app

# Create app context
app = create_app()

# Old and new encryption keys
old_key = Fernet('ys1ez5tkBQHElxQvNNBk41aHyJlHuZtkxzc2tZn43SQ='.encode())
new_key = Fernet(Config.ENCRYPTION_KEY)

def update_encrypted_credentials():
    with app.app_context():
        systems = CoreBankingSystem.query.filter(CoreBankingSystem.auth_credentials.isnot(None)).all()
        for system in systems:
            try:
                # Decrypt with old key
                decrypted = old_key.decrypt(system.auth_credentials.encode()).decode()
                # Encrypt with new key
                encrypted = new_key.encrypt(decrypted.encode()).decode()
                # Update the system
                system.auth_credentials = encrypted
                db.session.add(system)
                print(f"Successfully updated {system.name}")
            except Exception as e:
                print(f"Error updating {system.name}: {str(e)}")
        
        db.session.commit()

if __name__ == '__main__':
    update_encrypted_credentials()
