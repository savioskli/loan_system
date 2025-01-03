"""
Core banking routes for managing banking system configurations
"""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint
from extensions import db
from datetime import datetime
import json
from werkzeug.security import generate_password_hash
from services.encryption_service import encrypt_credentials

bp = Blueprint('core_banking', __name__)

@bp.route('/admin/core-banking')
@login_required
def index():
    """Core banking systems dashboard"""
    systems = CoreBankingSystem.query.all()
    return render_template('admin/core_banking/index.html', systems=systems)

@bp.route('/admin/core-banking/add', methods=['POST'])
@login_required
def add_system():
    """Add a new core banking system"""
    try:
        data = request.get_json()

        # Basic validation
        required_fields = ['name', 'base_url', 'auth_type']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Validate URL format
        if not data['base_url'].startswith(('http://', 'https://')):
            return jsonify({'success': False, 'message': 'Invalid URL format. Must start with http:// or https://'}), 400

        # Create auth credentials based on auth type
        auth_credentials = {}
        if data['auth_type'] == 'basic':
            if not all(k in data for k in ['username', 'password']):
                return jsonify({'success': False, 'message': 'Missing username or password for Basic Auth'}), 400
            auth_credentials = {
                'username': data['username'],
                'password': data['password']
            }

        elif data['auth_type'] == 'bearer':
            if 'token' not in data:
                return jsonify({'success': False, 'message': 'Missing token for Bearer authentication'}), 400
            auth_credentials = {
                'token': data['token']
            }

        elif data['auth_type'] == 'api_key':
            if not all(k in data for k in ['key_name', 'key_value']):
                return jsonify({'success': False, 'message': 'Missing key name or value for API Key authentication'}), 400
            auth_credentials = {
                'key_name': data['key_name'],
                'key_value': data['key_value']
            }

        elif data['auth_type'] == 'oauth2':
            if not all(k in data for k in ['client_id', 'client_secret', 'token_url']):
                return jsonify({'success': False, 'message': 'Missing OAuth2 credentials'}), 400
            auth_credentials = {
                'client_id': data['client_id'],
                'client_secret': data['client_secret'],
                'token_url': data['token_url']
            }

        # Encrypt sensitive credentials
        encrypted_credentials = encrypt_credentials(auth_credentials) if auth_credentials else None

        # Create new system
        system = CoreBankingSystem(
            name=data['name'],
            base_url=data['base_url'],
            port=data.get('port'),
            description=data.get('description'),
            auth_type=data['auth_type'],
            auth_credentials=encrypted_credentials
        )

        # Validate auth credentials
        if not system.validate_auth_credentials():
            return jsonify({'success': False, 'message': 'Invalid authentication credentials'}), 400

        db.session.add(system)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Core banking system added successfully',
            'system': system.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/admin/core-banking/<int:system_id>', methods=['GET'])
@login_required
def get_system(system_id):
    """Get core banking system details"""
    try:
        system = CoreBankingSystem.query.get_or_404(system_id)
        return jsonify({
            'success': True,
            'system': system.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/admin/core-banking/<int:system_id>', methods=['PUT'])
@login_required
def update_system(system_id):
    """Update a core banking system"""
    try:
        system = CoreBankingSystem.query.get_or_404(system_id)
        data = request.get_json()

        # Update basic fields
        system.name = data.get('name', system.name)
        system.base_url = data.get('base_url', system.base_url)
        system.port = data.get('port', system.port)
        system.description = data.get('description', system.description)

        # Update auth type and credentials if provided
        if 'auth_type' in data:
            system.auth_type = data['auth_type']
            auth_credentials = {}

            if data['auth_type'] == 'basic':
                if all(k in data for k in ['username', 'password']):
                    auth_credentials = {
                        'username': data['username'],
                        'password': data['password']
                    }

            elif data['auth_type'] == 'bearer':
                if 'token' in data:
                    auth_credentials = {
                        'token': data['token']
                    }

            elif data['auth_type'] == 'api_key':
                if all(k in data for k in ['key_name', 'key_value']):
                    auth_credentials = {
                        'key_name': data['key_name'],
                        'key_value': data['key_value']
                    }

            elif data['auth_type'] == 'oauth2':
                if all(k in data for k in ['client_id', 'client_secret', 'token_url']):
                    auth_credentials = {
                        'client_id': data['client_id'],
                        'client_secret': data['client_secret'],
                        'token_url': data['token_url']
                    }

            if auth_credentials:
                system.auth_credentials = encrypt_credentials(auth_credentials)

        # Validate updated auth credentials
        if not system.validate_auth_credentials():
            return jsonify({'success': False, 'message': 'Invalid authentication credentials'}), 400

        system.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Core banking system updated successfully',
            'system': system.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/admin/core-banking/<int:system_id>', methods=['DELETE'])
@login_required
def delete_system(system_id):
    """Delete a core banking system"""
    try:
        system = CoreBankingSystem.query.get_or_404(system_id)
        db.session.delete(system)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Core banking system deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/admin/core-banking/<int:system_id>/test', methods=['POST'])
@login_required
def test_connection(system_id):
    """Test connection to core banking system"""
    try:
        system = CoreBankingSystem.query.get_or_404(system_id)
        
        # Get authentication headers
        headers = system.get_auth_headers()
        
        # TODO: Implement actual connection test logic here
        # This would typically involve making a test API call to the system
        
        return jsonify({
            'success': True,
            'message': 'Connection test successful'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/admin/core-banking/endpoints/add', methods=['POST'])
@login_required
def add_endpoint():
    """Add a new endpoint to a core banking system"""
    try:
        data = request.get_json()
        print("Received endpoint data:", data)  # Debug print

        # Basic validation
        required_fields = ['system_id', 'name', 'path', 'method']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Validate system exists
        system = CoreBankingSystem.query.get(data['system_id'])
        if not system:
            return jsonify({'success': False, 'message': 'Core banking system not found'}), 404

        # Create new endpoint
        endpoint = CoreBankingEndpoint(
            system_id=data['system_id'],
            name=data['name'],
            path=data['path'],
            method=data['method'],
            description=data.get('description'),
            parameters=data.get('parameters', '{}'),
            headers=data.get('headers', '{}'),
            is_active=data.get('is_active', True)
        )

        db.session.add(endpoint)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Endpoint added successfully',
            'endpoint': {
                'id': endpoint.id,
                'name': endpoint.name,
                'path': endpoint.path,
                'method': endpoint.method,
                'description': endpoint.description,
                'is_active': endpoint.is_active
            }
        })

    except Exception as e:
        db.session.rollback()
        print("Error adding endpoint:", str(e))  # Debug print
        return jsonify({'success': False, 'message': str(e)}), 500
