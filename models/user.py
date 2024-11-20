from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    approved_by = db.relationship('User', remote_side=[id], backref='approved_users')
    role = db.relationship('Role', foreign_keys=[role_id])  # Removed conflicting backref
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def approve(self, approver):
        self.status = 'approved'
        self.approved_by_id = approver.id
        self.approved_at = datetime.utcnow()
    
    def reject(self, approver):
        self.status = 'rejected'
        self.approved_by_id = approver.id
        self.approved_at = datetime.utcnow()
    
    @property
    def is_admin(self):
        return self.role and self.role.name == 'Admin'
        
    def __repr__(self):
        return f'<User {self.email}>'
