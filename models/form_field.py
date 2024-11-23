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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent_module = db.relationship('Module', backref=db.backref('form_fields', lazy=True))

    def __repr__(self):
        return f'<FormField {self.field_name}>'
