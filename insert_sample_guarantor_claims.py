import sys
import traceback
from datetime import datetime
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config
from models.guarantor_claim import GuarantorClaim

def generate_kenyan_names():
    """Generate realistic Kenyan names."""
    first_names = [
        'Mary', 'John', 'Grace', 'Peter', 'Elizabeth', 
        'James', 'Sarah', 'David', 'Anna', 'Michael',
        'Ruth', 'Daniel', 'Esther', 'Joseph', 'Jane',
        'Samuel', 'Catherine', 'Paul', 'Margaret', 'Simon'
    ]
    last_names = [
        'Mutegi', 'Mwangi', 'Kamau', 'Ochieng', 'Njoroge', 
        'Kimani', 'Otieno', 'Muthomi', 'Wanjiru', 'Kipkorir',
        'Akinyi', 'Chebet', 'Kiptoo', 'Chepkosgei', 'Mutua'
    ]
    return random.choice(first_names), random.choice(last_names)

def generate_kenyan_phone_number():
    """Generate a realistic Kenyan phone number."""
    prefixes = ['070', '071', '072', '074', '075', '076', '077', '078', '079']
    return f"0{random.choice(prefixes)}{random.randint(100000, 999999)}"

def create_guarantor_claims_table(engine):
    """Create the guarantor_claims table if it doesn't exist."""
    Base = declarative_base()
    
    # Create table SQL
    create_table_sql = text('''
    CREATE TABLE IF NOT EXISTS guarantor_claims (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        guarantor_name VARCHAR(255) NOT NULL,
        borrower_name VARCHAR(255) NOT NULL,
        guarantor_contact VARCHAR(50),
        borrower_contact VARCHAR(50),
        amount_paid DECIMAL(15, 2) NOT NULL,
        claim_date DATETIME NOT NULL,
        status VARCHAR(20) NOT NULL,
        claim_description TEXT,
        guarantor_id INTEGER,
        loan_id INTEGER
    )
    ''')
    
    # Execute table creation
    with engine.connect() as connection:
        connection.execute(create_table_sql)
        connection.commit()

def generate_sample_guarantor_claims():
    """Generate and insert sample guarantor claims."""
    try:
        # Create engine directly from config
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        
        # Create the table first
        create_guarantor_claims_table(engine)
        
        # Create a session factory
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Clear existing claims to avoid duplicates
            session.query(GuarantorClaim).delete()
            
            # Generate multiple sample claims
            for _ in range(10):
                # Generate names
                guarantor_first, guarantor_last = generate_kenyan_names()
                borrower_first, borrower_last = generate_kenyan_names()
                
                # Create claim
                claim = GuarantorClaim(
                    guarantor_name=f"{guarantor_first} {guarantor_last}",
                    borrower_name=f"{borrower_first} {borrower_last}",
                    guarantor_contact=generate_kenyan_phone_number(),
                    borrower_contact=generate_kenyan_phone_number(),
                    amount_paid=round(random.uniform(50000, 500000), 2),
                    claim_date=datetime.utcnow(),
                    status=random.choice(['Pending', 'Resolved', 'In Progress']),
                    claim_description=f"Loan guarantee for {borrower_first} {borrower_last}'s business loan",
                    guarantor_id=random.randint(1, 100),
                    loan_id=random.randint(1, 100)
                )
                
                # Add to session
                session.add(claim)
            
            # Commit the transaction
            session.commit()
            print(f"Successfully inserted sample guarantor claims!")
        
        except Exception as e:
            # Rollback in case of error
            session.rollback()
            
            # Detailed error logging
            print(f"Error occurred while inserting sample guarantor claims:")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Details: {str(e)}")
            print("\nFull Traceback:")
            traceback.print_exc()
            
            # Exit with error code
            sys.exit(1)
        
        finally:
            # Close the session
            session.close()
    
    except Exception as e:
        # Catch any errors in setting up the database connection
        print(f"Database connection error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    generate_sample_guarantor_claims()
