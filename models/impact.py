from datetime import datetime
from extensions import db

class ImpactCategory(db.Model):
    """Model for loan impact categories"""
    __tablename__ = 'impact_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    metrics = db.relationship('ImpactMetric', backref='category', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ImpactCategory {self.name}>'

class ImpactMetric(db.Model):
    """Model for impact metrics associated with categories"""
    __tablename__ = 'impact_metrics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    impact_category_id = db.Column(db.Integer, db.ForeignKey('impact_categories.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.String(20), nullable=False)  # text, number, boolean, date
    unit = db.Column(db.String(50))  # e.g., kg, acres, percentage
    required = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f'<ImpactMetric {self.name} for {self.category.name}>'
