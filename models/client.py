from extensions import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    client_no = db.Column(db.String(50), unique=True, nullable=False)
    client_type_id = db.Column(db.Integer, db.ForeignKey('client_types.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # Personal/Business Information
    first_name = db.Column(db.String(100))  # For individual clients
    middle_name = db.Column(db.String(100))  # For individual clients
    last_name = db.Column(db.String(100))  # For individual clients
    business_name = db.Column(db.String(200))  # For business clients
    registration_no = db.Column(db.String(100))  # For business clients
    
    # Contact Information
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    postal_address = db.Column(db.String(100))
    physical_address = db.Column(db.String(200))
    
    # Status and Dates
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, suspended
    onboarding_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Relationships
    client_type = db.relationship('ClientType', backref=db.backref('clients', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('clients', lazy=True))
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_clients')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_clients')
    
    @property
    def full_name(self):
        """Return the full name of the client."""
        if self.client_type.client_code == 'IND':  # Individual
            names = filter(None, [self.first_name, self.middle_name, self.last_name])
            return ' '.join(names)
        return self.business_name
    
    def __repr__(self):
        return f'<Client {self.client_no}: {self.full_name}>'
