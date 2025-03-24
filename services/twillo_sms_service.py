import re  # Import the re module for regular expressions
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
from models.sms_gateway import SmsGatewayConfig  # Import the SMS Gateway Config model

logger = logging.getLogger(__name__)

class TwilioSmsService:
    def __init__(self, account_sid=None, auth_token=None, from_number=None):
        """
        Initialize the Twilio SMS Service.
        
        Args:
            account_sid (str, optional): The Twilio account SID. If None, will be retrieved from DB.
            auth_token (str, optional): The Twilio auth token. If None, will be retrieved from DB.
            from_number (str, optional): The sender phone number. If None, will be retrieved from DB.
        """
        # If parameters are not provided, retrieve from database
        if not account_sid or not auth_token or not from_number:
            config = SmsGatewayConfig.query.first()
            if not config:
                raise ValueError("SMS Gateway configuration not found in the database.")
            
            # Use provided values or fall back to database values
            account_sid = account_sid or config.twilio_account_sid
            auth_token = auth_token or config.twilio_auth_token
            from_number = from_number or config.sms_sender_id

        # Validate Twilio-specific fields
        if not account_sid or not auth_token:
            raise ValueError("Twilio Account SID or Auth Token missing.")

        self.client = Client(account_sid, auth_token)
        self.sender_id = from_number

        # Validate sender ID format (Twilio requires E.164 or alphanumeric)
        if not self._validate_sender_id():
            raise ValueError("Invalid Twilio Sender ID. Must be a valid phone number or alphanumeric ID.")

    def _validate_sender_id(self):
        """
        Validate the sender ID format.
        - E.164 format: +1234567890
        - Alphanumeric: Up to 11 characters (e.g., MyCompany)
        """
        return re.match(r'^\+?[1-9]\d{1,14}$', self.sender_id) or re.match(r'^[a-zA-Z0-9 ]+$', self.sender_id)

    def send_sms(self, to, body):
        """
        Send an SMS message using Twilio.

        :param to: The recipient's phone number in E.164 format.
        :param body: The content of the SMS message.
        """
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.sender_id,
                to=to
            )
            logger.info(f"Twilio SMS sent to {to}. SID: {message.sid}")
            return message.sid
        except TwilioRestException as e:
            logger.error(f"Twilio Error (Code {e.code}): {e.msg}")
            raise ValueError(f"Twilio Error: {e.msg}")  # User-friendly message