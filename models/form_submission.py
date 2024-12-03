from extensions import db
from datetime import datetime

class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    client_type_id = db.Column(db.Integer, db.ForeignKey('client_types.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    form_data = db.Column(db.JSON, nullable=False)  # Store all form fields
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = db.relationship('Module', backref='submissions')
    client_type = db.relationship('ClientType', backref='submissions')
    staff = db.relationship('Staff', backref='form_submissions')
    
    def __repr__(self):
        return f'<FormSubmission {self.id} for Module {self.module.code}>'
