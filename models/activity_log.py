from extensions import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('staff.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Staff model
    staff = db.relationship('Staff', backref=db.backref('activities', lazy='dynamic'))

    def __init__(self, user_id, action, details=None, ip_address=None):
        self.user_id = user_id
        self.action = action
        self.details = details
        self.ip_address = ip_address

    def __repr__(self):
        return f'<ActivityLog {self.id} {self.action}>'
