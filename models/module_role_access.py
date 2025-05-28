from extensions import db

class ModuleRoleAccess(db.Model):
    __tablename__ = 'module_role_access'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    can_create = db.Column(db.Boolean, default=False)
    can_read = db.Column(db.Boolean, default=False)
    can_update = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)
    
    # Relationships
    role = db.relationship('Role', backref='module_access')
    module = db.relationship('Module', backref='role_access')
    
    def __repr__(self):
        return f'<ModuleRoleAccess {self.role.name} - {self.module.name}>'
