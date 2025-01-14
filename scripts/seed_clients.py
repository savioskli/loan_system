from datetime import datetime
from models.client import Client
from models.client_type import ClientType
from models.staff import Staff
from extensions import db
from app import create_app

def seed_clients():
    app = create_app()
    with app.app_context():
        # First ensure we have staff and client types
        staff = Staff.query.first()
        if not staff:
            print("Please ensure there is at least one staff member in the database")
            return

        client_type = ClientType.query.filter_by(client_code='IND').first()
        if not client_type:
            print("Please ensure there is an individual client type in the database")
            return

        # Sample Kenyan clients
        sample_clients = [
            {
                "first_name": "Wanjiku",
                "middle_name": "",
                "last_name": "Kamau",
                "id_number": "12345678",
                "phone": "+254712345678",
                "email": "wanjiku.kamau@example.com"
            },
            {
                "first_name": "Odhiambo",
                "middle_name": "",
                "last_name": "Otieno",
                "id_number": "23456789",
                "phone": "+254723456789",
                "email": "odhiambo.otieno@example.com"
            },
            {
                "first_name": "Aisha",
                "middle_name": "",
                "last_name": "Mwangi",
                "id_number": "34567890",
                "phone": "+254734567890",
                "email": "aisha.mwangi@example.com"
            },
            {
                "first_name": "Kipchoge",
                "middle_name": "",
                "last_name": "Kipruto",
                "id_number": "45678901",
                "phone": "+254745678901",
                "email": "kipchoge.kipruto@example.com"
            },
            {
                "first_name": "Njeri",
                "middle_name": "",
                "last_name": "Gathoni",
                "id_number": "56789012",
                "phone": "+254756789012",
                "email": "njeri.gathoni@example.com"
            }
        ]

        # Create client records
        for client_data in sample_clients:
            client = Client(
                client_type_id=client_type.id,
                form_data=client_data,
                status='Active',
                created_by=staff.id,
                updated_by=staff.id
            )
            db.session.add(client)

        try:
            db.session.commit()
            print("Successfully added sample client records")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding records: {str(e)}")

if __name__ == "__main__":
    seed_clients()
