from extensions import db
from datetime import datetime

class SystemReferenceValue(db.Model):
    """Model for system reference values like client types, product types etc."""
    __tablename__ = 'system_reference_values'

    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, nullable=False, index=True)
    value = db.Column(db.String(255), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    parent_value_id = db.Column(db.Integer, db.ForeignKey('system_reference_values.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SystemReferenceValue {self.field_id}:{self.value}>'

    def to_dict(self):
        return {
            'id': self.id,
            'field_id': self.field_id,
            'value': self.value,
            'label': self.label,
            'is_active': self.is_active,
            'parent_value_id': self.parent_value_id
        }
