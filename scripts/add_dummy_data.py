import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import json
from app import create_app
from extensions import db
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint

def add_dummy_data():
    app = create_app()
    with app.app_context():
        # Add dummy core banking systems
        systems = [
            {
                'name': 'Temenos T24',
                'base_url': 'https://api.temenos.com',
                'port': 443,
                'description': 'Temenos T24 Core Banking System',
                'auth_type': 'oauth2',
                'auth_credentials': json.dumps({
                    'client_id': 'dummy_client_id',
                    'client_secret': 'dummy_client_secret',
                    'token_url': 'https://api.temenos.com/oauth/token'
                }),
                'headers': json.dumps({
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }),
                'is_active': True
            },
            {
                'name': 'Fiserv DNA',
                'base_url': 'https://api.fiserv.com',
                'port': 443,
                'description': 'Fiserv DNA Core Banking Platform',
                'auth_type': 'api_key',
                'auth_credentials': json.dumps({
                    'api_key': 'dummy_api_key'
                }),
                'headers': json.dumps({
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }),
                'is_active': True
            }
        ]

        # Add systems
        for system_data in systems:
            system = CoreBankingSystem(**system_data)
            db.session.add(system)
            db.session.commit()

            # Add endpoints for each system
            endpoints = [
                {
                    'system_id': system.id,
                    'name': 'Get Account Balance',
                    'path': '/accounts/{account_id}/balance',
                    'method': 'GET',
                    'description': 'Retrieve account balance',
                    'parameters': json.dumps({
                        'account_id': {'type': 'string', 'required': True}
                    }),
                    'headers': json.dumps({
                        'X-Transaction-ID': 'string'
                    }),
                    'is_active': True
                },
                {
                    'system_id': system.id,
                    'name': 'Get Transaction History',
                    'path': '/accounts/{account_id}/transactions',
                    'method': 'GET',
                    'description': 'Retrieve transaction history',
                    'parameters': json.dumps({
                        'account_id': {'type': 'string', 'required': True},
                        'start_date': {'type': 'string', 'format': 'date'},
                        'end_date': {'type': 'string', 'format': 'date'}
                    }),
                    'headers': json.dumps({
                        'X-Transaction-ID': 'string'
                    }),
                    'is_active': True
                },
                {
                    'system_id': system.id,
                    'name': 'Make Transfer',
                    'path': '/transfers',
                    'method': 'POST',
                    'description': 'Make a funds transfer',
                    'parameters': json.dumps({
                        'from_account': {'type': 'string', 'required': True},
                        'to_account': {'type': 'string', 'required': True},
                        'amount': {'type': 'number', 'required': True},
                        'currency': {'type': 'string', 'required': True},
                        'reference': {'type': 'string'}
                    }),
                    'headers': json.dumps({
                        'X-Transaction-ID': 'string',
                        'Idempotency-Key': 'string'
                    }),
                    'is_active': True
                }
            ]

            for endpoint_data in endpoints:
                endpoint = CoreBankingEndpoint(**endpoint_data)
                db.session.add(endpoint)
            
            db.session.commit()

        print("Dummy data added successfully!")

if __name__ == '__main__':
    add_dummy_data()
