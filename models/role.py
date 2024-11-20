from datetime import datetime
from extensions import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Relationships
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_roles')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_roles')
    
    def __init__(self, name, description=None, is_active=True, created_by=None):
        self.name = name
        self.description = description
        self.is_active = is_active
        self.created_by = created_by
        self.updated_by = created_by
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
