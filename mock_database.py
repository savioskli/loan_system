from models.client import Client
from models.correspondence import Correspondence
from models.staff import Staff
from models.branch import Branch
from models.client_type import ClientType
from datetime import datetime, timedelta
from extensions import db

def create_mock_data():
    # Create branches
    branches = [
        Branch(name='Main Branch', code='MB001', status='active'),
        Branch(name='Downtown Branch', code='DB001', status='active'),
        Branch(name='Uptown Branch', code='UB001', status='active')
    ]
    for branch in branches:
        db.session.add(branch)
    
    # Create client types
    client_types = [
        ClientType(name='Individual', client_code='IND', description='Individual clients'),
        ClientType(name='Business', client_code='BUS', description='Business clients'),
        ClientType(name='Corporate', client_code='COR', description='Corporate clients')
    ]
    for client_type in client_types:
        db.session.add(client_type)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return
    
    # Create sample clients
    clients = [
        Client(
            client_no='CLI001',
            client_type_id=client_types[0].id,  # Individual
            branch_id=branches[0].id,
            first_name='John',
            middle_name='William',
            last_name='Doe',
            phone='+254712345678',
            email='john.doe@example.com',
            postal_address='P.O Box 123',
            physical_address='123 Main St',
            status='active'
        ),
        Client(
            client_no='CLI002',
            client_type_id=client_types[0].id,  # Individual
            branch_id=branches[1].id,
            first_name='Jane',
            middle_name='Mary',
            last_name='Smith',
            phone='+254723456789',
            email='jane.smith@example.com',
            postal_address='P.O Box 456',
            physical_address='456 Oak Ave',
            status='active'
        ),
        Client(
            client_no='CLI003',
            client_type_id=client_types[1].id,  # Business
            branch_id=branches[2].id,
            business_name='Tech Solutions Ltd',
            registration_no='BUS123',
            phone='+254734567890',
            email='info@techsolutions.com',
            postal_address='P.O Box 789',
            physical_address='789 Tech Park',
            status='active'
        ),
        Client(
            client_no='CLI004',
            client_type_id=client_types[2].id,  # Corporate
            branch_id=branches[0].id,
            business_name='Global Corp Inc',
            registration_no='COR456',
            phone='+254745678901',
            email='contact@globalcorp.com',
            postal_address='P.O Box 012',
            physical_address='012 Corporate Plaza',
            status='active'
        )
    ]
    
    for client in clients:
        db.session.add(client)
    
    # Create sample correspondence
    correspondence_types = ['sms', 'email', 'call']
    messages = [
        'Following up on your loan application.',
        'Your loan payment is due next week.',
        'Thank you for your recent payment.',
        'Please update your contact information.',
        'Your loan has been approved!'
    ]
    
    for client in clients:
        # Add 3-5 correspondence entries for each client
        for _ in range(3):
            correspondence = Correspondence(
                account_no=client.client_no,
                client_name=client.full_name,
                type=correspondence_types[_ % len(correspondence_types)],
                message=messages[_ % len(messages)],
                status='sent',
                sent_by='System Admin',
                staff_id=1,  # You'll need to update this with a valid staff ID
                loan_id=1,  # You'll need to update this with a valid loan ID
                created_at=datetime.utcnow() - timedelta(days=_ * 2)  # Spread out the dates
            )
            db.session.add(correspondence)
    
    try:
        db.session.commit()
        print("Mock data created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating mock data: {str(e)}")

if __name__ == '__main__':
    create_mock_data()
