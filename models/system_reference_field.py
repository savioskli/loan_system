from datetime import datetime
from extensions import db
from sqlalchemy import text

class SystemReferenceField(db.Model):
    __tablename__ = 'system_reference_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    reference_code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    field_type = db.Column(db.String(50), nullable=False)
    data_type = db.Column(db.String(50), nullable=False, default='string')
    default_value = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_required = db.Column(db.Boolean, default=False)
    validation_rules = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    form_fields = db.relationship('FormField', backref='system_reference', lazy=True)
    module = db.relationship('Module', backref='system_fields')
    creator = db.relationship('Staff', foreign_keys=[created_by])
    updater = db.relationship('Staff', foreign_keys=[updated_by])
    
    @classmethod
    def get_by_reference_code(cls, reference_code):
        """Get a system reference field by its reference code"""
        return cls.query.filter_by(reference_code=reference_code).first()
        
    @classmethod
    def get_field_value(cls, reference_code, context=None):
        """
        Get the value of a system reference field
        
        Args:
            reference_code (str): The reference code of the field
            context (dict): Additional context for value resolution
            
        Returns:
            The field value or None if not found
        """
        field = cls.get_by_reference_code(reference_code)
        if not field:
            return None
            
        # Default to the field's default value
        value = field.default_value
        
        # If there's a custom resolver for this field type, use it
        resolver_name = f'resolve_{field.field_type}_field'
        if hasattr(cls, resolver_name):
            resolver = getattr(cls, resolver_name)
            value = resolver(field, context) or value
            
        return value
        
    @classmethod
    def resolve_related_field(cls, field, context):
        """Resolve a related field value"""
        if not context or 'related_id' not in context:
            return None
            
        # This is a simplified example - you'd need to implement the actual resolution
        # based on your application's data model
        related_model = field.field_type.replace('_field', '').title()
        try:
            model = globals().get(related_model)
            if model:
                related_obj = model.query.get(context['related_id'])
                if related_obj:
                    return getattr(related_obj, field.reference_code.split('.')[-1], None)
        except Exception:
            pass
            
        return None
    
    def __repr__(self):
        return f'<SystemReferenceField {self.name}>'
