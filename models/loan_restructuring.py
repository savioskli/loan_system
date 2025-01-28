from datetime import datetime
from . import db

class LoanRescheduling(db.Model):
    """Model for loan rescheduling requests"""
    __tablename__ = 'loan_rescheduling'

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    current_balance = db.Column(db.Numeric(15, 2), nullable=False)
    new_tenure = db.Column(db.Integer, nullable=False)
    new_installment = db.Column(db.Numeric(15, 2), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected'), default='Pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loan = db.relationship('Loan', backref='rescheduling_requests')
    client = db.relationship('Client', backref='rescheduling_requests')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_reschedulings')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_reschedulings')

class LoanRefinancing(db.Model):
    """Model for loan refinancing requests"""
    __tablename__ = 'loan_refinancing'

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    current_balance = db.Column(db.Numeric(15, 2), nullable=False)
    additional_amount = db.Column(db.Numeric(15, 2), nullable=False)
    new_total = db.Column(db.Numeric(15, 2), nullable=False)
    new_tenure = db.Column(db.Integer, nullable=False)
    new_installment = db.Column(db.Numeric(15, 2), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected'), default='Pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loan = db.relationship('Loan', backref='refinancing_requests')
    client = db.relationship('Client', backref='refinancing_requests')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_refinancings')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_refinancings')

class SettlementPlan(db.Model):
    """Model for settlement plan requests"""
    __tablename__ = 'settlement_plans'

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    current_balance = db.Column(db.Numeric(15, 2), nullable=False)
    settlement_amount = db.Column(db.Numeric(15, 2), nullable=False)
    waiver_amount = db.Column(db.Numeric(15, 2), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    deadline_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected', 'Completed'), default='Pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loan = db.relationship('Loan', backref='settlement_plans')
    client = db.relationship('Client', backref='settlement_plans')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_settlements')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_settlements')
