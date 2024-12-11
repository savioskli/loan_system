from datetime import datetime
from sqlalchemy.dialects.mysql import JSON
from app import db

class FormField(db.Model):
    __tablename__ = 'form_fields'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    field_label = db.Column(db.String(50), nullable=False)
    field_placeholder = db.Column(db.String(100))
    field_type = db.Column(db.String(20), nullable=False)
    validation_text = db.Column(db.String(200))
    is_required = db.Column(db.Boolean, default=False)
    field_order = db.Column(db.Integer, nullable=False)
    options = db.Column(JSON)
    client_type_restrictions = db.Column(JSON)
    depends_on = db.Column(db.String(50))  # Name of the field this field depends on
    section_id = db.Column(db.Integer, db.ForeignKey('form_sections.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent_module = db.relationship('Module', backref=db.backref('form_fields', lazy=True))
    parent_section = db.relationship('FormSection', backref=db.backref('form_fields', lazy=True))

    def __init__(self, module_id, field_name, field_label, field_type, field_order=0,
                 field_placeholder=None, is_required=True, options=None, depends_on=None,
                 validation_text=None, client_type_restrictions=None):
        self.module_id = module_id
        self.field_name = field_name
        self.field_label = field_label
        self.field_type = field_type
        self.field_order = field_order
        self.field_placeholder = field_placeholder
        self.is_required = is_required
        self.options = options
        self.depends_on = depends_on
        self.validation_text = validation_text
        self.client_type_restrictions = client_type_restrictions

    def __repr__(self):
        return f'<FormField {self.field_name}>'
