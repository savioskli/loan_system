from datetime import datetime
from extensions import db

class Branch(db.Model):
    __tablename__ = 'branches'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    branch_code = db.Column(db.String(20), unique=True, nullable=False)
    branch_name = db.Column(db.String(100), nullable=False)
    lower_limit = db.Column(db.Numeric(10, 2), nullable=False)
    upper_limit = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    is_active = db.Column(db.Boolean, default=True)

    # Define relationships with proper foreign key specifications
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_branches')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_branches')
    staff_members = db.relationship('Staff', back_populates='branch', 
                                  primaryjoin='Branch.id==Staff.branch_id')

    def __repr__(self):
        return f'<Branch {self.branch_name}>'
