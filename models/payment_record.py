from datetime import datetime
from extensions import db

class PaymentRecord(db.Model):
    __tablename__ = 'payment_records'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('collection_schedules.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Relationships
    schedule = db.relationship('CollectionSchedule', backref=db.backref('payment_records', lazy=True))
    loan = db.relationship('Loan', backref=db.backref('payment_records', lazy=True))
    creator = db.relationship('Staff', foreign_keys=[created_by], backref=db.backref('created_payments', lazy=True))
    
    def __repr__(self):
        return f'<PaymentRecord {self.id}: {self.amount}>' 
    
    def to_dict(self):
        """Convert the payment record to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'loan_id': self.loan_id,
            'amount': float(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'description': self.description,
            'attachment_url': self.attachment_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
