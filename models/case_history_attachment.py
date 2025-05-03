from datetime import datetime
from app import db

class CaseHistoryAttachment(db.Model):
    __tablename__ = 'case_history_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    case_history_id = db.Column(db.Integer, db.ForeignKey('case_history.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    
    case_history_id = db.Column(db.Integer, db.ForeignKey('case_history.id'), nullable=False)
    case_history = db.relationship('CaseHistory', back_populates='history_attachments')
    
    def __repr__(self):
        return f'<CaseHistoryAttachment {self.id}: {self.file_name}>'
