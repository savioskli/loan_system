from enum import Enum
from extensions import db
from datetime import datetime

class TemplateType(str, Enum):
    LOAN_APPROVED = "loan_approved"
    LOAN_REJECTED = "loan_rejected"
    PAYMENT_REMINDER = "payment_reminder"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_OVERDUE = "payment_overdue"
    LOAN_DISBURSED = "loan_disbursed"

class SMSTemplate(db.Model):
    __tablename__ = 'sms_templates'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    days_trigger = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SMSTemplate {self.type}>'