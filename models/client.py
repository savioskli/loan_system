from extensions import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    client_type_id = db.Column(db.Integer, db.ForeignKey('client_types.id'), nullable=False)
    client_no = db.Column(db.String(50), unique=True)  # Keep this for backward compatibility
    form_data = db.Column(db.JSON, nullable=False)
    files = db.Column(db.JSON)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    
    # Relationships
    client_type = db.relationship('ClientType', backref=db.backref('clients', lazy=True))
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_clients')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_clients')
    
    @property
    def full_name(self):
        """Get the full name of the client."""
        if self.client_type.client_code == 'IND':  # Individual
            return (
                f"{self.form_data.get('first_name', '')} "
                f"{self.form_data.get('middle_name', '')} "
                f"{self.form_data.get('last_name', '')}"
            ).strip()
        return self.form_data.get('business_name', 'Unknown Client')
    
    def __repr__(self):
        return f'<Client {self.client_no}: {self.full_name}>'
