from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Table, Boolean
from sqlalchemy.orm import relationship
from database import Base

# Association table for notifications and attachments
notification_attachments = Table(
    'notification_attachments',
    Base.metadata,
    Column('notification_id', Integer, ForeignKey('guarantor_notifications.id'), primary_key=True),
    Column('attachment_id', Integer, ForeignKey('notification_attachments.id'), primary_key=True)
)

class GuarantorNotification(Base):
    __tablename__ = 'guarantor_notifications'

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(50), nullable=False)
    customer_name = Column(String(100), nullable=False)
    account_no = Column(String(50), nullable=False)
    notification_type = Column(String(50), nullable=False)  # SMS, Email, Both
    notification_category = Column(String(50), nullable=False)  # Payment Due, Payment Overdue, etc.
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    status = Column(String(20), default='Pending')  # Pending, Sent, Failed
    sent_at = Column(DateTime)
    
    # Relationships
    attachments = relationship('NotificationAttachment', secondary=notification_attachments)
    recipients = relationship('NotificationRecipient', back_populates='notification')

class NotificationAttachment(Base):
    __tablename__ = 'notification_attachments'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey('users.id'))

class NotificationRecipient(Base):
    __tablename__ = 'notification_recipients'

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('guarantor_notifications.id'))
    guarantor_id = Column(String(50), nullable=False)
    guarantor_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    email = Column(String(100))
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    notification = relationship('GuarantorNotification', back_populates='recipients')
