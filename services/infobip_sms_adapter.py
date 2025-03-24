import logging
from typing import Optional
from services.sms_gateway_interface import SmsGatewayInterface
from services.infobip_sms_service import InfobipSmsService, InfobipConfigurationError

logger = logging.getLogger(__name__)

class InfobipSmsAdapter(SmsGatewayInterface):
    """
    Adapter for the InfobipSmsService to conform to the SmsGatewayInterface.
    """
    
    def __init__(self, api_key: Optional[str] = None, sender_id: Optional[str] = None):
        """
        Initialize the InfobipSmsAdapter.
        
        Args:
            api_key (Optional[str]): The API key for authentication.
            sender_id (Optional[str]): The default sender ID for SMS.
        """
        try:
            # Get configuration from database if not provided
            if not api_key or not sender_id:
                from models.sms_gateway import SmsGatewayConfig
                config = SmsGatewayConfig.get_config_by_provider('infobip')
                if config:
                    api_key = api_key or config.sms_api_key
                    sender_id = sender_id or config.sms_sender_id
                    
            self.service = InfobipSmsService(api_key=api_key, default_sender_id=sender_id)
        except InfobipConfigurationError as e:
            logger.error(f"Infobip configuration error: {str(e)}")
            raise ValueError(f"Infobip configuration error: {str(e)}")
    
    def send_sms(self, to: str, message: str, sender_id: Optional[str] = None) -> bool:
        """
        Send an SMS message using Infobip.
        
        Args:
            to (str): The recipient's phone number.
            message (str): The SMS message content.
            sender_id (Optional[str]): The sender ID. If None, will use the default from configuration.
            
        Returns:
            bool: True if the SMS was sent successfully, False otherwise.
        """
        try:
            return self.service.send_sms(to=to, message=message, sender_id=sender_id)
        except Exception as e:
            logger.error(f"Error sending SMS via Infobip: {str(e)}")
            return False
    
    def get_provider_name(self) -> str:
        """
        Get the name of the SMS provider.
        
        Returns:
            str: The name of the SMS provider.
        """
        return "infobip"
