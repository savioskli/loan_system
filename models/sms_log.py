from extensions import db
from datetime import datetime

class SMSLog(db.Model):
    __tablename__ = 'sms_logs'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('sms_templates.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    recipient = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'sent' or 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    template = db.relationship('SMSTemplate', backref='logs')
    loan = db.relationship('Loan', backref='sms_logs')

    def __repr__(self):
        return f'<SMSLog {self.id} - {self.status}>'