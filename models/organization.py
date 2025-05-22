from extensions import db
from datetime import datetime

class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - define them here without backrefs
    modules = db.relationship('Module', back_populates='organization', lazy=True)
    staff_members = db.relationship('Staff', back_populates='organization', lazy=True)
    form_fields = db.relationship('FormField', back_populates='organization', lazy=True)

    def __repr__(self):
        return f'<Organization {self.name}>'
