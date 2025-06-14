from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db
from models.staff import Staff

class LegalCase(db.Model):
    __tablename__ = 'legal_cases'

    id = Column(Integer, primary_key=True)
    loan_id = Column(String(50), nullable=False)
    case_number = Column(String(50), unique=True, nullable=False)
    court_name = Column(String(100), nullable=False)
    case_type = Column(String(50), nullable=False)
    filing_date = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)  # Active, Resolved, Pending, Dismissed
    plaintiff = Column(String(100), nullable=False)
    defendant = Column(String(100), nullable=False)
    amount_claimed = Column(Float, nullable=False)
    lawyer_name = Column(String(100))
    lawyer_contact = Column(String(100))
    description = Column(Text)
    next_hearing_date = Column(DateTime)
    legal_officer_id = Column(Integer)
    legal_officer_name = Column(String(100))
    supervisor_id = Column(Integer)
    supervisor_name = Column(String(100))
    assigned_branch = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attachments = relationship("LegalCaseAttachment", back_populates="legal_case")
    history = relationship("CaseHistory", back_populates="legal_case")

class LegalCaseAttachment(db.Model):
    __tablename__ = 'legal_case_attachments'

    id = Column(Integer, primary_key=True)
    legal_case_id = Column(Integer, ForeignKey('legal_cases.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    legal_case = relationship("LegalCase", back_populates="attachments")

    __table_args__ = (
        db.UniqueConstraint('legal_case_id', 'file_name', name='uq_legal_case_file'),
    )

    def __repr__(self):
        return f'<LegalCaseAttachment {self.id}: {self.file_name}>'

class CaseHistory(db.Model):
    __tablename__ = 'case_history'

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('legal_cases.id'), nullable=False)
    action = Column(String(255), nullable=False)
    action_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    status = Column(String(50), nullable=False)  # Active, Pending, Closed
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer)

    # Relationships
    legal_case = relationship("LegalCase", back_populates="history")
    history_attachments = relationship("CaseHistoryAttachment", back_populates="case_history")

class CaseAttachment(db.Model):
    __tablename__ = 'case_attachments'

    id = Column(Integer, primary_key=True)
    case_history_id = Column(Integer, ForeignKey('case_history.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('case_history_id', 'file_name', name='uq_case_history_file'),
    )
