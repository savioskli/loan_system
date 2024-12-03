from extensions import db
from datetime import datetime

class Prospect(db.Model):
    __tablename__ = 'prospects'
    
    id = db.Column(db.Integer, primary_key=True)
    client_type_id = db.Column(db.Integer, db.ForeignKey('client_types.id'), nullable=False)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    id_number = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    county = db.Column(db.String(100))
    sub_county = db.Column(db.String(100))
    postal_address = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    town = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    form_data = db.Column(db.JSON)  # Store any additional form fields
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client_type = db.relationship('ClientType', backref='prospects')
    staff = db.relationship('Staff', backref='prospects')
    
    def __repr__(self):
        return f'<Prospect {self.first_name} {self.last_name}>'
