from datetime import datetime
from extensions import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, action, details=None, ip_address=None):
        self.user_id = user_id
        self.action = action
        self.details = details
        self.ip_address = ip_address

    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.user_id} at {self.timestamp}>'
