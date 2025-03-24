from extensions import db
from models.email_template import EmailTemplate, EmailTemplateType
import logging

logger = logging.getLogger(__name__)

def update_payment_reminder_template():
    try:
        # Update the payment reminder template
        payment_reminder = EmailTemplate.query.filter_by(type=EmailTemplateType.PAYMENT_REMINDER.value).first()
        
        if payment_reminder:
            payment_reminder.subject = 'Payment Reminder for Your Loan'
            payment_reminder.content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Reminder</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #3B82F6; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; border: 1px solid #ddd; border-top: none; }
        .footer { font-size: 12px; text-align: center; margin-top: 20px; color: #666; }
        .important { color: #DC2626; font-weight: bold; }
        .amount { font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Payment Reminder</h2>
    </div>
    <div class="content">
        <p>Dear {{client_name}},</p>
        
        <p>This is a friendly reminder that your loan payment is due soon.</p>
        
        <p><strong>Account Number:</strong> {{account_no}}</p>
        <p><strong>Outstanding Balance:</strong> <span class="amount">KES {{outstanding_balance}}</span></p>
        <p><strong>Due Date:</strong> {{due_date}}</p>
        
        <p>Please ensure that your account has sufficient funds for the payment to be processed on the due date.</p>
        
        <p>If you have already made this payment, please disregard this reminder.</p>
        
        <p>If you have any questions or need assistance, please don't hesitate to contact our customer service team.</p>
        
        <p>Thank you for your prompt attention to this matter.</p>
        
        <p>Best regards,<br>
        The Loan Team</p>
    </div>
    <div class="footer">
        <p>This is an automated email. Please do not reply to this message.</p>
        <p>© 2025 Loan System. All rights reserved.</p>
    </div>
</body>
</html>
'''
            db.session.commit()
            logger.info("Payment reminder template updated successfully")
            return True
        else:
            logger.error("Payment reminder template not found")
            return False

    except Exception as e:
        logger.error(f"Error updating payment reminder template: {str(e)}")
        db.session.rollback()
        return False

def update_payment_overdue_template():
    try:
        # Update the payment overdue template
        payment_overdue = EmailTemplate.query.filter_by(type=EmailTemplateType.PAYMENT_OVERDUE.value).first()
        
        if payment_overdue:
            payment_overdue.subject = 'URGENT: Payment Overdue Notice'
            payment_overdue.content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Overdue Notice</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #DC2626; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; border: 1px solid #ddd; border-top: none; }
        .footer { font-size: 12px; text-align: center; margin-top: 20px; color: #666; }
        .important { color: #DC2626; font-weight: bold; }
        .amount { font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h2>URGENT: Payment Overdue</h2>
    </div>
    <div class="content">
        <p>Dear {{client_name}},</p>
        
        <p class="important">Your loan payment is now overdue.</p>
        
        <p><strong>Account Number:</strong> {{account_no}}</p>
        <p><strong>Outstanding Balance:</strong> <span class="amount">KES {{outstanding_balance}}</span></p>
        <p><strong>Due Date:</strong> {{due_date}}</p>
        <p><strong>Current Date:</strong> {{current_date}}</p>
        
        <p>Please make your payment as soon as possible to avoid additional late fees and potential impact on your credit score.</p>
        
        <p>If you have already made this payment, please disregard this notice.</p>
        
        <p>If you are experiencing financial difficulties, please contact our customer service team immediately to discuss possible payment arrangements.</p>
        
        <p>Thank you for your immediate attention to this matter.</p>
        
        <p>Best regards,<br>
        The Loan Team</p>
    </div>
    <div class="footer">
        <p>This is an automated email. Please do not reply to this message.</p>
        <p>© 2025 Loan System. All rights reserved.</p>
    </div>
</body>
</html>
'''
            db.session.commit()
            logger.info("Payment overdue template updated successfully")
            return True
        else:
            logger.error("Payment overdue template not found")
            return False

    except Exception as e:
        logger.error(f"Error updating payment overdue template: {str(e)}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    update_payment_reminder_template()
    update_payment_overdue_template()
