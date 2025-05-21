from extensions import db
from datetime import datetime

class County(db.Model):
    __tablename__ = 'counties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Relationships
    subcounties = db.relationship('SubCounty', backref='county', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<County {self.name}>'

class SubCounty(db.Model):
    __tablename__ = 'subcounties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    county_id = db.Column(db.Integer, db.ForeignKey('counties.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Relationships
    wards = db.relationship('Ward', backref='subcounty', lazy=True, cascade='all, delete-orphan')
    
    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('name', 'county_id', name='uq_subcounty_name_county'),
    )
    
    def __repr__(self):
        return f'<SubCounty {self.name}>'

class Ward(db.Model):
    __tablename__ = 'wards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subcounty_id = db.Column(db.Integer, db.ForeignKey('subcounties.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    
    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('name', 'subcounty_id', name='uq_ward_name_subcounty'),
    )
    
    def __repr__(self):
        return f'<Ward {self.name}>'
