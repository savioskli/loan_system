from database.db_manager import db
from datetime import datetime

class LoanGrading(db.Model):
    """Model for loan grading information"""
    __tablename__ = 'loan_grading'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    loan_account_no = db.Column(db.String(20), nullable=False)
    loan_amount = db.Column(db.Numeric(15, 2), nullable=False)
    outstanding_balance = db.Column(db.Numeric(15, 2), nullable=False)
    days_in_arrears = db.Column(db.Integer, nullable=False)
    principal_in_arrears = db.Column(db.Numeric(15, 2), nullable=False)
    interest_in_arrears = db.Column(db.Numeric(15, 2), nullable=False)
    total_in_arrears = db.Column(db.Numeric(15, 2), nullable=False)
    classification = db.Column(db.String(1), nullable=False)  # N=Normal, W=Watch, S=Substandard, D=Doubtful, L=Loss
    classification_date = db.Column(db.Date, nullable=False)
    provision_rate = db.Column(db.Numeric(5, 2), nullable=False)
    provision_amount = db.Column(db.Numeric(15, 2), nullable=False)
    last_payment_date = db.Column(db.Date)
    next_payment_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = db.relationship('Client', backref=db.backref('loan_gradings', lazy=True))

class LoanGradingAnalysis(db.Model):
    """Model for loan grading analysis"""
    __tablename__ = 'loan_grading_analysis'

    risk_grade = db.Column(db.Text)
    loan_count = db.Column(db.BigInteger, nullable=False, default=0)
    total_exposure = db.Column(db.Numeric(32, 2))
    avg_days_in_arrears = db.Column(db.Numeric(14, 6))
    min_days_in_arrears = db.Column(db.Numeric(10, 2))
    max_days_in_arrears = db.Column(db.Numeric(10, 2))

    def __repr__(self):
        return f'<LoanGradingAnalysis {self.risk_grade}>'
