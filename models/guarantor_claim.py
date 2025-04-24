from datetime import datetime
from . import db
from datetime import datetime

class GuarantorClaim(db.Model):
    """
    Model representing guarantor claims for loans.
    """
    __tablename__ = 'guarantor_claims'

    id = db.Column(db.Integer, primary_key=True)
    
    # Identifiers
    loan_id = db.Column(db.Integer, nullable=True)
    loan_no = db.Column(db.String(20), nullable=True)
    borrower_id = db.Column(db.Integer, nullable=True)
    borrower_name = db.Column(db.String(255), nullable=False)
    guarantor_id = db.Column(db.Integer, nullable=True)
    guarantor_name = db.Column(db.String(255), nullable=False)
    
    # Claim Details
    claim_amount = db.Column(db.Numeric(15, 2), nullable=False)
    claim_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    document_path = db.Column(db.String(255), nullable=True)
    
    # Audit Fields
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert the model instance to a dictionary for easy serialization."""
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'loan_no': self.loan_no,
            'borrower_id': self.borrower_id,
            'borrower_name': self.borrower_name,
            'guarantor_id': self.guarantor_id,
            'guarantor_name': self.guarantor_name,
            'claim_amount': float(self.claim_amount) if self.claim_amount else None,
            'claim_date': self.claim_date.isoformat() if self.claim_date else None,
            'status': self.status,
            'notes': self.notes,
            'document_path': self.document_path,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<GuarantorClaim {self.id}: {self.guarantor_name} - {self.status}>'
