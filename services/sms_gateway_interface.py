from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SmsGatewayInterface(ABC):
    """
    Abstract base class that defines the interface for all SMS gateway implementations.
    All SMS gateway services should inherit from this class and implement its methods.
    """
    
    @abstractmethod
    def send_sms(self, to: str, message: str, sender_id: Optional[str] = None) -> bool:
        """
        Send an SMS message.
        
        Args:
            to (str): The recipient's phone number.
            message (str): The SMS message content.
            sender_id (Optional[str]): The sender ID or phone number. May be overridden by provider defaults.
            
        Returns:
            bool: True if the SMS was sent successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the SMS provider.
        
        Returns:
            str: The name of the SMS provider.
        """
        pass
