from extensions import db
from datetime import datetime

class SMSTemplate(db.Model):
    __tablename__ = 'sms_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    template = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    variables = db.Column(db.JSON)  # List of variables that can be used in the template
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Relationships
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_templates')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_templates')
    
    def __repr__(self):
        return f'<SMSTemplate {self.code}: {self.name}>'
