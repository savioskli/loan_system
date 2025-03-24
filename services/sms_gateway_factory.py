import logging
from typing import Optional
from models.sms_gateway import SmsGatewayConfig
from services.sms_gateway_interface import SmsGatewayInterface

logger = logging.getLogger(__name__)

class SmsGatewayFactory:
    """
    Factory class for creating SMS gateway service instances based on configuration.
    This allows the correspondence module to easily switch between different SMS providers.
    """
    
    @staticmethod
    def create_gateway(provider: Optional[str] = None, api_key: Optional[str] = None, 
                      sender_id: Optional[str] = None) -> SmsGatewayInterface:
        """
        Create and return an instance of the appropriate SMS gateway service.
        
        Args:
            provider (Optional[str]): The SMS provider to use. If None, will use the active config from database.
            api_key (Optional[str]): The API key for the SMS provider. If None, will use the config from database.
            sender_id (Optional[str]): The sender ID for the SMS provider. If None, will use the config from database.
            
        Returns:
            SmsGatewayInterface: An instance of the appropriate SMS gateway service.
            
        Raises:
            ValueError: If the provider is not supported or if required configuration is missing.
        """
        # Get the active configuration from the database
        # For this implementation, we only use a single provider configuration
        config = SmsGatewayConfig.get_active_config()
            
        if not config:
            raise ValueError("No SMS gateway configuration found in the database.")
        provider = config.sms_provider
        
        # Use provided API key and sender ID if specified, otherwise use from config
        actual_api_key = api_key if api_key else config.sms_api_key
        actual_sender_id = sender_id if sender_id else config.sms_sender_id
        
        # Create the appropriate gateway based on the provider
        if provider.lower() == 'twilio':
            from services.twilio_sms_adapter import TwilioSmsAdapter
            return TwilioSmsAdapter(api_key=actual_api_key, sender_id=actual_sender_id)
            
        elif provider.lower() == 'infobip':
            from services.infobip_sms_adapter import InfobipSmsAdapter
            return InfobipSmsAdapter(api_key=actual_api_key, sender_id=actual_sender_id)
            
        # Add more providers here as needed
        
        else:
            raise ValueError(f"Unsupported SMS provider: {provider}")
    
    @staticmethod
    def get_available_providers() -> list:
        """
        Get a list of all available SMS gateway providers.
        
        Returns:
            list: A list of available SMS gateway provider names.
        """
        return ['twilio', 'infobip']
