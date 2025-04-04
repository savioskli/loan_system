from datetime import datetime
from extensions import db
from sqlalchemy.dialects.mysql import JSON

class WorkflowDefinition(db.Model):
    __tablename__ = 'workflow_definitions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    module_id = db.Column(db.Integer, db.ForeignKey('post_disbursement_modules.id'))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    module = db.relationship('PostDisbursementModule', backref='workflows')
    steps = db.relationship('WorkflowStep', backref='workflow', cascade='all, delete-orphan')
    creator = db.relationship('Staff', foreign_keys=[created_by], backref='created_workflows')
    updater = db.relationship('Staff', foreign_keys=[updated_by], backref='updated_workflows')

    def __repr__(self):
        return f'<WorkflowDefinition {self.name}>'

class WorkflowStep(db.Model):
    __tablename__ = 'workflow_steps'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_definitions.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    step_order = db.Column(db.Integer, default=0)  # Order of execution in the workflow
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)  # Role responsible for this step
    is_start_step = db.Column(db.Boolean, default=False)  # Indicates if this is the starting step
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    role = db.relationship('Role', backref='workflow_steps')
    next_steps = db.relationship('WorkflowTransition', 
                                foreign_keys='WorkflowTransition.from_step_id',
                                backref='from_step', 
                                cascade='all, delete-orphan')

    def __repr__(self):
        return f'<WorkflowStep {self.name} for Workflow {self.workflow_id}>'

class WorkflowTransition(db.Model):
    __tablename__ = 'workflow_transitions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_definitions.id'), nullable=False)
    from_step_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'), nullable=False)
    to_step_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'), nullable=False)
    transition_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    workflow = db.relationship('WorkflowDefinition', backref='transitions')
    to_step = db.relationship('WorkflowStep', foreign_keys=[to_step_id], backref='incoming_transitions')

    def __repr__(self):
        return f'<WorkflowTransition {self.transition_name} from {self.from_step_id} to {self.to_step_id}>'

class WorkflowInstance(db.Model):
    __tablename__ = 'workflow_instances'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_definitions.id'), nullable=False)
    current_step_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Relationships
    workflow = db.relationship('WorkflowDefinition', backref='instances')
    current_step = db.relationship('WorkflowStep', backref='active_instances')
    creator = db.relationship('Staff', backref='initiated_workflows')
    history = db.relationship('WorkflowHistory', backref='instance', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<WorkflowInstance {self.id} for Workflow {self.workflow_id}>'

class WorkflowHistory(db.Model):
    __tablename__ = 'workflow_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instance_id = db.Column(db.Integer, db.ForeignKey('workflow_instances.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'), nullable=False)
    transition_id = db.Column(db.Integer, db.ForeignKey('workflow_transitions.id'))
    action = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.Text)
    performed_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    performed_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    step = db.relationship('WorkflowStep')
    transition = db.relationship('WorkflowTransition')
    performer = db.relationship('Staff', backref='workflow_actions')

    def __repr__(self):
        return f'<WorkflowHistory {self.id} for Instance {self.instance_id}>'
