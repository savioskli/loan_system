from datetime import datetime
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event
from extensions import db
from flask import current_app

class FormField(db.Model):
    __tablename__ = 'form_fields'
    __table_args__ = {'extend_existing': True}
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    field_label = db.Column(db.String(100), nullable=False)
    field_placeholder = db.Column(db.String(200), nullable=True)
    column_name = db.Column(db.String(100), nullable=True, comment='Database column name this field maps to')
    field_type = db.Column(db.String(50), nullable=False)
    validation_text = db.Column(db.String(200), nullable=True)
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    field_order = db.Column(db.Integer, default=0, nullable=False)
    options = db.Column(JSON, nullable=True)
    validation_rules = db.Column(JSON, nullable=True)
    client_type_restrictions = db.Column(JSON, nullable=True)
    depends_on = db.Column(db.String(50), nullable=True)
    section_id = db.Column(db.Integer, db.ForeignKey('form_sections.id', ondelete='SET NULL'), nullable=True)
    reference_field_code = db.Column(db.String(50), nullable=True)
    is_cascading = db.Column(db.Boolean, default=False, nullable=False)
    parent_field_id = db.Column(db.Integer, db.ForeignKey('form_fields.id', ondelete='SET NULL'), nullable=True)
    is_system = db.Column(db.Boolean, default=False, nullable=False)
    system_reference_field_id = db.Column(db.Integer, db.ForeignKey('form_fields.id', ondelete='SET NULL'), nullable=True)
    is_visible = db.Column(db.Boolean, default=True, nullable=False, server_default='1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    # The backref for parent_module is defined in the Module model
    parent_module = db.relationship('Module', back_populates='form_fields')
    parent_section = db.relationship('FormSection', backref=db.backref('form_fields', lazy=True))
    organization = db.relationship('Organization', back_populates='form_fields')
    parent_field = db.relationship('FormField', 
                                remote_side=[id], 
                                foreign_keys=[parent_field_id],
                                backref=db.backref('child_fields', 
                                                lazy=True,
                                                foreign_keys='FormField.parent_field_id'))
    
    def __init__(self, **kwargs):
        # Set default values for required fields
        self.is_system = kwargs.pop('is_system', False)
        self.is_visible = kwargs.pop('is_visible', True)
        
        # Let SQLAlchemy handle the rest
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return f'<FormField {self.field_name}>'
