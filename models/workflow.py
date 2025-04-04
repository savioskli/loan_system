from extensions import db
from datetime import datetime

class Workflow(db.Model):
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    steps = db.relationship('CollectionWorkflowStep', backref='workflow_steps', lazy=True)
    schedules = db.relationship('CollectionSchedule', backref='workflow_schedules', lazy=True)

class CollectionWorkflowStep(db.Model):
    __tablename__ = 'collection_workflow_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique step order within a workflow
    __table_args__ = (
        db.UniqueConstraint('workflow_id', 'step_order', name='uq_workflow_step_order'),
    )
    
    # Relationships
    workflow = db.relationship('Workflow', backref='workflow_steps', lazy=True)
    
    def __repr__(self):
        return f'<CollectionWorkflowStep {self.name} (Order: {self.step_order})>'
