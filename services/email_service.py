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
            print(f"[INFO] Fetching email configuration from database")
            config = EmailConfig.query.first()
            if not config:
                print(f"[WARNING] No email configuration found in the database")
                logger.warning("No email configuration found in the database")
                return None
            print(f"[INFO] Email configuration found: {config.smtp_server}:{config.smtp_port}")
            return config
        except Exception as e:
            print(f"[ERROR] Error getting email configuration: {str(e)}")
            logger.error(f"Error getting email configuration: {str(e)}", exc_info=True)
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
            # Validate input parameters
            print(f"[INFO] Validating email parameters: to={to}, subject='{subject}', template_type={template_type}")
            if not to or '@' not in to:
                error_msg = f"Invalid recipient email address: {to}"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
                
            if not subject:
                error_msg = "Email subject cannot be empty"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
            
            # Get email configuration
            config = EmailService.get_email_config()
            if not config:
                error_msg = "Email configuration not found"
                print(f"[ERROR] {error_msg}")
                return {
                    'success': False,
                    'message': error_msg
                }
            
            # If template_type is provided, get the template and render it
            if template_type and template_data:
                try:
                    print(f"[INFO] Looking for email template: {template_type}")
                    template = EmailTemplate.query.filter_by(type=template_type).first()
                    if not template:
                        error_msg = f"Email template {template_type} not found"
                        print(f"[ERROR] {error_msg}")
                        logger.error(error_msg)
                        return {
                            'success': False,
                            'message': error_msg
                        }
                    print(f"[INFO] Found template: {template_type}, subject: '{template.subject}'")
                    
                    # Render the template with the provided data
                    print(f"[INFO] Rendering template with data: {template_data}")
                    jinja_template = Template(template.content)
                    body = jinja_template.render(**template_data)
                    subject = template.subject
                    print(f"[INFO] Template rendered successfully")
                except Exception as template_error:
                    error_msg = f"Error rendering email template: {str(template_error)}"
                    print(f"[ERROR] {error_msg}")
                    logger.error(error_msg, exc_info=True)
                    return {
                        'success': False,
                        'message': error_msg
                    }
            else:
                print(f"[INFO] Using direct body content (no template)")
                if not body:
                    error_msg = "Email body cannot be empty when no template is used"
                    print(f"[ERROR] {error_msg}")
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'message': error_msg
                    }
            
            # Create email message
            print(f"[INFO] Creating email message")
            msg = MIMEMultipart()
            msg['From'] = config.from_email
            msg['To'] = to
            msg['Subject'] = subject
            print(f"[INFO] Email headers set: From={config.from_email}, To={to}, Subject='{subject}'")
            
            # Attach body
            msg.attach(MIMEText(body, 'html'))
            print(f"[INFO] HTML body attached to email")
            
            # Connect to SMTP server and send email
            print(f"[INFO] Using SMTP password directly without decryption")
            
            # Check if SMTP password exists
            if not config.smtp_password:
                error_msg = "SMTP password is not configured"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': 'Email service not properly configured: SMTP password is missing'
                }
                
            # Use the password directly without decryption
            smtp_password = config.smtp_password

            try:
                print(f"[INFO] Connecting to SMTP server: {config.smtp_server}:{config.smtp_port}")
                logger.info(f"Connecting to SMTP server: {config.smtp_server}:{config.smtp_port}")
                
                # Create SMTP connection with timeout
                try:
                    # Check if we should use SSL (port 465) or TLS (usually port 587)
                    if config.smtp_port == 465:
                        print(f"[INFO] Using SMTP_SSL for port 465")
                        server = smtplib.SMTP_SSL(config.smtp_server, config.smtp_port, timeout=10)
                        print(f"[INFO] SMTP_SSL connection established")
                    else:
                        print(f"[INFO] Using standard SMTP with STARTTLS")
                        server = smtplib.SMTP(config.smtp_server, config.smtp_port, timeout=10)
                        print(f"[INFO] SMTP connection established")
                except (smtplib.SMTPConnectError, ConnectionRefusedError) as conn_err:
                    error_msg = f"Failed to connect to SMTP server: {str(conn_err)}"
                    print(f"[ERROR] {error_msg}")
                    logger.error(error_msg, exc_info=True)
                    return {
                        'success': False,
                        'message': error_msg
                    }
                except Exception as e:
                    error_msg = f"Unexpected error connecting to SMTP server: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    logger.error(error_msg, exc_info=True)
                    return {
                        'success': False,
                        'message': error_msg
                    }
                
                # Start TLS (only if not using SSL)
                if config.smtp_port != 465:
                    try:
                        print(f"[INFO] Starting TLS")
                        server.starttls()  # Secure the connection
                        print(f"[INFO] TLS started successfully")
                    except Exception as tls_error:
                        error_msg = f"TLS error: {str(tls_error)}"
                        print(f"[ERROR] {error_msg}")
                        logger.error(error_msg, exc_info=True)
                        server.quit()  # Close the connection if TLS fails
                        return {
                            'success': False,
                            'message': error_msg
                        }
                else:
                    print(f"[INFO] Using SSL connection, skipping TLS")
                
                # Login
                try:
                    print(f"[INFO] Logging in with username: {config.smtp_username}")
                    logger.info(f"Logging in with username: {config.smtp_username}")
                    server.login(config.smtp_username, smtp_password)
                    print(f"[INFO] Login successful")
                except smtplib.SMTPAuthenticationError as auth_error:
                    error_msg = f"SMTP authentication failed: {str(auth_error)}"
                    print(f"[ERROR] {error_msg}")
                    logger.error(error_msg)
                    server.quit()
                    return {
                        'success': False,
                        'message': 'SMTP authentication failed: Invalid username or password'
                    }
                
                # Send email
                try:
                    print(f"[INFO] Sending email to: {to}")
                    logger.info(f"Sending email to: {to}")
                    server.send_message(msg)
                    print(f"[INFO] Email sent successfully")
                    logger.info("Email sent successfully")
                    server.quit()
                    return {
                        'success': True,
                        'message': 'Email sent successfully'
                    }
                except smtplib.SMTPRecipientsRefused as recip_error:
                    error_msg = f"Recipients refused: {str(recip_error)}"
                    print(f"[ERROR] {error_msg}")
                    logger.error(error_msg)
                    server.quit()
                    return {
                        'success': False,
                        'message': error_msg
                    }
                except smtplib.SMTPException as smtp_error:
                    error_msg = f"SMTP error while sending: {str(smtp_error)}"
                    print(f"[ERROR] {error_msg}")
                    logger.error(error_msg)
                    server.quit()
                    return {
                        'success': False,
                        'message': error_msg
                    }
                except Exception as send_error:
                    error_msg = f"Unexpected error while sending email: {str(send_error)}"
                    print(f"[ERROR] {error_msg}")
                    logger.error(error_msg, exc_info=True)
                    server.quit()
                    return {
                        'success': False,
                        'message': error_msg
                    }
            except smtplib.SMTPException as smtp_error:
                error_msg = f"SMTP error: {str(smtp_error)}"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
            except Exception as conn_error:
                error_msg = f"Connection error: {str(conn_error)}"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg, exc_info=True)
                return {
                    'success': False,
                    'message': error_msg
                }
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}", exc_info=True)
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
        try:
            # Validate input parameters
            print(f"[INFO] Validating payment reminder parameters")
            if not to or '@' not in to:
                error_msg = f"Invalid recipient email address: {to}"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
                
            # Check if client_name is valid
            if not client_name:
                error_msg = "Client name cannot be empty"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
                
            # Check if account_no is valid
            if not account_no:
                error_msg = "Account number cannot be empty"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
            
            # Format currency values for display
            try:
                formatted_loan_amount = '{:,.2f}'.format(loan_amount)
                print(f"[INFO] Formatted loan amount: {formatted_loan_amount}")
            except (ValueError, TypeError) as e:
                error_msg = f"Invalid loan amount: {loan_amount}. Error: {str(e)}"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
                
            try:
                # As per system requirements, we use OutstandingBalance when InstallmentAmount is not available
                formatted_outstanding_balance = '{:,.2f}'.format(outstanding_balance)
                print(f"[INFO] Formatted outstanding balance: {formatted_outstanding_balance}")
            except (ValueError, TypeError) as e:
                error_msg = f"Invalid outstanding balance: {outstanding_balance}. Error: {str(e)}"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
                
            try:
                formatted_due_date = due_date.strftime('%d %B, %Y')
                print(f"[INFO] Formatted due date: {formatted_due_date}")
            except (ValueError, TypeError, AttributeError) as e:
                error_msg = f"Invalid due date: {due_date}. Error: {str(e)}"
                print(f"[ERROR] {error_msg}")
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg
                }
            
            logger.info(f"Sending payment reminder email to {to} for account {account_no}")
            print(f"[INFO] Sending payment reminder email to {to} for account {account_no}")
            
            # Create HTML email body directly
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Payment Reminder</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #0056b3; color: white; padding: 10px 20px; text-align: center; }}
                    .content {{ padding: 20px; border: 1px solid #ddd; }}
                    .amount {{ font-weight: bold; color: #0056b3; }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Payment Reminder</h2>
                    </div>
                    <div class="content">
                        <p>Dear {client_name},</p>
                        
                        <p>This is a friendly reminder that your loan payment of <span class="amount">KES {formatted_outstanding_balance}</span> is due on {formatted_due_date}.</p>
                        
                        <p>Loan Details:</p>
                        <ul>
                            <li>Account Number: {account_no}</li>
                            <li>Original Loan Amount: KES {formatted_loan_amount}</li>
                            <li>Outstanding Balance: KES {formatted_outstanding_balance}</li>
                            <li>Due Date: {formatted_due_date}</li>
                        </ul>
                        
                        <p>Please ensure that your payment is made on or before the due date to avoid any late payment penalties.</p>
                        
                        <p>If you have already made this payment, please disregard this reminder.</p>
                        
                        <p>Thank you for your prompt attention to this matter.</p>
                        
                        <p>Best regards,<br>
                        Loan Management Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            print(f"[INFO] HTML email body created successfully")
            
            # Send the email with the direct HTML content
            print(f"[INFO] Calling send_email method")
            return EmailService.send_email(
                to=to,
                subject=f'Payment Reminder for Loan {account_no}',
                body=html_body,
                template_type=None,  # Don't use a template
                template_data=None   # Don't use template data
            )
        except Exception as e:
            error_msg = f"Error in send_payment_reminder: {str(e)}"
            print(f"[ERROR] {error_msg}")
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'message': error_msg
            }

    @staticmethod
    def batch_send_payment_reminders(reminder_data: list) -> Dict[str, Any]:
        """
        Send payment reminder emails to multiple recipients in a single SMTP session.
        
        Args:
            reminder_data (list): A list of dictionaries containing recipient data with the following structure:
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
        
        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation with details for each recipient.
        """
        results = {
            'success': True,
            'total': len(reminder_data),
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        if not reminder_data:
            return {
                'success': False,
                'message': 'No recipients provided',
                'total': 0,
                'sent': 0,
                'failed': 0,
                'details': []
            }
        
        # Get email configuration
        config = EmailService.get_email_config()
        if not config:
            error_msg = 'Email configuration not found'
            print(f'[ERROR] {error_msg}')
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'total': len(reminder_data),
                'sent': 0,
                'failed': len(reminder_data),
                'details': [{'to': item.get('to', 'unknown'), 'success': False, 'message': error_msg} for item in reminder_data]
            }
        
        # Prepare SMTP connection
        try:
            print(f'[INFO] Connecting to SMTP server: {config.smtp_server}:{config.smtp_port}')
            logger.info(f'Connecting to SMTP server: {config.smtp_server}:{config.smtp_port}')
            
            # Decrypt SMTP password
            smtp_password = config.smtp_password if config.smtp_password else ''
            if not smtp_password:
                error_msg = 'SMTP password is empty or could not be decrypted'
                print(f'[ERROR] {error_msg}')
                logger.error(error_msg)
                return {
                    'success': False,
                    'message': error_msg,
                    'total': len(reminder_data),
                    'sent': 0,
                    'failed': len(reminder_data),
                    'details': [{'to': item.get('to', 'unknown'), 'success': False, 'message': error_msg} for item in reminder_data]
                }
            
            # Create SMTP connection
            if config.smtp_port == 465:
                print(f'[INFO] Using SMTP_SSL for port 465')
                server = smtplib.SMTP_SSL(config.smtp_server, config.smtp_port, timeout=30)
                server.ehlo()  # Identify to the server
                # No need for starttls with SSL
            else:
                print(f'[INFO] Using standard SMTP with STARTTLS')
                server = smtplib.SMTP(config.smtp_server, config.smtp_port, timeout=30)
                server.ehlo()  # Identify to the server
                server.starttls()  # Secure the connection
                server.ehlo()  # Re-identify as an encrypted connection
            
            server.login(config.smtp_username, smtp_password)
            print(f'[INFO] SMTP connection established and authenticated successfully')
            
            # Process each recipient
            for item in reminder_data:
                try:
                    to = item.get('to')
                    client_name = item.get('client_name')
                    account_no = item.get('account_no')
                    loan_amount = item.get('loan_amount')
                    outstanding_balance = item.get('outstanding_balance')  # As per system requirements
                    due_date = item.get('due_date')
                    
                    # Validate required fields
                    if not all([to, client_name, account_no, loan_amount, outstanding_balance, due_date]):
                        missing = [k for k, v in {'to': to, 'client_name': client_name, 'account_no': account_no, 
                                              'loan_amount': loan_amount, 'outstanding_balance': outstanding_balance, 
                                              'due_date': due_date}.items() if not v]
                        error_msg = f'Missing required fields: {missing}'
                        print(f'[ERROR] {error_msg} for recipient {to}')
                        results['details'].append({
                            'to': to or 'unknown',
                            'success': False,
                            'message': error_msg
                        })
                        results['failed'] += 1
                        continue
                    
                    # Validate email format
                    if '@' not in to:
                        error_msg = f'Invalid email format: {to}'
                        print(f'[ERROR] {error_msg}')
                        results['details'].append({
                            'to': to,
                            'success': False,
                            'message': error_msg
                        })
                        results['failed'] += 1
                        continue
                    
                    # Format values for display
                    try:
                        formatted_loan_amount = '{:,.2f}'.format(float(loan_amount))
                        formatted_outstanding_balance = '{:,.2f}'.format(float(outstanding_balance))
                        formatted_due_date = due_date.strftime('%d %B, %Y') if isinstance(due_date, datetime) else str(due_date)
                    except (ValueError, TypeError, AttributeError) as e:
                        error_msg = f'Error formatting values: {str(e)}'
                        print(f'[ERROR] {error_msg} for recipient {to}')
                        results['details'].append({
                            'to': to,
                            'success': False,
                            'message': error_msg
                        })
                        results['failed'] += 1
                        continue
                    
                    # Create email message
                    msg = MIMEMultipart()
                    msg['From'] = config.from_email
                    msg['To'] = to
                    msg['Subject'] = f'Payment Reminder for Loan {account_no}'
                    
                    # Create HTML email body
                    html_body = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Payment Reminder</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                            .header {{ background-color: #0056b3; color: white; padding: 10px 20px; text-align: center; }}
                            .content {{ padding: 20px; border: 1px solid #ddd; }}
                            .amount {{ font-weight: bold; color: #0056b3; }}
                            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h2>Payment Reminder</h2>
                            </div>
                            <div class="content">
                                <p>Dear {client_name},</p>
                                
                                <p>This is a friendly reminder that your loan payment of <span class="amount">KES {formatted_outstanding_balance}</span> is due on {formatted_due_date}.</p>
                                
                                <p>Loan Details:</p>
                                <ul>
                                    <li>Account Number: {account_no}</li>
                                    <li>Original Loan Amount: KES {formatted_loan_amount}</li>
                                    <li>Outstanding Balance: KES {formatted_outstanding_balance}</li>
                                    <li>Due Date: {formatted_due_date}</li>
                                </ul>
                                
                                <p>Please ensure that your payment is made on or before the due date to avoid any late payment penalties.</p>
                                
                                <p>If you have already made this payment, please disregard this reminder.</p>
                                
                                <p>Thank you for your prompt attention to this matter.</p>
                                
                                <p>Best regards,<br>
                                Loan Management Team</p>
                            </div>
                            <div class="footer">
                                <p>This is an automated message. Please do not reply to this email.</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Attach HTML body
                    msg.attach(MIMEText(html_body, 'html'))
                    
                    # Send the email
                    print(f'[INFO] Sending email to: {to}')
                    server.send_message(msg)
                    print(f'[INFO] Email sent successfully to {to}')
                    
                    # Record success
                    results['details'].append({
                        'to': to,
                        'success': True,
                        'message': 'Email sent successfully'
                    })
                    results['sent'] += 1
                    
                except Exception as e:
                    error_msg = f'Error sending to {item.get("to", "unknown")}: {str(e)}'
                    print(f'[ERROR] {error_msg}')
                    logger.error(error_msg, exc_info=True)
                    results['details'].append({
                        'to': item.get('to', 'unknown'),
                        'success': False,
                        'message': error_msg
                    })
                    results['failed'] += 1
            
            # Close the connection
            server.quit()
            print(f'[INFO] SMTP connection closed. Sent: {results["sent"]}, Failed: {results["failed"]}')
            
            # Update overall success flag
            if results['failed'] > 0:
                if results['sent'] == 0:
                    results['success'] = False
                    results['message'] = 'All emails failed to send'
                else:
                    results['message'] = f'Partially successful: {results["sent"]} sent, {results["failed"]} failed'
            else:
                results['message'] = 'All emails sent successfully'
            
            return results
            
        except smtplib.SMTPAuthenticationError as auth_error:
            error_msg = f'SMTP authentication failed: {str(auth_error)}'
            print(f'[ERROR] {error_msg}')
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'total': len(reminder_data),
                'sent': 0,
                'failed': len(reminder_data),
                'details': [{'to': item.get('to', 'unknown'), 'success': False, 'message': error_msg} for item in reminder_data]
            }
        except Exception as e:
            error_msg = f'Error in batch email sending: {str(e)}'
            print(f'[ERROR] {error_msg}')
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'message': error_msg,
                'total': len(reminder_data),
                'sent': 0,
                'failed': len(reminder_data),
                'details': [{'to': item.get('to', 'unknown'), 'success': False, 'message': error_msg} for item in reminder_data]
            }
