from extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from datetime import datetime
from models.member import Member

class LetterType(db.Model):
    __tablename__ = 'letter_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to letter templates
    templates = relationship('LetterTemplate', back_populates='letter_type', cascade='all, delete-orphan')
    demand_letters = relationship('DemandLetter', back_populates='letter_type')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active
        }

class LetterTemplate(db.Model):
    __tablename__ = 'letter_templates'

    id = Column(Integer, primary_key=True)
    letter_type_id = Column(Integer, ForeignKey('letter_types.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    template_content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to letter type
    letter_type = relationship('LetterType', back_populates='templates')
    demand_letters = relationship('DemandLetter', back_populates='letter_template')

    def to_dict(self):
        return {
            'id': self.id,
            'letter_type_id': self.letter_type_id,
            'name': self.name,
            'template_content': self.template_content,
            'is_active': self.is_active,
            'letter_type_name': self.letter_type.name if self.letter_type else None
        }

class DemandLetter(db.Model):
    __tablename__ = 'demand_letters'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    letter_type_id = Column(Integer, ForeignKey('letter_types.id'), nullable=False)
    letter_template_id = Column(Integer, ForeignKey('letter_templates.id'), nullable=False)

    amount_outstanding = Column(Numeric(10, 2), nullable=False)
    letter_content = Column(Text, nullable=True)

    status = Column(String(50), default='Draft')  # Draft, Sent, Delivered, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

    # Relationships
    member = relationship('Member', back_populates='demand_letters')
    letter_type = relationship('LetterType', back_populates='demand_letters')
    letter_template = relationship('LetterTemplate', back_populates='demand_letters')
