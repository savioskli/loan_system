from datetime import datetime
from extensions import db
from models.client_registration import ClientRegistration

class CorporateSignatory(db.Model):
    """Model for corporate signatories (authorized to sign on behalf of the company)."""
    __tablename__ = 'corporate_signatories'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_registration_data.id', ondelete='CASCADE'))
    name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255), nullable=False)
    id_number = db.Column(db.String(50), nullable=False)
    signature_level = db.Column(db.String(50))  # e.g., "A", "B", "C"
    is_active = db.Column(db.Boolean, default=True)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer)
    updated_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    
    # Relationship with client registration
    client = db.relationship(ClientRegistration, backref=db.backref('signatories', lazy='dynamic'))
    
    def __repr__(self):
        return f'<CorporateSignatory {self.name} - Level {self.signature_level}>'
