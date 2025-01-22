from extensions import db
from datetime import datetime

class CRBReport(db.Model):
    __tablename__ = 'crb_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    national_id = db.Column(db.String(20), nullable=False)
    report_data = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = db.Column(db.Text, nullable=True)
    credit_score = db.Column(db.Integer, nullable=True)
    report_reference = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<CRBReport {self.national_id}>'
