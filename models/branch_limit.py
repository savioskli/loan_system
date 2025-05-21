from datetime import datetime
from extensions import db

class BranchLimit(db.Model):
    __tablename__ = 'branch_limits'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    min_amount = db.Column(db.Numeric(15, 2), nullable=False)
    max_amount = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    is_active = db.Column(db.Boolean, default=True)

    # Define relationships
    branch = db.relationship('Branch', backref='limits')
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_branch_limits')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_branch_limits')

    def __init__(self, branch_id, min_amount, max_amount, created_by=None):
        self.branch_id = branch_id
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.created_by = created_by
        self.updated_by = created_by
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True

    def update(self, min_amount=None, max_amount=None, updated_by=None):
        if min_amount is not None:
            self.min_amount = min_amount
        if max_amount is not None:
            self.max_amount = max_amount
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<BranchLimit {self.branch.name}: {self.min_amount} - {self.max_amount}>'
