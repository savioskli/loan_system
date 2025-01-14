from datetime import datetime, timedelta
from models.calendar_event import CalendarEvent
from models.staff import Staff
from models.client import Client
from models.loan import Loan
from extensions import db
from app import create_app
import random

def seed_calendar_events():
    app = create_app()
    with app.app_context():
        # First ensure we have staff, clients and loans
        staff = Staff.query.first()
        if not staff:
            print("Please ensure there is at least one staff member in the database")
            return

        clients = Client.query.all()
        if not clients:
            print("Please ensure there are clients in the database")
            return

        loans = Loan.query.all()
        
        # Event types and their descriptions
        event_types = {
            'follow-up': [
                "Loan payment follow-up call with {client}",
                "Follow up on pending documentation from {client}",
                "Check business progress with {client}"
            ],
            'meeting': [
                "Site visit to {client}'s business",
                "Loan review meeting with {client}",
                "Financial advisory session with {client}"
            ],
            'reminder': [
                "Loan payment due - {client}",
                "Document submission deadline - {client}",
                "Loan restructuring discussion with {client}"
            ]
        }

        # Current time reference
        current_time = datetime(2025, 1, 14, 10, 21, 14)  # Using the provided current time
        
        # Generate events for January and February 2025
        events = []
        
        # Create events for each client
        for client in clients:
            # Get client's name from form_data
            client_name = client.full_name
            
            # Get client's loan if exists
            client_loan = next((loan for loan in loans if loan.client_id == client.id), None)
            
            # January events
            jan_start = datetime(2025, 1, 1)
            jan_end = datetime(2025, 1, 31)
            
            # February events
            feb_start = datetime(2025, 2, 1)
            feb_end = datetime(2025, 2, 28)
            
            for month_start, month_end in [(jan_start, jan_end), (feb_start, feb_end)]:
                # 2-3 events per client per month
                num_events = random.randint(2, 3)
                
                for _ in range(num_events):
                    event_type = random.choice(list(event_types.keys()))
                    
                    # Generate random time between 9 AM and 5 PM
                    event_date = month_start + timedelta(days=random.randint(0, (month_end - month_start).days))
                    event_time = timedelta(hours=random.randint(9, 16), minutes=random.choice([0, 15, 30, 45]))
                    event_datetime = datetime.combine(event_date.date(), (datetime.min + event_time).time())
                    
                    # Skip if event is in the past
                    if event_datetime < current_time:
                        continue
                    
                    # Create event title
                    title_template = random.choice(event_types[event_type])
                    title = title_template.format(client=client_name)
                    
                    # Create event description
                    descriptions = {
                        'follow-up': f"Regular follow-up with {client_name} regarding loan status and business progress.",
                        'meeting': f"Scheduled meeting with {client_name} to discuss loan terms and business performance.",
                        'reminder': f"Payment reminder for {client_name}'s loan installment."
                    }
                    
                    # Create the event
                    event = CalendarEvent(
                        title=title,
                        description=descriptions[event_type],
                        event_type=event_type,
                        start_time=event_datetime,
                        end_time=event_datetime + timedelta(hours=1),
                        all_day=False,
                        status='scheduled',
                        created_by_id=staff.id,
                        client_id=client.id,
                        loan_id=client_loan.id if client_loan else None
                    )
                    events.append(event)

        # Bulk insert all events
        try:
            db.session.bulk_save_objects(events)
            db.session.commit()
            print(f"Successfully added {len(events)} calendar events")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding records: {str(e)}")

if __name__ == "__main__":
    seed_calendar_events()
