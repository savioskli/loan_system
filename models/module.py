from extensions import db
from datetime import datetime
from models.organization import Organization

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'))
    is_active = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    table_name = db.Column(db.String(100))
    
    # Self-referential relationship for hierarchical structure
    parent = db.relationship('Module', 
                           remote_side=[id], 
                           backref=db.backref('children', 
                                            lazy='dynamic',
                                            cascade='all, delete-orphan',
                                            passive_deletes=True))
    
    # Relationship with organization
    organization = db.relationship('Organization', back_populates='modules')
    
    # Relationship with form fields
    form_fields = db.relationship('FormField', 
                                back_populates='parent_module',
                                lazy='dynamic',
                                cascade='all, delete-orphan',
                                passive_deletes=True,
                                order_by='FormField.field_order')
    
    def __repr__(self):
        return f'<Module {self.name}>'
