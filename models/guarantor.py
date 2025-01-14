from datetime import datetime
from extensions import db
from models.client import Client

class Guarantor(db.Model):
    __tablename__ = 'guarantors'

    id = db.Column(db.Integer, primary_key=True)
    guarantor_no = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    id_no = db.Column(db.String(20), unique=True, nullable=False)
    phone_no = db.Column(db.String(30))
    email = db.Column(db.String(80))
    relationship = db.Column(db.String(50))
    occupation = db.Column(db.String(50))
    monthly_income = db.Column(db.Float)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    client = db.relationship('Client', backref=db.backref('guarantors', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'guarantor_no': self.guarantor_no,
            'client_id': self.client_id,
            'name': self.name,
            'id_no': self.id_no,
            'phone_no': self.phone_no,
            'email': self.email,
            'relationship': self.relationship,
            'occupation': self.occupation,
            'monthly_income': self.monthly_income,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
