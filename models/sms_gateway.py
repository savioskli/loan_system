from extensions import db
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class SmsGatewayConfig(db.Model):
    """Model for storing SMS gateway configuration."""
    __tablename__ = 'sms_gateway_config'

    id = db.Column(db.Integer, primary_key=True)
    sms_provider = db.Column(db.String(50), nullable=False)
    sms_api_key = db.Column(db.String(255), nullable=False)
    sms_sender_id = db.Column(db.String(50), nullable=False)
    africas_talking_username = db.Column(db.String(255), nullable=True)
    twilio_account_sid = db.Column(db.String(255), nullable=True)
    twilio_auth_token = db.Column(db.String(255), nullable=True)
    infobip_base_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'sms_provider': self.sms_provider,
            'sms_api_key': self.sms_api_key,
            'sms_sender_id': self.sms_sender_id,
            'africas_talking_username': self.africas_talking_username,
            'twilio_account_sid': self.twilio_account_sid,
            'twilio_auth_token': self.twilio_auth_token,
            'infobip_base_url': self.infobip_base_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def get_active_config():
        """Get the active configuration."""
        return SmsGatewayConfig.query.first()

    @classmethod
    def get_all(cls):
        """Get all configurations."""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, config_id):
        """Get configuration by ID."""
        return cls.query.get(config_id)

    @classmethod
    def update(cls, config_id, **kwargs):
        """Update configuration."""
        config = cls.query.get(config_id)
        for key, value in kwargs.items():
            setattr(config, key, value)
        db.session.commit()
        return config

    @classmethod
    def delete(cls, config_id):
        """Delete configuration."""
        config = cls.query.get(config_id)
        db.session.delete(config)
        db.session.commit()