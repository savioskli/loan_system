from datetime import datetime
from extensions import db

class ClientRegistration(db.Model):
    """Model for client registration data."""
    __tablename__ = 'client_registration_data'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.JSON)
    identification_type = db.Column(db.String(100))
    identification_number = db.Column(db.String(255))
    serial_number = db.Column(db.String(255))
    birth_date = db.Column(db.Date)
    mobile_number = db.Column(db.String(255))
    email_address = db.Column(db.String(255))
    postal_address = db.Column(db.String(255))
    postal_code = db.Column(db.String(255))
    postal_town = db.Column(db.String(100))
    county = db.Column(db.String(100))
    status = db.Column(db.String(255))
    draft_status = db.Column(db.String(50), default='draft')
    client_type = db.Column(db.String(255))
    corporate_name = db.Column(db.String(255))
    corporate_registration_date = db.Column(db.Date)
    number_of_directors_or_members = db.Column(db.Integer)
    purpose = db.Column(db.String(255))
    product = db.Column(db.String(255))
    corporate_registration_number = db.Column(db.String(255))
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer)
    updated_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    branch_id = db.Column(db.Integer)
