from datetime import datetime
from extensions import db

class RefinanceApplication(db.Model):
    __tablename__ = 'refinance_applications'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    member_name = db.Column(db.String(255), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    current_balance = db.Column(db.Float, nullable=False)
    requested_amount = db.Column(db.Float, nullable=False)
    new_term = db.Column(db.Integer, nullable=False)
    application_date = db.Column(db.DateTime, nullable=False)
    application_notes = db.Column(db.Text)
    supporting_documents = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Pending', nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<RefinanceApplication {self.id} - Status: {self.status}>'