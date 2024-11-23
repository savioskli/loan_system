from datetime import datetime, date
from extensions import db
from sqlalchemy.orm import validates
from flask_login import current_user

class ClientType(db.Model):
    __tablename__ = 'client_types'
    
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(20), unique=True, nullable=True)
    client_name = db.Column(db.String(100), nullable=True)
    effective_from = db.Column(db.Date, nullable=True)
    effective_to = db.Column(db.Date, nullable=True)
    status = db.Column(db.Boolean, default=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)

    @validates('effective_from', 'effective_to')
    def validate_dates(self, key, value):
        if value is None and key == 'effective_to':
            return value
        
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(f"Invalid date format for {key}. Expected format: YYYY-MM-DD")
        elif isinstance(value, datetime):
            value = value.date()
        elif not isinstance(value, date):
            raise ValueError(f"Invalid date type for {key}")
        
        return value

    def __repr__(self):
        return f'<ClientType {self.client_code}>'
