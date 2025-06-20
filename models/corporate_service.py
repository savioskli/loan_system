from datetime import datetime
from extensions import db
from models.client_registration import ClientRegistration
from models.system_reference_value import SystemReferenceValue

class CorporateService(db.Model):
    """Model for services subscribed by corporate clients."""
    __tablename__ = 'corporate_services'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_registration_data.id', ondelete='CASCADE'))
    service_type = db.Column(db.Integer, db.ForeignKey('system_reference_values.id'))
    details = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer)
    updated_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    
    # Relationships
    client = db.relationship(ClientRegistration, backref=db.backref('services', lazy='dynamic'))
    service_type_ref = db.relationship(SystemReferenceValue, foreign_keys=[service_type])
    
    def __repr__(self):
        return f'<CorporateService {self.service_type} - {self.start_date}>'
