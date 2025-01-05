from extensions import db
from datetime import datetime

class Correspondence(db.Model):
    __tablename__ = 'correspondence'
    
    id = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.String(50), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # sms, email, call, letter, visit
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # sent, delivered, failed, pending
    sent_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # If it's an SMS or email
    recipient = db.Column(db.String(100))
    delivery_status = db.Column(db.String(50))
    delivery_time = db.Column(db.DateTime)
    
    # If it's a call
    call_duration = db.Column(db.Integer)  # in seconds
    call_outcome = db.Column(db.String(50))
    
    # If it's a site visit
    location = db.Column(db.String(200))
    visit_purpose = db.Column(db.String(200))
    visit_outcome = db.Column(db.String(200))
    
    # Relationships
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    attachment_path = db.Column(db.String(500))
    
    staff = db.relationship('Staff', backref=db.backref('correspondence', lazy=True))
    
    def __repr__(self):
        return f'<Correspondence {self.id} - {self.type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'account_no': self.account_no,
            'client_name': self.client_name,
            'type': self.type,
            'message': self.message,
            'status': self.status,
            'sent_by': self.sent_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'recipient': self.recipient,
            'delivery_status': self.delivery_status,
            'delivery_time': self.delivery_time.isoformat() if self.delivery_time else None,
            'call_duration': self.call_duration,
            'call_outcome': self.call_outcome,
            'location': self.location,
            'visit_purpose': self.visit_purpose,
            'visit_outcome': self.visit_outcome,
            'staff_id': self.staff_id,
            'attachment_path': self.attachment_path
        }

    @classmethod
    def sync_from_core_banking(cls, member_id=None, start_date=None, end_date=None):
        """
        Sync communications from core banking system
        """
        from utils.core_banking import get_endpoint_data
        
        # Prepare parameters for the API call
        params = {}
        if member_id:
            params['member_id'] = member_id
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
            
        # Get communications from core banking
        communications = get_endpoint_data('loan_communications', params)
        
        if not communications:
            return []
            
        synced_records = []
        for comm in communications:
            # Check if communication already exists
            existing = cls.query.filter_by(
                created_at=datetime.fromisoformat(comm['SentDate'])
            ).first()
            
            if not existing:
                # Create new communication record
                new_comm = cls(
                    account_no=comm.get('LoanNo', ''),
                    client_name=comm.get('MemberName', ''),
                    type=comm['CommunicationType'].lower(),
                    message=comm['MessageContent'],
                    status='completed',
                    sent_by=comm.get('SentByUser', ''),
                    created_at=datetime.fromisoformat(comm['SentDate']),
                    delivery_status=comm['DeliveryStatus'],
                    delivery_time=datetime.fromisoformat(comm['SentDate']),
                    staff_id=comm.get('SentBy', 1),  # Default to admin if not found
                )
                
                if comm.get('ResponseReceived'):
                    new_comm.message += f"\n\nResponse: {comm['ResponseReceived']}"
                    new_comm.updated_at = datetime.fromisoformat(comm['ResponseDate']) if comm.get('ResponseDate') else None
                
                db.session.add(new_comm)
                synced_records.append(new_comm)
        
        if synced_records:
            db.session.commit()
            
        return synced_records

    @classmethod
    def get_communications(cls, member_id=None, start_date=None, end_date=None, sync_first=True):
        """
        Get all communications, optionally syncing from core banking first
        """
        if sync_first:
            cls.sync_from_core_banking(member_id, start_date, end_date)
        
        query = cls.query
        
        if member_id:
            query = query.join(cls.staff).filter(cls.staff.has(member_id=member_id))
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)
            
        return query.order_by(cls.created_at.desc()).all()
