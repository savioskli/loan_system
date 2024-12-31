"""
API manager for handling core banking API requests
"""
import requests
import json
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint, CoreBankingLog
from utils.encryption import decrypt_value
from extensions import db
from datetime import datetime

class APIManager:
    def __init__(self, system_id):
        """Initialize API manager with a banking system ID"""
        self.system = CoreBankingSystem.query.get(system_id)
        if not self.system:
            raise Exception("Banking system not found")
        
        # Decrypt auth credentials
        self.auth_credentials = {}
        if self.system.auth_credentials:
            self.auth_credentials = json.loads(decrypt_value(self.system.auth_credentials))

        # Get base headers
        self.base_headers = self.system.headers_dict

    def _get_auth_header(self):
        """Get authentication header based on auth type"""
        if self.system.auth_type == 'basic':
            import base64
            auth_string = f"{self.auth_credentials.get('username')}:{self.auth_credentials.get('password')}"
            auth_bytes = auth_string.encode('ascii')
            base64_bytes = base64.b64encode(auth_bytes)
            return {'Authorization': f'Basic {base64_bytes.decode("ascii")}'}
        elif self.system.auth_type == 'bearer':
            return {'Authorization': f'Bearer {self.auth_credentials.get("token")}'}
        elif self.system.auth_type == 'api_key':
            key_name = self.auth_credentials.get('key_name', 'X-API-Key')
            return {key_name: self.auth_credentials.get('key')}
        return {}

    def _get_full_url(self, endpoint):
        """Get full URL for the endpoint"""
        base_url = self.system.base_url.rstrip('/')
        if self.system.port:
            base_url = f"{base_url}:{self.system.port}"
        endpoint = endpoint.lstrip('/')
        return f"{base_url}/{endpoint}"

    def _log_request(self, endpoint_id, method, url, headers, body, response=None, error=None):
        """Log API request and response"""
        try:
            log = CoreBankingLog(
                system_id=self.system.id,
                endpoint_id=endpoint_id,
                request_method=method,
                request_url=url,
                request_headers=json.dumps(headers),
                request_body=json.dumps(body) if body else None,
                response_status=response.status_code if response else None,
                response_body=response.text if response else None,
                error_message=str(error) if error else None
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to log request: {str(e)}")

    def make_request(self, endpoint_id, **kwargs):
        """Make an API request to the specified endpoint"""
        endpoint = CoreBankingEndpoint.query.get(endpoint_id)
        if not endpoint:
            raise Exception("Endpoint not found")

        # Prepare request
        url = self._get_full_url(endpoint.endpoint)
        headers = {**self.base_headers, **self._get_auth_header()}
        method = endpoint.method.lower()

        try:
            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            # Log request
            self._log_request(
                endpoint_id=endpoint.id,
                method=method,
                url=url,
                headers=headers,
                body=kwargs.get('json') or kwargs.get('data'),
                response=response
            )

            # Raise for bad status
            response.raise_for_status()

            return response.json() if response.text else None

        except requests.exceptions.RequestException as e:
            # Log error
            self._log_request(
                endpoint_id=endpoint.id,
                method=method,
                url=url,
                headers=headers,
                body=kwargs.get('json') or kwargs.get('data'),
                error=e
            )
            raise Exception(f"API request failed: {str(e)}")

    def get(self, endpoint_id, **kwargs):
        """Make a GET request"""
        return self.make_request(endpoint_id, **kwargs)

    def post(self, endpoint_id, **kwargs):
        """Make a POST request"""
        return self.make_request(endpoint_id, **kwargs)

    def put(self, endpoint_id, **kwargs):
        """Make a PUT request"""
        return self.make_request(endpoint_id, **kwargs)

    def delete(self, endpoint_id, **kwargs):
        """Make a DELETE request"""
        return self.make_request(endpoint_id, **kwargs)
