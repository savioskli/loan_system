from extensions import db
from datetime import datetime

class CollectionSchedule(db.Model):
    __tablename__ = 'collection_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    schedule_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # scheduled, completed, missed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    staff = db.relationship('Staff', backref=db.backref('collection_schedules', lazy=True))
    loan = db.relationship('Loan', backref=db.backref('collection_schedules', lazy=True))

    def __repr__(self):
        return f'<CollectionSchedule {self.id}: {self.status}>'
