from extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class CoreBankingConfig(db.Model):
    """Model for storing core banking integration configuration"""
    __tablename__ = 'core_banking_config'

    id = db.Column(db.Integer, primary_key=True)
    system_type = db.Column(db.String(50), nullable=False)  # 'navision' or 'brnet'
    server_url = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    database = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))  # Will be encrypted before storage
    api_key = db.Column(db.String(255))   # Will be encrypted before storage
    sync_interval = db.Column(db.Integer, default=15)  # in minutes
    sync_settings = db.Column(JSONB, default={})  # Store sync preferences
    selected_tables = db.Column(JSONB, default=[])  # Store selected tables
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'system_type': self.system_type,
            'server_url': self.server_url,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'sync_interval': self.sync_interval,
            'sync_settings': self.sync_settings,
            'selected_tables': self.selected_tables,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def get_active_config():
        """Get the active configuration"""
        return CoreBankingConfig.query.filter_by(is_active=True).first()
