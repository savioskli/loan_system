from datetime import datetime, timedelta
from models.legal_case import LegalCase
from database import db

def create_sample_legal_cases():
    # Sample case 1
    case1 = LegalCase(
        loan_id=1,
        case_number="CASE-2025-001",
        court_name="High Court of Nairobi",
        case_type="civil",
        filing_date=datetime.now() - timedelta(days=30),
        status="active",
        plaintiff="ABC Bank Ltd",
        defendant="John Doe",
        amount_claimed=50000.00,
        lawyer_name="James Smith",
        lawyer_contact="james.smith@lawfirm.com",
        description="Loan default case for personal loan",
        next_hearing_date=datetime.now() + timedelta(days=15)
    )

    # Sample case 2
    case2 = LegalCase(
        loan_id=2,
        case_number="CASE-2025-002",
        court_name="Commercial Court of Mombasa",
        case_type="civil",
        filing_date=datetime.now() - timedelta(days=45),
        status="pending",
        plaintiff="ABC Bank Ltd",
        defendant="XYZ Company Ltd",
        amount_claimed=150000.00,
        lawyer_name="Sarah Johnson",
        lawyer_contact="sarah.j@lawfirm.com",
        description="Business loan default case",
        next_hearing_date=datetime.now() + timedelta(days=30)
    )

    # Sample case 3
    case3 = LegalCase(
        loan_id=3,
        case_number="CASE-2025-003",
        court_name="High Court of Kisumu",
        case_type="bankruptcy",
        filing_date=datetime.now() - timedelta(days=90),
        status="resolved",
        plaintiff="ABC Bank Ltd",
        defendant="Jane Smith",
        amount_claimed=75000.00,
        lawyer_name="Michael Brown",
        lawyer_contact="m.brown@lawfirm.com",
        description="Bankruptcy proceedings for personal loan default",
        next_hearing_date=None
    )

    db.session.add_all([case1, case2, case3])
    db.session.commit()

if __name__ == '__main__':
    create_sample_legal_cases()
