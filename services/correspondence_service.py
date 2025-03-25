import logging
from typing import Optional, Dict, Any
from models.correspondence import Correspondence
from models.sms_gateway import SmsGatewayConfig
from models.email_config import EmailConfig
from models.email_template import EmailTemplateType
from services.sms_gateway_factory import SmsGatewayFactory
from services.email_service import EmailService
from extensions import db
from datetime import datetime

logger = logging.getLogger(__name__)

class CorrespondenceService:
    """
    Service for handling correspondence operations including sending SMS messages
    and emails using the configured gateways.
    """
    
    @staticmethod
    def send_sms(to: str, message: str, account_no: str, client_name: str, 
                staff_id: int, sent_by: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an SMS message using the configured SMS gateway and record it in the correspondence table.
        
        Args:
            to (str): The recipient's phone number.
            message (str): The SMS message content.
            account_no (str): The account number associated with the correspondence.
            client_name (str): The client name associated with the correspondence.
            staff_id (int): The ID of the staff member sending the message.
            sent_by (str): The name of the user sending the message.
            provider (Optional[str]): Not used, kept for backward compatibility.
            
        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
                {
                    'success': bool,
                    'message': str,
                    'correspondence_id': Optional[int]
                }
        """
        try:
            # Create the SMS gateway using the factory
            # We use the single configured provider from the database
            sms_gateway = SmsGatewayFactory.create_gateway()
            
            # Send the SMS
            success = sms_gateway.send_sms(to=to, message=message)
            
            # Create correspondence record
            correspondence = Correspondence(
                account_no=account_no,
                client_name=client_name,
                type='sms',
                message=message,
                status='sent' if success else 'failed',
                sent_by=sent_by,
                recipient=to,
                delivery_status='delivered' if success else 'failed',
                delivery_time=datetime.utcnow() if success else None,
                staff_id=staff_id
            )
            
            db.session.add(correspondence)
            db.session.commit()
            
            return {
                'success': success,
                'message': 'SMS sent successfully' if success else 'Failed to send SMS',
                'correspondence_id': correspondence.id
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return {
                'success': False,
                'message': f"Error sending SMS: {str(e)}",
                'correspondence_id': None
            }
    
    @staticmethod
    def get_active_sms_provider() -> str:
        """
        Get the name of the active SMS provider from configuration.
        
        Returns:
            str: The name of the active SMS provider.
        """
        config = SmsGatewayConfig.get_active_config()
        if not config:
            return "No provider configured"
        return config.sms_provider
    
    @staticmethod
    def get_available_sms_providers() -> list:
        """
        Get a list of all available SMS providers.
        
        Returns:
            list: A list of available SMS provider names.
        """
        return SmsGatewayFactory.get_available_providers()
    
    @staticmethod
    def send_email(to: str, subject: str, message: str, account_no: str, client_name: str,
                 staff_id: int, sent_by: str, template_type: Optional[str] = None,
                 template_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send an email using the configured email service and record it in the correspondence table.
        
        Args:
            to (str): The recipient's email address.
            subject (str): The email subject.
            message (str): The email message content (used if template_type is None).
            account_no (str): The account number associated with the correspondence.
            client_name (str): The client name associated with the correspondence.
            staff_id (int): The ID of the staff member sending the message.
            sent_by (str): The name of the user sending the message.
            template_type (Optional[str]): The type of email template to use.
            template_data (Optional[Dict[str, Any]]): Data to render the template with.
            
        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
                {
                    'success': bool,
                    'message': str,
                    'correspondence_id': Optional[int]
                }
        """
        try:
            # Send the email using the email service
            result = EmailService.send_email(
                to=to,
                subject=subject,
                body=message,
                template_type=template_type,
                template_data=template_data
            )
            
            success = result['success']
            
            # Create correspondence record
            correspondence = Correspondence(
                account_no=account_no,
                client_name=client_name,
                type='email',
                message=message,
                status='sent' if success else 'failed',
                sent_by=sent_by,
                recipient=to,
                delivery_status='delivered' if success else 'failed',
                delivery_time=datetime.utcnow() if success else None,
                staff_id=staff_id
            )
            
            db.session.add(correspondence)
            db.session.commit()
            
            return {
                'success': success,
                'message': 'Email sent successfully' if success else f'Failed to send email: {result["message"]}',
                'correspondence_id': correspondence.id
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                'success': False,
                'message': f"Error sending email: {str(e)}",
                'correspondence_id': None
            }
    
    @staticmethod
    def send_payment_reminder_email(to: str, client_name: str, account_no: str,
                                  loan_amount: float, outstanding_balance: float,
                                  due_date: datetime, staff_id: int, sent_by: str) -> Dict[str, Any]:
        """
        Send a payment reminder email using the payment_reminder template.
        
        Args:
            to (str): The recipient's email address.
            client_name (str): The client's name.
            account_no (str): The loan account number.
            loan_amount (float): The original loan amount.
            outstanding_balance (float): The outstanding balance.
            due_date (datetime): The payment due date.
            staff_id (int): The ID of the staff member sending the reminder.
            sent_by (str): The name of the user sending the reminder.
            
        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        logger.info(f"Sending payment reminder email to {to} for account {account_no}")
        
        # First, use EmailService to send the actual email
        # Note: We use outstanding_balance as per system requirements when InstallmentAmount is not available
        email_result = EmailService.send_payment_reminder(
            to=to,
            client_name=client_name,
            account_no=account_no,
            loan_amount=loan_amount,
            outstanding_balance=outstanding_balance,  # Using outstanding balance for payment amount
            due_date=due_date
        )
        
        if not email_result['success']:
            logger.error(f"Failed to send payment reminder email: {email_result['message']}")
            return email_result
        
        # Then, record the correspondence in the database
        try:
            correspondence = Correspondence(
                type='email',
                to=to,
                subject='Payment Reminder',
                message='Payment reminder email sent',
                account_no=account_no,
                client_name=client_name,
                staff_id=staff_id,
                sent_by=sent_by,
                sent_at=datetime.utcnow()
            )
            
            db.session.add(correspondence)
            db.session.commit()
            
            logger.info(f"Correspondence record created with ID: {correspondence.id}")
            
            return {
                'success': True,
                'message': 'Email sent and correspondence recorded',
                'correspondence_id': correspondence.id
            }
            
        except Exception as e:
            logger.error(f"Error recording correspondence: {str(e)}", exc_info=True)
            db.session.rollback()
            
            # Even if we failed to record the correspondence, the email was sent
            return {
                'success': True,
                'message': 'Email sent but failed to record correspondence',
                'error': str(e)
            }
    
    @staticmethod
    def batch_send_payment_reminder_emails(reminders: list, staff_id: int, sent_by: str) -> Dict[str, Any]:
        """
        Send payment reminder emails to multiple recipients in a single batch operation.
        This is more efficient than sending emails one by one as it reuses a single SMTP connection.
        
        Args:
            reminders (list): A list of dictionaries containing recipient data with the following structure:
                [
                    {
                        'to': str,                  # Recipient email address
                        'client_name': str,         # Client name
                        'account_no': str,          # Loan account number
                        'loan_amount': float,       # Original loan amount
                        'outstanding_balance': float, # Outstanding balance (used as payment amount)
                        'due_date': datetime       # Payment due date
                    },
                    ...
                ]
            staff_id (int): The ID of the staff member sending the reminders.
            sent_by (str): The name of the user sending the reminders.
            
        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation with details for each recipient.
        """
        logger.info(f"Sending batch payment reminder emails to {len(reminders)} recipients")
        
        # First, use EmailService to send the actual emails in batch
        email_result = EmailService.batch_send_payment_reminders(reminders)
        
        # Now record correspondences for successful emails
        correspondence_results = []
        
        if email_result['sent'] > 0:
            try:
                # Get successful email details
                successful_emails = [detail for detail in email_result['details'] if detail['success']]
                
                # Create correspondence records for each successful email
                correspondences = []
                for detail in successful_emails:
                    # Find the original reminder data for this recipient
                    recipient_email = detail['to']
                    reminder_data = next((r for r in reminders if r.get('to') == recipient_email), None)
                    
                    if reminder_data:
                        correspondence = Correspondence(
                            type='email',
                            to=recipient_email,
                            subject='Payment Reminder',
                            message='Payment reminder email sent',
                            account_no=reminder_data.get('account_no', ''),
                            client_name=reminder_data.get('client_name', ''),
                            staff_id=staff_id,
                            sent_by=sent_by,
                            sent_at=datetime.utcnow()
                        )
                        correspondences.append(correspondence)
                
                # Bulk insert all correspondence records
                if correspondences:
                    db.session.add_all(correspondences)
                    db.session.commit()
                    
                    # Add correspondence IDs to the results
                    for i, corr in enumerate(correspondences):
                        correspondence_results.append({
                            'to': corr.to,
                            'correspondence_id': corr.id,
                            'success': True
                        })
                    
                    logger.info(f"Created {len(correspondences)} correspondence records")
            except Exception as e:
                logger.error(f"Error recording correspondences: {str(e)}", exc_info=True)
                db.session.rollback()
                
                # Add error info to the result
                email_result['correspondence_error'] = str(e)
        
        # Add correspondence results to the email results
        email_result['correspondences'] = correspondence_results
        
        return email_result
    
    @staticmethod
    def is_email_configured() -> bool:
        """
        Check if email is configured in the system.
        
        Returns:
            bool: True if email is configured, False otherwise.
        """
        config = EmailConfig.query.first()
        return config is not None
