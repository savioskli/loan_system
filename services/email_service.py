import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from models.email_config import EmailConfig
from models.email_template import EmailTemplate
from utils.encryption import decrypt_value
from jinja2 import Template
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service for handling email operations using the configured SMTP server.
    """
    
    @staticmethod
    def get_email_config() -> Optional[EmailConfig]:
        """
        Get the active email configuration from the database.
        
        Returns:
            Optional[EmailConfig]: The active email configuration or None if not configured.
        """
        try:
            # Get the first email config (assuming there's only one active config)
            return EmailConfig.query.first()
        except Exception as e:
            logger.error(f"Error getting email configuration: {str(e)}")
            return None
    
    @staticmethod
    def send_email(to: str, subject: str, body: str, template_type: Optional[str] = None, 
                  template_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send an email using the configured SMTP server.
        
        Args:
            to (str): The recipient's email address.
            subject (str): The email subject.
            body (str): The email body (used if template_type is None).
            template_type (Optional[str]): The type of email template to use.
            template_data (Optional[Dict[str, Any]]): Data to render the template with.
            
        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
                {
                    'success': bool,
                    'message': str
                }
        """
        try:
            # Get email configuration
            config = EmailService.get_email_config()
            if not config:
                return {
                    'success': False,
                    'message': 'Email configuration not found'
                }
            
            # If template_type is provided, get the template and render it
            if template_type and template_data:
                template = EmailTemplate.query.filter_by(type=template_type, is_active=True).first()
                if not template:
                    return {
                        'success': False,
                        'message': f'Email template {template_type} not found'
                    }
                
                # Render the template with the provided data
                jinja_template = Template(template.content)
                body = jinja_template.render(**template_data)
                subject = template.subject
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = config.from_email
            msg['To'] = to
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server and send email
            smtp_password = decrypt_value(config.smtp_password) if config.smtp_password else ''
            
            with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(config.smtp_username, smtp_password)
                server.send_message(msg)
            
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                'success': False,
                'message': f"Error sending email: {str(e)}"
            }
    
    @staticmethod
    def send_payment_reminder(to: str, client_name: str, account_no: str, 
                             loan_amount: float, outstanding_balance: float, 
                             due_date: datetime) -> Dict[str, Any]:
        """
        Send a payment reminder email using the payment_reminder template.
        
        Args:
            to (str): The recipient's email address.
            client_name (str): The client's name.
            account_no (str): The loan account number.
            loan_amount (float): The original loan amount.
            outstanding_balance (float): The outstanding balance.
            due_date (datetime): The payment due date.
            
        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        template_data = {
            'client_name': client_name,
            'account_no': account_no,
            'loan_amount': loan_amount,
            'outstanding_balance': outstanding_balance,
            'due_date': due_date.strftime('%Y-%m-%d'),
            'current_date': datetime.utcnow().strftime('%Y-%m-%d')
        }
        
        return EmailService.send_email(
            to=to,
            subject='Payment Reminder',  # Will be overridden by template
            body='',  # Will be overridden by template
            template_type='payment_reminder',
            template_data=template_data
        )
