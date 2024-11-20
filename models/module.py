from extensions import db
from datetime import datetime

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for hierarchical structure
    parent = db.relationship('Module', remote_side=[id], backref=db.backref('children', lazy='dynamic'))
    # Relationship with form fields
    form_fields = db.relationship('FormField', backref='parent_module', lazy='dynamic', 
                                order_by='FormField.field_order')
    
    def __repr__(self):
        return f'<Module {self.name}>'

class FormField(db.Model):
    __tablename__ = 'form_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    field_label = db.Column(db.String(100), nullable=False)
    field_placeholder = db.Column(db.String(200))
    field_type = db.Column(db.String(50), nullable=False)
    validation_text = db.Column(db.String(200))
    is_required = db.Column(db.Boolean, default=False)
    field_order = db.Column(db.Integer, default=0)
    options = db.Column(db.JSON)
    validation_rules = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FormField {self.field_name}>'
