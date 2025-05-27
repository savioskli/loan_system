from datetime import datetime
from extensions import db

class SystemReferenceField(db.Model):
    __tablename__ = 'system_reference_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    field_type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    form_fields = db.relationship('FormField', backref='system_reference_field', lazy=True)
    
    def __repr__(self):
        return f'<SystemReferenceField {self.name}>'
