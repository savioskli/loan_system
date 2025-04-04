from extensions import db
from datetime import datetime

class CollectionSchedule(db.Model):
    __tablename__ = 'collection_schedules'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    assigned_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)  # Changed from staff_id
    client_id = db.Column(db.Integer, nullable=False)  # Reference to external core banking system
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=True)
    
    # Collection Staff Assignment
    assigned_branch = db.Column(db.String(100), nullable=False)
    assignment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    follow_up_deadline = db.Column(db.DateTime, nullable=False)
    collection_priority = db.Column(db.String(20), nullable=False)  # High, Medium, Low
    
    # Follow-up Plan
    follow_up_frequency = db.Column(db.String(20), nullable=False)  # Daily, Weekly, Bi-Weekly
    next_follow_up_date = db.Column(db.DateTime, nullable=False)
    preferred_collection_method = db.Column(db.String(50), nullable=False)  # Phone Call, Physical Visit, Legal Action
    promised_payment_date = db.Column(db.DateTime, nullable=True)
    attempts_allowed = db.Column(db.Integer, nullable=False, default=3)
    attempts_made = db.Column(db.Integer, nullable=False, default=0)
    
    # Task & Progress Tracking
    task_description = db.Column(db.Text, nullable=True)
    progress_status = db.Column(db.String(20), nullable=False, default='Not Started')  # Not Started, In Progress, Completed, Escalated
    escalation_level = db.Column(db.Integer, nullable=True)
    resolution_date = db.Column(db.DateTime, nullable=True)
    
    # Loan Details
    outstanding_balance = db.Column(db.Float, nullable=True)
    missed_payments = db.Column(db.Integer, nullable=True)
    
    # Contact Details
    best_contact_time = db.Column(db.String(20), nullable=True)  # Morning, Afternoon, Evening
    collection_location = db.Column(db.String(200), nullable=True)
    alternative_contact = db.Column(db.String(200), nullable=True)
    
    # Supervisor/Manager Review
    reviewed_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)
    approval_date = db.Column(db.DateTime, nullable=True)
    special_instructions = db.Column(db.Text, nullable=True)
    
    # Workflow
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=True)
    progress_status = db.Column(db.String(20), nullable=False, default='Not Started')
    
    # Relationships
    loan = db.relationship('Loan', backref=db.backref('collection_schedules', lazy=True))
    assigned_staff = db.relationship('Staff', foreign_keys=[assigned_id], backref=db.backref('assigned_schedules', lazy=True))
    supervisor = db.relationship('Staff', foreign_keys=[supervisor_id], backref=db.backref('supervised_schedules', lazy=True))
    manager = db.relationship('Staff', foreign_keys=[manager_id], backref=db.backref('managed_schedules', lazy=True))
    reviewer = db.relationship('Staff', foreign_keys=[reviewed_by], backref=db.backref('reviewed_schedules', lazy=True))
    workflow = db.relationship('Workflow', backref='workflow_schedules', lazy=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CollectionSchedule {self.id}>'

    def to_dict(self):
        """Convert the collection schedule to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'assigned_id': self.assigned_id,
            'staff_name': f"{self.assigned_staff.first_name} {self.assigned_staff.last_name}" if self.assigned_staff else None,
            'loan_id': self.loan_id,
            'loan_account': self.loan.account_no if self.loan else None,
            'borrower_name': self.loan.client.full_name if self.loan and self.loan.client else None,
            'supervisor_id': self.supervisor_id,
            'supervisor_name': f"{self.supervisor.first_name} {self.supervisor.last_name}" if self.supervisor else None,
            'manager_id': self.manager_id,
            'manager_name': f"{self.manager.first_name} {self.manager.last_name}" if self.manager else None,
            'assigned_branch': self.assigned_branch,
            'assignment_date': self.assignment_date.isoformat() if self.assignment_date else None,
            'follow_up_deadline': self.follow_up_deadline.isoformat() if self.follow_up_deadline else None,
            'collection_priority': self.collection_priority,
            'follow_up_frequency': self.follow_up_frequency,
            'next_follow_up_date': self.next_follow_up_date.isoformat() if self.next_follow_up_date else None,
            'preferred_collection_method': self.preferred_collection_method,
            'promised_payment_date': self.promised_payment_date.isoformat() if self.promised_payment_date else None,
            'attempts_allowed': self.attempts_allowed,
            'attempts_made': self.attempts_made,
            'task_description': self.task_description,
            'progress_status': self.progress_status,
            'escalation_level': self.escalation_level,
            'resolution_date': self.resolution_date.isoformat() if self.resolution_date else None,
            'special_instructions': self.special_instructions,
            'collection_location': self.collection_location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CollectionScheduleProgress(db.Model):
    __tablename__ = 'collection_schedule_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    collection_schedule_id = db.Column(db.Integer, db.ForeignKey('collection_schedules.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    collection_schedule = db.relationship('CollectionSchedule', backref=db.backref('supervisor_updates', lazy=True))