from extensions import db
from datetime import datetime
from models.staff import Staff

class LoanImpact(db.Model):
    __tablename__ = 'loan_impact'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loan_id = db.Column(db.Integer, nullable=False, index=True)
    impact_category_id = db.Column(db.Integer, db.ForeignKey('impact_categories.id'), nullable=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    verification_status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Verified, Rejected
    verification_notes = db.Column(db.Text)
    verified_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    verification_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    category = db.relationship('ImpactCategory', backref='loan_impacts')
    submitter = db.relationship('Staff', foreign_keys=[submitted_by], backref='submitted_impacts')
    verifier = db.relationship('Staff', foreign_keys=[verified_by], backref='verified_impacts')
    values = db.relationship('ImpactValue', backref='loan_impact', cascade='all, delete-orphan')
    evidence = db.relationship('ImpactEvidence', backref='loan_impact', cascade='all, delete-orphan')

class ImpactValue(db.Model):
    __tablename__ = 'impact_values'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loan_impact_id = db.Column(db.Integer, db.ForeignKey('loan_impact.id'), nullable=False)
    impact_metric_id = db.Column(db.Integer, db.ForeignKey('impact_metrics.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)  # Store all values as text, convert as needed
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    metric = db.relationship('ImpactMetric', backref='values')

class ImpactEvidence(db.Model):
    __tablename__ = 'impact_evidence'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loan_impact_id = db.Column(db.Integer, db.ForeignKey('loan_impact.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    uploader = db.relationship('Staff', backref='uploaded_evidence')
