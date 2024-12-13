from extensions import db
import json

class FieldDependency(db.Model):
    __tablename__ = 'field_dependencies'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_field_id = db.Column(db.Integer, db.ForeignKey('form_fields.id', ondelete='CASCADE'), nullable=False)
    dependent_field_id = db.Column(db.Integer, db.ForeignKey('form_fields.id', ondelete='CASCADE'), nullable=False)
    show_on_values = db.Column(db.Text, nullable=False)  # JSON array of values that will show the dependent field
    
    # Relationships
    parent_field = db.relationship('FormField', foreign_keys=[parent_field_id], backref='dependencies')
    dependent_field = db.relationship('FormField', foreign_keys=[dependent_field_id], backref='dependent_on')
    
    def get_show_values(self):
        """Get the list of values that will show this dependent field"""
        return json.loads(self.show_on_values)
    
    def set_show_values(self, values):
        """Set the list of values that will show this dependent field"""
        self.show_on_values = json.dumps(values)
