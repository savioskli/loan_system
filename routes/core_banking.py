"""
Core banking routes for managing banking system configurations
"""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint, CoreBankingLog
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
def get_chart_data(system_id):
    """Generate chart data for last 7 days"""
    from datetime import datetime, timedelta
    
    dates = []
    success_data = []
    error_data = []
    
    for i in range(6, -1, -1):
        date = datetime.now() - timedelta(days=i)
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        total = CoreBankingLog.query.filter(
            CoreBankingLog.system_id == system_id,
            CoreBankingLog.created_at.between(start, end)
        ).count()
        
        errors = CoreBankingLog.query.filter(
            CoreBankingLog.system_id == system_id,
            CoreBankingLog.error_message.isnot(None),
            CoreBankingLog.created_at.between(start, end)
        ).count()
        
        dates.append(date.strftime('%Y-%m-%d'))
        success_data.append(total - errors)
        error_data.append(errors)
    
    return {
        'labels': dates,
        'success_data': success_data,
        'error_data': error_data
    }
@bp.route('/api/core-banking/system/<int:system_id>')
@login_required
def get_system_details(system_id):
    """Get complete system details for view modal"""
    try:
        system = CoreBankingSystem.query.get_or_404(system_id)
        
        # Get endpoints
        endpoints = CoreBankingEndpoint.query.filter_by(system_id=system_id).all()
        
        # Get recent logs (last 50)
        logs = CoreBankingLog.query.filter_by(system_id=system_id)\
                   .order_by(CoreBankingLog.created_at.desc())\
                   .limit(50).all()
        
        # Calculate stats
        total_requests = CoreBankingLog.query.filter_by(system_id=system_id).count()
        error_requests = CoreBankingLog.query.filter(CoreBankingLog.error_message.isnot(None)).count()
        active_endpoints = CoreBankingEndpoint.query.filter_by(system_id=system_id, is_active=True).count()
        
        # Calculate endpoint stats
        endpoint_stats = {}
        for endpoint in endpoints:
            total = CoreBankingLog.query.filter_by(endpoint_id=endpoint.id).count()
            errors = CoreBankingLog.query.filter_by(endpoint_id=endpoint.id)\
                        .filter(CoreBankingLog.error_message.isnot(None)).count()
            success_rate = ((total - errors) / total * 100) if total > 0 else 100
            endpoint_stats[endpoint.id] = {
                'success_rate': success_rate,
                'total_requests': total
            }

        return jsonify({
            'status': 'success',
            'data': {
                'system': system.to_dict(),
                'endpoints': [e.to_dict() for e in endpoints],
                'logs': [l.to_dict() for l in logs],
                'stats': {
                    'total_requests': total_requests,
                    'error_requests': error_requests,
                    'active_endpoints': active_endpoints,
                    'success_rate': ((total_requests - error_requests) / total_requests * 100) if total_requests > 0 else 100,
                    'endpoint_stats': endpoint_stats
                },
                'chart_data': get_chart_data(system_id)  # Implement this function
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
    """Test connection to core banking system database"""
    try:
        # Get the system from database for logging purposes
        system = CoreBankingSystem.query.get_or_404(system_id)
        
        # Get the updated data from request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
            
        # Validate base URL and port
        base_url = data.get('base_url', '').rstrip('/')
        if not base_url:
            return jsonify({
                'success': False,
                'message': 'Host/IP is required'
            }), 400
            
        # Remove http:// or https:// prefix for MySQL connection
        base_url = base_url.replace('http://', '').replace('https://', '')
            
        port = data.get('port')
        if not port:
            port = 3306  # Default MySQL port
            
        # Validate auth credentials
        auth_type = data.get('auth_type')
        if not auth_type or auth_type != 'basic':
            return jsonify({
                'success': False,
                'message': 'Basic authentication is required for database connection'
            }), 400
            
        if not all(k in data for k in ['username', 'password']):
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
            
        # Test MySQL connection
        try:
            import mysql.connector
            
            conn = mysql.connector.connect(
                host=base_url,
                port=int(port),
                user=data['username'],
                password=data['password'],
                connection_timeout=10  # 10 second timeout
            )
            
            # If connection successful, try to get server version
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            # Close cursor and connection
            cursor.close()
            conn.close()
            
            # Log the successful test
            log = CoreBankingLog(
                system_id=system.id,
                request_method='CONNECT',
                request_url=f"mysql://{base_url}:{port}",
                response_status=200,
                response_body=f"Connected successfully. MySQL version: {version}"
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Connection successful! MySQL version: {version}'
            })
            
        except mysql.connector.Error as err:
            error_message = str(err)
            
            # Log the failed attempt
            log = CoreBankingLog(
                system_id=system.id,
                request_method='CONNECT',
                request_url=f"mysql://{base_url}:{port}",
                error_message=error_message
            )
            db.session.add(log)
            db.session.commit()
            
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                message = "Access denied. Please check your username and password."
            elif err.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
                message = "Failed to connect to server. Please check the host and port."
            else:
                message = f"Database error: {error_message}"
                
            return jsonify({
                'success': False,
                'message': message
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error testing connection: {str(e)}'
        }), 500

@bp.route('/admin/core-banking/<int:system_id>/databases', methods=['GET'])
@login_required
def list_databases(system_id):
    """List available databases for a core banking system"""
    try:
        system = CoreBankingSystem.query.get_or_404(system_id)
        databases = system.list_databases()
        return jsonify({'success': True, 'databases': databases})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/admin/core-banking/<int:system_id>/database', methods=['PUT'])
@login_required
def select_database(system_id):
    """Select a database for a core banking system"""
    try:
        system = CoreBankingSystem.query.get_or_404(system_id)
        data = request.get_json()
        
        if 'database_name' not in data:
            return jsonify({'success': False, 'message': 'Database name is required'}), 400
        
        system.select_database(data['database_name'])
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Database selected successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/admin/core-banking/<int:system_id>/tables', methods=['GET', 'PUT'])
@login_required
def manage_tables(system_id):
    """Manage tables for a core banking system"""
    try:
        system = CoreBankingSystem.query.get_or_404(system_id)
        
        if request.method == 'GET':
            # Get available tables and their schemas
            tables = []
            for table_name in system.list_tables():
                schema = system.get_table_schema(table_name)
                tables.append({
                    'name': table_name,
                    'fields': schema
                })
            
            # Get current table configuration
            current_config = {}
            if system.selected_tables:
                current_config = json.loads(system.selected_tables)
            
            return jsonify({
                'success': True, 
                'tables': tables,
                'current_config': current_config
            })
        else:  # PUT
            data = request.get_json()
            if 'table_configs' not in data:
                return jsonify({'success': False, 'message': 'Table configurations are required'}), 400
            
            system.configure_tables(data['table_configs'])
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Tables configured successfully'})
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
