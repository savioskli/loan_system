import logging
from typing import Optional
from services.sms_gateway_interface import SmsGatewayInterface
from services.twillo_sms_service import TwilioSmsService

logger = logging.getLogger(__name__)

class TwilioSmsAdapter(SmsGatewayInterface):
    """
    Adapter for the TwilioSmsService to conform to the SmsGatewayInterface.
    """
    
    def __init__(self, api_key: Optional[str] = None, sender_id: Optional[str] = None):
        """
        Initialize the TwilioSmsAdapter.
        
        Args:
            api_key (Optional[str]): The API key (auth token) for Twilio.
            sender_id (Optional[str]): The sender ID (phone number) for Twilio.
        """
        try:
            # Get configuration from database if not provided
            if not api_key or not sender_id:
                from models.sms_gateway import SmsGatewayConfig
                config = SmsGatewayConfig.get_config_by_provider('twilio')
                if config:
                    api_key = api_key or config.sms_api_key
                    sender_id = sender_id or config.sms_sender_id
            
            # Initialize the service with the provided or retrieved config
            self.service = TwilioSmsService(auth_token=api_key, from_number=sender_id)
        except ValueError as e:
            logger.error(f"Twilio configuration error: {str(e)}")
            raise ValueError(f"Twilio configuration error: {str(e)}")
    
    def send_sms(self, to: str, message: str, sender_id: Optional[str] = None) -> bool:
        """
        Send an SMS message using Twilio.
        
        Args:
            to (str): The recipient's phone number.
            message (str): The SMS message content.
            sender_id (Optional[str]): Not used as Twilio uses the configured sender ID.
            
        Returns:
            bool: True if the SMS was sent successfully, False otherwise.
        """
        try:
            # Twilio service returns the message SID if successful
            result = self.service.send_sms(to=to, body=message)
            return bool(result)
        except Exception as e:
            logger.error(f"Error sending SMS via Twilio: {str(e)}")
            return False
    
    def get_provider_name(self) -> str:
        """
        Get the name of the SMS provider.
        
        Returns:
            str: The name of the SMS provider.
        """
        return "twilio"
