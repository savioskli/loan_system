import logging
from typing import Optional, Dict, Any
from models.correspondence import Correspondence
from models.sms_gateway import SmsGatewayConfig
from services.sms_gateway_factory import SmsGatewayFactory
from extensions import db
from datetime import datetime

logger = logging.getLogger(__name__)

class CorrespondenceService:
    """
    Service for handling correspondence operations including sending SMS messages
    using the configured SMS gateway.
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
