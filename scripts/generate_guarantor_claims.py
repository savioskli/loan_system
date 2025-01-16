import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from extensions import db
from models.guarantor_claim import GuarantorClaim
from datetime import datetime, timedelta
import random

# Kenyan names for sample data
KENYAN_FIRST_NAMES = [
    'John', 'Mary', 'David', 'Sarah', 'Peter', 'Elizabeth', 'James', 'Grace', 
    'Michael', 'Agnes', 'Daniel', 'Ruth', 'Joseph', 'Esther', 'Samuel', 'Rebecca'
]

KENYAN_LAST_NAMES = [
    'Ochieng', 'Mutua', 'Kamau', 'Njoroge', 'Muthomi', 'Wanjiru', 'Kipkorir', 
    'Chebet', 'Kiptoo', 'Akinyi', 'Otieno', 'Mwangi', 'Kimani', 'Njeri', 'Gitau'
]

STATUSES = ['Pending', 'Resolved', 'In Progress']

def generate_name():
    return f"{random.choice(KENYAN_FIRST_NAMES)} {random.choice(KENYAN_LAST_NAMES)}"

def generate_guarantor_claims(num_claims=50):
    app = create_app()
    
    with app.app_context():
        # Clear existing claims
        GuarantorClaim.query.delete()
        
        # Generate new claims
        for _ in range(num_claims):
            claim = GuarantorClaim(
                guarantor_name=generate_name(),
                borrower_name=generate_name(),
                guarantor_contact=f"+254{random.randint(700000000, 799999999)}",
                borrower_contact=f"+254{random.randint(700000000, 799999999)}",
                amount_paid=round(random.uniform(1000, 100000), 2),
                claim_date=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
                status=random.choice(STATUSES),
                claim_description=f"Loan default claim for {generate_name()}"
            )
            db.session.add(claim)
        
        db.session.commit()
        print(f"Generated {num_claims} guarantor claims.")

if __name__ == '__main__':
    generate_guarantor_claims()
