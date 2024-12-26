from extensions import db
from models.email_template import EmailTemplate, EmailTemplateType
import logging

logger = logging.getLogger(__name__)

def create_email_templates_table():
    try:
        # Create the table
        db.create_all()
        logger.info("Email templates table created successfully")

        # Create default templates
        default_templates = [
            {
                'type': EmailTemplateType.LOAN_APPROVED.value,
                'subject': 'Your Loan Application Has Been Approved',
                'content': '''Dear {{customer_name}},

We are pleased to inform you that your loan application for {{loan_amount}} has been approved.

Best regards,
The Loan Team'''
            },
            {
                'type': EmailTemplateType.LOAN_REJECTED.value,
                'subject': 'Loan Application Status Update',
                'content': '''Dear {{customer_name}},

We regret to inform you that your loan application has been declined at this time.

Best regards,
The Loan Team'''
            },
            {
                'type': EmailTemplateType.PAYMENT_REMINDER.value,
                'subject': 'Payment Reminder',
                'content': '''Dear {{customer_name}},

This is a reminder that your loan payment of {{payment_amount}} is due on {{due_date}}.

Best regards,
The Loan Team'''
            },
            {
                'type': EmailTemplateType.PAYMENT_RECEIVED.value,
                'subject': 'Payment Received',
                'content': '''Dear {{customer_name}},

We have received your payment of {{payment_amount}}. Thank you for your prompt payment.

Best regards,
The Loan Team'''
            },
            {
                'type': EmailTemplateType.PAYMENT_OVERDUE.value,
                'subject': 'Payment Overdue Notice',
                'content': '''Dear {{customer_name}},

Your loan payment of {{payment_amount}} was due on {{due_date}} and is now overdue.

Best regards,
The Loan Team'''
            },
            {
                'type': EmailTemplateType.LOAN_DISBURSED.value,
                'subject': 'Loan Disbursement Notification',
                'content': '''Dear {{customer_name}},

Your loan amount of {{loan_amount}} has been disbursed to your account.

Best regards,
The Loan Team'''
            }
        ]

        # Insert default templates
        for template_data in default_templates:
            template = EmailTemplate(
                type=template_data['type'],
                subject=template_data['subject'],
                content=template_data['content']
            )
            db.session.add(template)

        db.session.commit()
        logger.info("Default email templates created successfully")
        return True

    except Exception as e:
        logger.error(f"Error creating email templates: {str(e)}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    create_email_templates_table()
