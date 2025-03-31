from extensions import db
from datetime import datetime

class ProgressUpdate(db.Model):
    __tablename__ = 'progress_updates'

    id = db.Column(db.Integer, primary_key=True)
    collection_schedule_id = db.Column(db.Integer, db.ForeignKey('collection_schedules.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=True)
    collection_method = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.String(1000), nullable=True)
    attachment_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    collection_schedule = db.relationship('CollectionSchedule', backref=db.backref('progress_updates', lazy=True))

    def __repr__(self):
        return f"<ProgressUpdate {self.id}: {self.status} - {self.amount}>"
