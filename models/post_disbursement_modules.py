from datetime import datetime
from extensions import db

class PostDisbursementModule(db.Model):
    __tablename__ = 'post_disbursement_modules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    url = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('post_disbursement_modules.id'))
    parent = db.relationship('PostDisbursementModule', remote_side=[id], backref='post_disbursement_submodules')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    hidden = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    selected_tables = db.Column(db.JSON, default=[])  # JSON field to store selected tables

    def __repr__(self):
        return f'<PostDisbursementModule {self.name}>'

class ExpectedStructure(db.Model):
    __tablename__ = 'expected_structures'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('post_disbursement_modules.id'), nullable=False)
    table_name = db.Column(db.String(80), nullable=False)
    columns = db.Column(db.JSON, nullable=False)  # JSON field to store list of columns

    # Relationship to PostDisbursementModule
    module = db.relationship('PostDisbursementModule', backref=db.backref('expected_structures', lazy=True))

    def __repr__(self):
        return f'<ExpectedStructure for Module {self.module_id}: {self.table_name}>'

class ActualStructure(db.Model):
    __tablename__ = 'actual_structures'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expected_structure_id = db.Column(db.Integer, db.ForeignKey('expected_structures.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('post_disbursement_modules.id'), nullable=False)
    table_name = db.Column(db.String(80), nullable=False)
    columns = db.Column(db.JSON, nullable=False)  # JSON field to store list of columns

    # Relationships
    expected_structure = db.relationship('ExpectedStructure', backref=db.backref('actual_structures', lazy=True))
    module = db.relationship('PostDisbursementModule', backref=db.backref('actual_structures', lazy=True))

    def __repr__(self):
        return f'<ActualStructure for Expected Structure {self.expected_structure_id}: {self.table_name}>'
