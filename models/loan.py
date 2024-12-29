from extensions import db
from datetime import datetime
from models.collection_schedule import CollectionSchedule

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    term = db.Column(db.Integer, nullable=False)  # in months
    disbursement_date = db.Column(db.DateTime)
    maturity_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)  # pending, active, closed, defaulted
    outstanding_balance = db.Column(db.Numeric(15, 2))
    total_in_arrears = db.Column(db.Numeric(15, 2), default=0)
    days_in_arrears = db.Column(db.Integer, default=0)
    classification = db.Column(db.String(20))  # NORMAL, WATCH, SUBSTANDARD, DOUBTFUL, LOSS
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Relationships
    client = db.relationship('Client', backref=db.backref('loans', lazy=True))
    product = db.relationship('Product', backref=db.backref('loans', lazy=True))
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_loans')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_loans')
    
    def __repr__(self):
        return f'<Loan {self.account_no}: {self.status}>'
