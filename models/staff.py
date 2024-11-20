from flask_login import UserMixin
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Staff(UserMixin, db.Model):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    branch = db.relationship('Branch', foreign_keys=[branch_id], back_populates='staff_members')
    activities = db.relationship('ActivityLog', backref='staff', lazy='dynamic')
    role = db.relationship('Role', foreign_keys=[role_id], backref=db.backref('staff_members', lazy='dynamic'))

    def __init__(self, email, first_name, last_name, password=None, role_id=None, phone=None, branch_id=None, is_active=False):
        self.email = email.lower()
        self.first_name = first_name
        self.last_name = last_name
        if password:
            self.set_password(password)
        self.role_id = role_id
        self.phone = phone
        self.branch_id = branch_id
        self.is_active = is_active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role.name.lower() == 'admin'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<Staff {self.email}>'
