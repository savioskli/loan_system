"""
Core banking models for managing external banking system integrations
"""
from extensions import db
from datetime import datetime
import json

class CoreBankingSystem(db.Model):
    """Model for storing core banking system configurations"""
    __tablename__ = 'core_banking_systems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text)
    auth_type = db.Column(db.String(20))  # basic, bearer, api_key
    auth_credentials = db.Column(db.Text)  # Encrypted JSON string
    headers = db.Column(db.Text)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    endpoints = db.relationship('CoreBankingEndpoint', backref='system', lazy=True)
    logs = db.relationship('CoreBankingLog', backref='system', lazy=True)

    def __init__(self, **kwargs):
        super(CoreBankingSystem, self).__init__(**kwargs)
        if isinstance(self.headers, dict):
            self.headers = json.dumps(self.headers)
        if isinstance(self.auth_credentials, dict):
            self.auth_credentials = json.dumps(self.auth_credentials)

    @property
    def headers_dict(self):
        """Get headers as dictionary"""
        if not self.headers:
            return {}
        return json.loads(self.headers)

    @property
    def auth_credentials_dict(self):
        """Get auth credentials as dictionary"""
        if not self.auth_credentials:
            return {}
        return json.loads(self.auth_credentials)

class CoreBankingEndpoint(db.Model):
    """Model for storing core banking API endpoints"""
    __tablename__ = 'core_banking_endpoints'

    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('core_banking_systems.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)  # GET, POST, PUT, DELETE
    description = db.Column(db.Text)
    request_schema = db.Column(db.Text)  # JSON schema
    response_schema = db.Column(db.Text)  # JSON schema
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(CoreBankingEndpoint, self).__init__(**kwargs)
        if isinstance(self.request_schema, dict):
            self.request_schema = json.dumps(self.request_schema)
        if isinstance(self.response_schema, dict):
            self.response_schema = json.dumps(self.response_schema)

    @property
    def request_schema_dict(self):
        """Get request schema as dictionary"""
        if not self.request_schema:
            return {}
        return json.loads(self.request_schema)

    @property
    def response_schema_dict(self):
        """Get response schema as dictionary"""
        if not self.response_schema:
            return {}
        return json.loads(self.response_schema)

class CoreBankingLog(db.Model):
    """Model for logging core banking API requests and responses"""
    __tablename__ = 'core_banking_logs'

    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('core_banking_systems.id'), nullable=False)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('core_banking_endpoints.id'), nullable=True)
    request_method = db.Column(db.String(10), nullable=False)
    request_url = db.Column(db.String(255), nullable=False)
    request_headers = db.Column(db.Text)  # JSON string
    request_body = db.Column(db.Text)  # JSON string
    response_status = db.Column(db.Integer)
    response_body = db.Column(db.Text)  # JSON string
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    endpoint = db.relationship('CoreBankingEndpoint')
