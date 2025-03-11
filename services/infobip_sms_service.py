import http.client
import json
import logging
from typing import Optional
from models.sms_gateway import SmsGatewayConfig  # Assuming this is your database model

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class InfobipConfigurationError(Exception):
    """Custom exception for Infobip configuration errors."""
    pass

class InfobipSmsService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_sender_id: Optional[str] = None
    ):
        """
        Initialize the Infobip SMS service.

        Args:
            api_key (Optional[str]): The API key for authentication.
            default_sender_id (Optional[str]): The default sender ID for SMS.
        """
        if api_key is None:
            # Fetch configuration from the database
            config = SmsGatewayConfig.query.first()
            if not config:
                raise InfobipConfigurationError("SMS Gateway configuration not found.")
            if not config.infobip_base_url or not config.sms_api_key:
                raise InfobipConfigurationError("Infobip base URL or API key missing.")

            self.base_url = config.infobip_base_url
            self.api_key = config.sms_api_key
            self.default_sender_id = config.sms_sender_id
        else:
            # Use provided parameters
            self.base_url = "kqvmj8.api.infobip.com"  # Static base URL for Infobip API
            self.api_key = api_key
            self.default_sender_id = default_sender_id

        self.headers = {
            'Authorization': f'App {self.api_key}',  # Directly use the provided API key
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def send_sms(self, to: str, message: str, sender_id: Optional[str] = None) -> bool:
        """
        Send an SMS using the Infobip API.

        Args:
            to (str): The recipient's phone number.
            message (str): The SMS message content.
            sender_id (Optional[str]): The sender ID. Defaults to the service's default sender ID.

        Returns:
            bool: True if the SMS was sent successfully, False otherwise.
        """
        sender = sender_id or self.default_sender_id
        if not sender:
            raise ValueError("Sender ID is required.")

        endpoint = "/sms/2/text/advanced"
        payload = json.dumps({
            "messages": [
                {
                    "destinations": [{"to": to}],
                    "from": sender,
                    "text": message
                }
            ]
        })

        # Establish connection and send request
        conn = http.client.HTTPSConnection(self.base_url)
        try:
            # Log headers and payload for debugging
            logger.debug(f"Headers: {self.headers}")
            logger.debug(f"Payload: {payload}")

            conn.request("POST", endpoint, payload, self.headers)
            res = conn.getresponse()
            data = res.read()
            response_data = json.loads(data.decode("utf-8"))

            # Log the full response
            logger.info(f"Infobip API response: {response_data}")

            # Check for errors in the response
            if "requestError" in response_data:
                logger.error(f"Infobip API Error: {response_data['requestError']}")
                return False

            # Check for 'messages' field
            messages = response_data.get("messages", None)
            if not messages:
                logger.error(f"No 'messages' field in response: {response_data}")
                return False

            # Validate the status group
            status_group = messages[0].get("status", {}).get("groupId")
            if status_group == 1:
                logger.info(f"SMS to {to} accepted by Infobip.")
                return True
            else:
                logger.error(f"Infobip error: Status group {status_group}, {response_data}")
                return False

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return False
