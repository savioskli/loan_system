from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from extensions import db

class EmailConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)  # smtp, sendgrid, mailgun, etc
    api_key = db.Column(db.String(255), nullable=True)  # Set to nullable
    smtp_server = db.Column(db.String(100), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_username = db.Column(db.String(100))
    smtp_password = db.Column(db.String(255))
    from_email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, config_id):
        return cls.query.get(config_id)

    @classmethod
    def create(cls, **kwargs):
        config = cls(**kwargs)
        db.session.add(config)
        db.session.commit()
        return config

    @classmethod
    def update(cls, config_id, **kwargs):
        config = cls.query.get(config_id)
        for key, value in kwargs.items():
            setattr(config, key, value)
        db.session.commit()
        return config

    @classmethod
    def delete(cls, config_id):
        config = cls.query.get(config_id)
        db.session.delete(config)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'provider': self.provider,
            'api_key': self.api_key,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'smtp_password': decrypt_value(self.smtp_password) if self.smtp_password else None,
            'from_email': self.from_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }