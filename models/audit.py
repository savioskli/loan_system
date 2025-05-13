from datetime import datetime
from extensions import db
from flask_login import current_user
from models.staff import Staff

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    action_type = db.Column(db.String(50), nullable=False)  # e.g., 'create', 'update', 'delete', 'view'
    entity_type = db.Column(db.String(50), nullable=False)  # e.g., 'loan', 'client', 'repayment'
    entity_id = db.Column(db.Integer, nullable=True)  # ID of the affected entity
    description = db.Column(db.Text, nullable=False)  # Description of the action
    old_value = db.Column(db.JSON, nullable=True)  # Previous state (for updates)
    new_value = db.Column(db.JSON, nullable=True)  # New state (for updates and creates)
    ip_address = db.Column(db.String(50), nullable=True)  # IP address of the user
    user_agent = db.Column(db.String(255), nullable=True)  # User agent of the browser
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Relationship to Staff model
    user = db.relationship('Staff', backref=db.backref('audit_logs', lazy=True))

    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action_type} on {self.entity_type} {self.entity_id}'
    
    @classmethod
    def log_action(cls, action_type, entity_type, entity_id=None, description=None, 
                  old_value=None, new_value=None, ip_address=None, user_agent=None):
        """Helper method to create an audit log entry"""
        user_id = current_user.id if current_user and current_user.is_authenticated else None
        
        log_entry = cls(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
