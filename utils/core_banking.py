from flask import current_app
import requests
from models.core_banking import CoreBankingEndpoint

def get_endpoint_data(endpoint_name, params=None):
    """
    Get data from a core banking endpoint
    """
    endpoint = CoreBankingEndpoint.query.filter_by(name=endpoint_name).first()
    if not endpoint:
        current_app.logger.error(f"Endpoint {endpoint_name} not found")
        return None

    try:
        # Get core banking config
        core_banking_url = current_app.config.get('CORE_BANKING_URL')
        api_key = current_app.config.get('CORE_BANKING_API_KEY')
        
        if not core_banking_url or not api_key:
            current_app.logger.error("Core banking URL or API key not configured")
            return None

        # Prepare headers
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Make request to core banking
        url = f"{core_banking_url.rstrip('/')}/{endpoint.path.lstrip('/')}"
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        current_app.logger.error(f"Error getting data from core banking: {str(e)}")
        return None
