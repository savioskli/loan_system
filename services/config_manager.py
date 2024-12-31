"""
Configuration manager for core banking integrations
"""
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint
from utils.encryption import encrypt_value, decrypt_value
from extensions import db
import json

class ConfigManager:
    @staticmethod
    def create_banking_system(name, base_url, auth_type, auth_credentials, headers=None, description=None, port=None):
        """Create a new core banking system configuration"""
        try:
            # Encrypt sensitive data
            if auth_credentials:
                auth_credentials = encrypt_value(json.dumps(auth_credentials))

            system = CoreBankingSystem(
                name=name,
                base_url=base_url,
                port=port,
                description=description,
                auth_type=auth_type,
                auth_credentials=auth_credentials,
                headers=json.dumps(headers) if headers else None
            )
            db.session.add(system)
            db.session.commit()
            return system
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create banking system: {str(e)}")

    @staticmethod
    def update_banking_system(system_id, **kwargs):
        """Update an existing core banking system configuration"""
        try:
            system = CoreBankingSystem.query.get(system_id)
            if not system:
                raise Exception("Banking system not found")

            # Handle auth credentials separately for encryption
            if 'auth_credentials' in kwargs:
                kwargs['auth_credentials'] = encrypt_value(json.dumps(kwargs['auth_credentials']))

            # Handle headers separately for JSON conversion
            if 'headers' in kwargs and isinstance(kwargs['headers'], dict):
                kwargs['headers'] = json.dumps(kwargs['headers'])

            for key, value in kwargs.items():
                if hasattr(system, key):
                    setattr(system, key, value)

            db.session.commit()
            return system
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update banking system: {str(e)}")

    @staticmethod
    def create_endpoint(system_id, name, endpoint, method, request_schema=None, response_schema=None, description=None):
        """Create a new endpoint configuration"""
        try:
            endpoint = CoreBankingEndpoint(
                system_id=system_id,
                name=name,
                endpoint=endpoint,
                method=method.upper(),
                description=description,
                request_schema=json.dumps(request_schema) if request_schema else None,
                response_schema=json.dumps(response_schema) if response_schema else None
            )
            db.session.add(endpoint)
            db.session.commit()
            return endpoint
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create endpoint: {str(e)}")

    @staticmethod
    def update_endpoint(endpoint_id, **kwargs):
        """Update an existing endpoint configuration"""
        try:
            endpoint = CoreBankingEndpoint.query.get(endpoint_id)
            if not endpoint:
                raise Exception("Endpoint not found")

            # Handle schema conversions
            if 'request_schema' in kwargs and isinstance(kwargs['request_schema'], dict):
                kwargs['request_schema'] = json.dumps(kwargs['request_schema'])
            if 'response_schema' in kwargs and isinstance(kwargs['response_schema'], dict):
                kwargs['response_schema'] = json.dumps(kwargs['response_schema'])

            for key, value in kwargs.items():
                if hasattr(endpoint, key):
                    setattr(endpoint, key, value)

            db.session.commit()
            return endpoint
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update endpoint: {str(e)}")

    @staticmethod
    def get_system_config(system_id):
        """Get a banking system configuration"""
        system = CoreBankingSystem.query.get(system_id)
        if not system:
            raise Exception("Banking system not found")
        
        # Decrypt sensitive data
        auth_credentials = system.auth_credentials
        if auth_credentials:
            auth_credentials = json.loads(decrypt_value(auth_credentials))

        return {
            'id': system.id,
            'name': system.name,
            'base_url': system.base_url,
            'port': system.port,
            'description': system.description,
            'auth_type': system.auth_type,
            'auth_credentials': auth_credentials,
            'headers': json.loads(system.headers) if system.headers else {},
            'is_active': system.is_active
        }

    @staticmethod
    def get_endpoint_config(endpoint_id):
        """Get an endpoint configuration"""
        endpoint = CoreBankingEndpoint.query.get(endpoint_id)
        if not endpoint:
            raise Exception("Endpoint not found")

        return {
            'id': endpoint.id,
            'system_id': endpoint.system_id,
            'name': endpoint.name,
            'endpoint': endpoint.endpoint,
            'method': endpoint.method,
            'description': endpoint.description,
            'request_schema': json.loads(endpoint.request_schema) if endpoint.request_schema else {},
            'response_schema': json.loads(endpoint.response_schema) if endpoint.response_schema else {},
            'is_active': endpoint.is_active
        }
