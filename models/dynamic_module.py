from extensions import db
from datetime import datetime

class Module(db.Model):
    __tablename__ = 'dynamic_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    module_type = db.Column(db.String(50), nullable=False)  # 'client' or 'loan'
    parent_id = db.Column(db.Integer, db.ForeignKey('dynamic_modules.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('Module', remote_side=[id], backref='children')
    fields = db.relationship('ModuleField', backref='module', cascade='all, delete-orphan')

class ModuleField(db.Model):
    __tablename__ = 'module_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('dynamic_modules.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)  # text, number, date, select, etc.
    required = db.Column(db.Boolean, default=False)
    options = db.Column(db.JSON)  # For select/radio fields
    validation_rules = db.Column(db.JSON)  # JSON field for validation rules
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
