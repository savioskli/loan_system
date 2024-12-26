from extensions import db
from datetime import datetime
from sqlalchemy import event

class Threshold(db.Model):
    __tablename__ = 'thresholds'

    id = db.Column(db.Integer, primary_key=True)
    npl_ratio = db.Column(db.Float, nullable=False, comment='Non-Performing Loan Ratio (%)')
    coverage_ratio = db.Column(db.Float, nullable=False, comment='Coverage Ratio (%)')
    par_ratio = db.Column(db.Float, nullable=False, comment='Portfolio at Risk Ratio (%)')
    cost_of_risk = db.Column(db.Float, nullable=False, comment='Cost of Risk (%)')
    recovery_rate = db.Column(db.Float, nullable=False, comment='Recovery Rate (%)')
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f'<Threshold valid_from={self.valid_from} to={self.valid_to}>'

    @classmethod
    def get_current_threshold(cls):
        """Get the currently active threshold based on the current date."""
        current_time = datetime.utcnow()
        return cls.query.filter(
            cls.is_active == True,
            cls.valid_from <= current_time,
            (cls.valid_to.is_(None) | (cls.valid_to >= current_time))
        ).order_by(cls.valid_from.desc()).first()

    def to_dict(self):
        """Convert the threshold object to a dictionary."""
        return {
            'id': self.id,
            'npl_ratio': self.npl_ratio,
            'coverage_ratio': self.coverage_ratio,
            'par_ratio': self.par_ratio,
            'cost_of_risk': self.cost_of_risk,
            'recovery_rate': self.recovery_rate,
            'valid_from': datetime.strptime(str(self.valid_from), '%Y-%m-%d %H:%M:%S') if isinstance(self.valid_from, str) else self.valid_from,
            'valid_to': datetime.strptime(str(self.valid_to), '%Y-%m-%d %H:%M:%S') if self.valid_to and isinstance(self.valid_to, str) else self.valid_to,
            'is_active': self.is_active
        }

# Event listener to ensure only one active threshold for any given time period
@event.listens_for(Threshold, 'before_insert')
@event.listens_for(Threshold, 'before_update')
def check_overlapping_periods(mapper, connection, target):
    if not target.is_active:
        return

    # Check for overlapping periods
    overlapping = Threshold.query.filter(
        Threshold.id != target.id,
        Threshold.is_active == True,
        Threshold.valid_from < (target.valid_to or datetime.max),
        (Threshold.valid_to.is_(None) | (Threshold.valid_to > target.valid_from))
    ).first()

    if overlapping:
        raise ValueError('The validity period overlaps with an existing threshold')
