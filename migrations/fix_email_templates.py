import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.email_template import EmailTemplate, EmailTemplateType

# Sample templates
sample_templates = [
    {
        'type': EmailTemplateType.LOAN_APPROVED.value,
        'subject': 'Your Loan Application Has Been Approved',
        'content': '''Dear {customer_name},

We are pleased to inform you that your loan application for {loan_amount} has been approved.

Best regards,
The Loan Team''',
        'days_trigger': None
    },
    {
        'type': EmailTemplateType.LOAN_REJECTED.value,
        'subject': 'Loan Application Status Update',
        'content': '''Dear {customer_name},

We regret to inform you that your loan application has been declined at this time.

Best regards,
The Loan Team''',
        'days_trigger': None
    },
    {
        'type': EmailTemplateType.PAYMENT_REMINDER.value,
        'subject': 'Payment Reminder',
        'content': '''Dear {customer_name},

This is a reminder that your loan payment of {payment_amount} is due on {due_date}.

Best regards,
The Loan Team''',
        'days_trigger': 3
    },
    {
        'type': EmailTemplateType.PAYMENT_RECEIVED.value,
        'subject': 'Payment Received',
        'content': '''Dear {customer_name},

We have received your payment of {payment_amount}. Thank you for your prompt payment.

Best regards,
The Loan Team''',
        'days_trigger': None
    },
    {
        'type': EmailTemplateType.PAYMENT_OVERDUE.value,
        'subject': 'Payment Overdue Notice',
        'content': '''Dear {customer_name},

Your loan payment of {payment_amount} was due on {due_date} and is now overdue.

Best regards,
The Loan Team''',
        'days_trigger': 1
    },
    {
        'type': EmailTemplateType.LOAN_DISBURSED.value,
        'subject': 'Loan Disbursement Notification',
        'content': '''Dear {customer_name},

Your loan amount of {loan_amount} has been disbursed to your account.

Best regards,
The Loan Team''',
        'days_trigger': None
    }
]

def fix_email_templates():
    try:
        app = create_app()
        with app.app_context():
            # Drop and recreate the table
            print("Dropping existing email_templates table...")
            EmailTemplate.__table__.drop(db.engine, checkfirst=True)
            
            print("Creating email_templates table with correct structure...")
            EmailTemplate.__table__.create(db.engine)

            # Insert sample templates
            print("Inserting sample templates...")
            for template_data in sample_templates:
                template = EmailTemplate(
                    type=template_data['type'],
                    subject=template_data['subject'],
                    content=template_data['content'],
                    days_trigger=template_data['days_trigger']
                )
                db.session.add(template)

            # Commit the changes
            db.session.commit()
            print("Email templates table fixed successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    fix_email_templates()
