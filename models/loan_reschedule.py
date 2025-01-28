from datetime import datetime
from extensions import db


class LoanReschedule(db.Model):
    __tablename__ = 'loan_rescheduling_requests'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    original_term = db.Column(db.Integer, nullable=False)
    proposed_term = db.Column(db.Integer, nullable=False)
    request_date = db.Column(db.DateTime, nullable=False)
    proposed_start_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.Text)
    supporting_documents = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Pending', nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<LoanReschedule {self.id} - Status: {self.status}>'