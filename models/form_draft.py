from datetime import datetime
from app import db

class FormDraft(db.Model):
    __tablename__ = 'form_drafts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('form_sections.id'), nullable=False)
    form_data = db.Column(db.JSON, nullable=False, default={})
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='form_drafts')
    organization = db.relationship('Organization', backref='form_drafts')
    module = db.relationship('Module', backref='form_drafts')
    section = db.relationship('FormSection', backref='form_drafts')
    
    def __repr__(self):
        return f'<FormDraft {self.id} - User {self.user_id} - Module {self.module_id} - Section {self.section_id}>'
