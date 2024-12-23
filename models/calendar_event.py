from extensions import db
from datetime import datetime

class CalendarEvent(db.Model):
    """Model for calendar events."""
    __tablename__ = 'calendar_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_type = db.Column(db.String(50), nullable=False)  # follow-up, meeting, reminder, other
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    all_day = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    
    # Foreign Keys
    created_by_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = db.relationship('Staff', backref=db.backref('calendar_events', lazy=True))
    client = db.relationship('Client', backref=db.backref('calendar_events', lazy=True))
    loan = db.relationship('Loan', backref=db.backref('calendar_events', lazy=True))

    def __init__(self, title, event_type, start_time, created_by_id, **kwargs):
        self.title = title
        self.event_type = event_type
        self.start_time = start_time
        self.created_by_id = created_by_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """Convert event to dictionary format for API responses."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.event_type,
            'start': self.start_time.isoformat(),
            'end': self.end_time.isoformat() if self.end_time else None,
            'allDay': self.all_day,
            'status': self.status,
            'createdBy': self.created_by_id,
            'clientId': self.client_id,
            'loanId': self.loan_id,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }

    @classmethod
    def create_event(cls, data, created_by_id):
        """Create a new calendar event."""
        try:
            # Convert date and time to datetime
            if 'date' in data and 'time' in data:
                start_time = datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M")
            else:
                start_time = datetime.fromisoformat(data.get('start', '').replace('Z', '+00:00'))

            # Create event
            event = cls(
                title=data['title'],
                description=data.get('description'),
                event_type=data['type'],
                start_time=start_time,
                all_day=data.get('all_day', False),
                created_by_id=created_by_id,
                client_id=data.get('client_id'),
                loan_id=data.get('loan_id')
            )

            # Add to session and commit
            db.session.add(event)
            db.session.commit()
            return event

        except Exception as e:
            db.session.rollback()
            raise e

    def update_event(self, data):
        """Update an existing calendar event."""
        try:
            # Update fields
            if 'title' in data:
                self.title = data['title']
            if 'description' in data:
                self.description = data['description']
            if 'type' in data:
                self.event_type = data['type']
            if 'date' in data and 'time' in data:
                self.start_time = datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M")
            elif 'start' in data:
                self.start_time = datetime.fromisoformat(data['start'].replace('Z', '+00:00'))
            if 'all_day' in data:
                self.all_day = data['all_day']
            if 'status' in data:
                self.status = data['status']
            if 'client_id' in data:
                self.client_id = data['client_id']
            if 'loan_id' in data:
                self.loan_id = data['loan_id']

            db.session.commit()
            return self

        except Exception as e:
            db.session.rollback()
            raise e

    def delete_event(self):
        """Delete a calendar event."""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
