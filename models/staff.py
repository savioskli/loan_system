from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Staff(UserMixin, db.Model):
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    status = db.Column(db.String(20), default='active')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    approved_by = db.relationship('Staff', remote_side=[id], backref='approved_staff')
    role = db.relationship('Role', foreign_keys=[role_id])
    branch = db.relationship('Branch', foreign_keys=[branch_id])
    
    @property
    def full_name(self):
        """Get the full name of the staff member."""
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        """Set the password hash for the staff member."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if the provided password matches the staff member's password."""
        return check_password_hash(self.password_hash, password)
    
    def approve(self, approver):
        """Approve the staff member."""
        self.status = 'approved'
        self.approved_by_id = approver.id
        self.approved_at = datetime.utcnow()
    
    def reject(self, approver):
        """Reject the staff member."""
        self.status = 'rejected'
        self.approved_by_id = approver.id
        self.approved_at = datetime.utcnow()
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def has_role(self, role_name):
        """Check if the staff member has a specific role."""
        return self.role and self.role.name.lower() == role_name.lower()
    
    @property
    def is_admin(self):
        """Check if the staff member is an admin."""
        return self.role and self.role.name.lower() == 'admin'
    
    def __repr__(self):
        return f'<Staff {self.username}: {self.full_name}>'