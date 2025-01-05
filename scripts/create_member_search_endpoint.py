import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint
from extensions import db
import json

def create_member_search_endpoint():
    app = create_app()
    with app.app_context():
        # Get active core banking system
        system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not system:
            print("No active core banking system found")
            return
        
        # Check if endpoint already exists
        existing_endpoint = CoreBankingEndpoint.query.filter_by(
            system_id=system.id,
            name='search_members',
            is_active=True
        ).first()
        
        if existing_endpoint:
            print(f"Endpoint already exists with ID: {existing_endpoint.id}")
            return existing_endpoint
        
        # Create new endpoint
        endpoint = CoreBankingEndpoint(
            system_id=system.id,
            name='search_members',
            path='/members/search',
            method='GET',
            description='Search for members in core banking system',
            parameters=json.dumps({
                'query': {'type': 'string', 'required': True, 'description': 'Search query (name or member number)'},
                'page': {'type': 'integer', 'required': False, 'default': 1, 'description': 'Page number for pagination'},
                'limit': {'type': 'integer', 'required': False, 'default': 10, 'description': 'Number of results per page'}
            }),
            is_active=True
        )
        
        try:
            db.session.add(endpoint)
            db.session.commit()
            print(f"Created member search endpoint with ID: {endpoint.id}")
            return endpoint
        except Exception as e:
            db.session.rollback()
            print(f"Error creating endpoint: {str(e)}")
            return None

if __name__ == '__main__':
    create_member_search_endpoint()
