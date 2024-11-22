from extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='Active')
    interest_rate = db.Column(db.String(10), nullable=False)
    rate_method = db.Column(db.String(20), nullable=True)
    processing_fee = db.Column(db.String(50), nullable=True)
    maintenance_fee = db.Column(db.String(50), nullable=True)
    insurance_fee = db.Column(db.String(20), nullable=True)
    frequency = db.Column(db.String(10), nullable=True)
    min_amount = db.Column(db.Numeric(20, 2), nullable=False, default=1.00)
    max_amount = db.Column(db.Numeric(20, 2), nullable=False)
    min_term = db.Column(db.Integer, nullable=False, default=1)
    max_term = db.Column(db.Integer, nullable=False)
    collateral = db.Column(db.Text, nullable=True)
    income_statement = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, nullable=True, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f'<Product {self.code}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'status': self.status,
            'interest_rate': self.interest_rate,
            'rate_method': self.rate_method,
            'processing_fee': self.processing_fee,
            'maintenance_fee': self.maintenance_fee,
            'insurance_fee': self.insurance_fee,
            'frequency': self.frequency,
            'min_amount': float(self.min_amount) if self.min_amount else None,
            'max_amount': float(self.max_amount) if self.max_amount else None,
            'min_term': self.min_term,
            'max_term': self.max_term,
            'collateral': self.collateral,
            'income_statement': self.income_statement
        }
