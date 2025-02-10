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

