from extensions import db
from datetime import datetime

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for hierarchical structure
    parent = db.relationship('Module', 
                           remote_side=[id], 
                           backref=db.backref('children', 
                                            lazy='dynamic',
                                            cascade='all, delete-orphan',
                                            passive_deletes=True))
    
    # Relationship with form fields
    form_fields = db.relationship('FormField', 
                                backref='parent_module', 
                                lazy='dynamic',
                                cascade='all, delete-orphan',
                                passive_deletes=True,
                                order_by='FormField.field_order')
    
    def __repr__(self):
        return f'<Module {self.name}>'

class FormField(db.Model):
    __tablename__ = 'form_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('form_sections.id', ondelete='CASCADE'))
    field_name = db.Column(db.String(100), nullable=False)
    field_label = db.Column(db.String(100), nullable=False)
    field_placeholder = db.Column(db.String(200))
    field_type = db.Column(db.String(50), nullable=False)
    validation_text = db.Column(db.String(200))
    is_required = db.Column(db.Boolean, default=False)
    field_order = db.Column(db.Integer, default=0)
    options = db.Column(db.JSON)
    validation_rules = db.Column(db.JSON)
    client_type_restrictions = db.Column(db.JSON, comment='List of client type IDs that can see this field')
    depends_on = db.Column(db.String(50))  # Name of the field this field depends on
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FormField {self.field_name}>'
