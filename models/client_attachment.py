from extensions import db
from datetime import datetime

class ClientAttachment(db.Model):
    __tablename__ = 'client_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_type_id = db.Column(db.Integer, db.ForeignKey('client_types.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    attachment_type = db.Column(db.String(50), nullable=False)  # e.g., 'pdf', 'image', 'doc'
    size_limit = db.Column(db.Integer)  # Size limit in bytes
    is_mandatory = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))

    # Relationships
    client_type = db.relationship('ClientType', backref='attachments')
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_attachments')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_attachments')

    def __repr__(self):
        return f'<ClientAttachment {self.name} for {self.client_type.name}>'
