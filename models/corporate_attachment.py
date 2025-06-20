from datetime import datetime
from extensions import db
from models.client_registration import ClientRegistration

class CorporateAttachment(db.Model):
    """Model for corporate attachments (documents)."""
    __tablename__ = 'corporate_attachments'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_registration_data.id', ondelete='CASCADE'))
    document_type = db.Column(db.String(100), nullable=False)  # e.g., "Certificate of Incorporation"
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # System fields
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    
    # Relationship with client registration
    client = db.relationship(ClientRegistration, backref=db.backref('attachments', lazy='dynamic'))
    
    def __repr__(self):
        return f'<CorporateAttachment {self.document_type} - {self.file_name}>'
