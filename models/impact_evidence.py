from datetime import datetime
from extensions import db

class ImpactEvidence(db.Model):
    """Model for storing evidence files related to impact assessments."""
    __tablename__ = 'impact_evidence'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    verification_notes = db.Column(db.Text, nullable=True)
    verified_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    verification_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    uploader = db.relationship('Staff', foreign_keys=[uploaded_by])
    verifier = db.relationship('Staff', foreign_keys=[verified_by])
    submission = db.relationship('FormSubmission', backref=db.backref('evidence_files', lazy=True))

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'field_name': self.field_name,
            'file_name': self.file_name,
            'original_name': self.original_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'uploaded_by': self.uploaded_by,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'is_verified': self.is_verified,
            'verification_notes': self.verification_notes,
            'verified_by': self.verified_by,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'download_url': f'/download/evidence/{self.id}'
        }

    def __repr__(self):
        return f'<ImpactEvidence {self.original_name} for submission {self.submission_id}>'
