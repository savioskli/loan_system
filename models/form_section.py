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
    
    # Add new columns for client type and product dependencies
    client_type_restrictions = db.Column(db.JSON, nullable=True)  # List of client type IDs
    product_restrictions = db.Column(db.JSON, nullable=True)  # List of product IDs
    submodule_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    module = db.relationship('Module', foreign_keys=[module_id], backref=db.backref('sections', lazy='dynamic', order_by='FormSection.order'))
    submodule = db.relationship('Module', foreign_keys=[submodule_id], backref=db.backref('parent_sections', lazy='dynamic'))
    fields = db.relationship('FormField', 
                           backref='section',
                           lazy='dynamic',
                           order_by='FormField.field_order',
                           cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FormSection {self.name}>'
