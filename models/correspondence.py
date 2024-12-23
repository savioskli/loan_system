from extensions import db
from datetime import datetime

class Correspondence(db.Model):
    __tablename__ = 'correspondence'
    
    id = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.String(50), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # sms, email, call, letter, visit
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # sent, delivered, failed, pending
    sent_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # If it's an SMS or email
    recipient = db.Column(db.String(100))
    delivery_status = db.Column(db.String(50))
    delivery_time = db.Column(db.DateTime)
    
    # If it's a call
    call_duration = db.Column(db.Integer)  # in seconds
    call_outcome = db.Column(db.String(50))
    
    # If it's a site visit
    location = db.Column(db.String(200))
    visit_purpose = db.Column(db.String(200))
    visit_outcome = db.Column(db.String(200))
    
    # Relationships
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    attachment_path = db.Column(db.String(500))
    
    staff = db.relationship('Staff', backref=db.backref('correspondence', lazy=True))
    loan = db.relationship('Loan', backref=db.backref('correspondence', lazy=True))
    
    def __repr__(self):
        return f'<Correspondence {self.id} - {self.type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'account_no': self.account_no,
            'client_name': self.client_name,
            'type': self.type,
            'message': self.message,
            'status': self.status,
            'sent_by': self.sent_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'recipient': self.recipient,
            'delivery_status': self.delivery_status,
            'delivery_time': self.delivery_time.isoformat() if self.delivery_time else None,
            'call_duration': self.call_duration,
            'call_outcome': self.call_outcome,
            'location': self.location,
            'visit_purpose': self.visit_purpose,
            'visit_outcome': self.visit_outcome,
            'staff_id': self.staff_id,
            'loan_id': self.loan_id,
            'attachment_path': self.attachment_path
        }
