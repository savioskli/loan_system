from extensions import db
from datetime import datetime

class FormSection(db.Model):
    __tablename__ = 'form_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = db.relationship('Module', backref=db.backref('sections', lazy='dynamic', order_by='FormSection.order'))
    fields = db.relationship('FormField', 
                           backref='section',
                           lazy='dynamic',
                           order_by='FormField.field_order',
                           cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FormSection {self.name}>'
