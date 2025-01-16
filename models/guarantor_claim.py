from datetime import datetime
from . import db

class GuarantorClaim(db.Model):
    """
    Model representing guarantor claims for loans.
    """
    __tablename__ = 'guarantor_claims'

    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    guarantor_name = db.Column(db.String(255), nullable=False)
    borrower_name = db.Column(db.String(255), nullable=False)
    guarantor_contact = db.Column(db.String(50), nullable=True)
    borrower_contact = db.Column(db.String(50), nullable=True)
    
    # Claim Details
    amount_paid = db.Column(db.Numeric(15, 2), nullable=False)
    claim_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending', 
                       nullable=False)  # Pending, Resolved
    
    # Optional Additional Information
    claim_description = db.Column(db.Text, nullable=True)
    
    # Optional Identifiers (without foreign key constraints)
    guarantor_id = db.Column(db.Integer, nullable=True)
    loan_id = db.Column(db.Integer, nullable=True)
    
    def to_dict(self):
        """
        Convert the model instance to a dictionary for easy serialization.
        """
        return {
            'id': self.id,
            'guarantor_name': self.guarantor_name,
            'borrower_name': self.borrower_name,
            'guarantor_contact': self.guarantor_contact,
            'borrower_contact': self.borrower_contact,
            'amount_paid': float(self.amount_paid),
            'claim_date': self.claim_date.isoformat() if self.claim_date else None,
            'status': self.status,
            'claim_description': self.claim_description,
            'guarantor_id': self.guarantor_id,
            'loan_id': self.loan_id
        }
    
    def __repr__(self):
        return f'<GuarantorClaim {self.id}: {self.guarantor_name} - {self.status}>'
