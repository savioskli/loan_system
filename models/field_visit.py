from extensions import db
from datetime import datetime

class FieldVisit(db.Model):
    __tablename__ = 'field_visits'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # External Database References
    customer_id = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    loan_account_no = db.Column(db.String(50), nullable=False)
    
    # Loan Details (at time of scheduling)
    outstanding_balance = db.Column(db.Numeric(15, 2), nullable=False)
    days_in_arrears = db.Column(db.Integer, nullable=False)
    missed_payments = db.Column(db.Integer, nullable=False)  # Calculated from days_in_arrears
    installment_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Staff Assignments - using integers without foreign key constraints
    field_officer_id = db.Column(db.Integer, nullable=False)
    supervisor_id = db.Column(db.Integer, nullable=True)
    assigned_branch_id = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)
    
    # Visit Details
    visit_date = db.Column(db.Date, nullable=False)
    visit_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)  # Low, Medium, High, Critical
    
    # Additional Information
    alternative_contact = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=False)
    special_instructions = db.Column(db.Text, nullable=True)
    attachment = db.Column(db.String(255), nullable=True)
    
    # Status Tracking
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled, in-progress, completed, cancelled
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FieldVisit {self.id}: {self.visit_date} - {self.status}>'
    
    def to_dict(self):
        """Convert the field visit to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'loan_account_no': self.loan_account_no,
            'field_officer_id': self.field_officer_id,
            'supervisor_id': self.supervisor_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'visit_time': self.visit_time.isoformat() if self.visit_time else None,
            'location': self.location,
            'purpose': self.purpose,
            'priority': self.priority,
            'outstanding_balance': float(self.outstanding_balance) if self.outstanding_balance else 0,
            'days_in_arrears': self.days_in_arrears,
            'missed_payments': self.missed_payments,
            'installment_amount': float(self.installment_amount) if self.installment_amount else 0,
            'alternative_contact': self.alternative_contact,
            'notes': self.notes,
            'special_instructions': self.special_instructions,
            'attachment': self.attachment,
            'status': self.status,
            'assigned_branch_id': self.assigned_branch_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
