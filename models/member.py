from extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

class Member(db.Model):
    __tablename__ = 'members'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    demand_letters = relationship('DemandLetter', back_populates='member')
    
    def __repr__(self):
        return f'<Member {self.full_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'is_active': self.is_active
        }
