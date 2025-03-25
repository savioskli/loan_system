from datetime import datetime
from extensions import db

class Branch(db.Model):
    __tablename__ = 'branches'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
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

    def __init__(self, code, name, address=None, created_by=None):
        self.code = code
        self.name = name
        self.address = address
        self.created_by = created_by
        self.updated_by = created_by
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True

    def update(self, code=None, name=None, address=None, updated_by=None):
        if code is not None:
            self.code = code
        if name is not None:
            self.name = name
        if address is not None:
            self.address = address
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<Branch {self.name}>'
