import json
from datetime import datetime
from extensions import db

class CoreBankingSystem(db.Model):
    __tablename__ = 'core_banking_systems'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, default=3306)
    database_name = db.Column(db.String(100), nullable=False)
    auth_credentials = db.Column(db.Text, nullable=False)  # JSON string with username and password
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def auth_credentials_dict(self):
        """Return auth credentials as a dictionary"""
        if not self.auth_credentials:
            return {}
        return json.loads(self.auth_credentials)
    
    def __repr__(self):
        return f'<CoreBankingSystem {self.name}>'
