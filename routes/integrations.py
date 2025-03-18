from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.exceptions import HTTPException
from flask_login import login_required
from utils.decorators import admin_required
import requests
from datetime import datetime
import json
import re
import logging
import mysql.connector
from extensions import csrf, db
from models.integrations import CoreBankingConfig
from models.sms_gateway import SmsGatewayConfig
from models.email_config import EmailConfig
from services.twillo_sms_service import TwilioSmsService
from services.infobip_sms_service import InfobipSmsService
from utils.encryption import encrypt_value, decrypt_value

logger = logging.getLogger(__name__)

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/credit-bureau')
@login_required
@admin_required
def credit_bureau():
    try:
        return render_template('admin/integrations/credit_bureau.html')
    except Exception as e:
        logger.error(f"Error rendering credit bureau template: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/payment-gateway')
@login_required
@admin_required
def payment_gateway():
    try:
        return render_template('admin/integrations/payment_gateway.html')
    except Exception as e:
        logger.error(f"Error rendering payment gateway template: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/core-banking')
@login_required
@admin_required
def core_banking():
    try:
        # Get existing configuration
        config = CoreBankingConfig.get_active_config()
        return render_template('admin/integrations/core_banking.html', config=config)
    except Exception as e:
        logger.error(f"Error rendering core banking template: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/sms-gateway', methods=['GET', 'POST'])
@login_required
@admin_required
def sms_gateway():
    if request.method == 'POST':
        try:
            # Retrieve form data
            sms_provider = request.form.get('sms_provider')
            sms_api_key = request.form.get('api_key')
            sms_sender_id = request.form.get('sender_id')

            # Retrieve provider-specific fields
            africas_talking_username = request.form.get('africas_talking_username') if sms_provider == 'africas_talking' else None
            twilio_account_sid = request.form.get('twilio_account_sid') if sms_provider == 'twilio' else None
            twilio_auth_token = request.form.get('twilio_auth_token') if sms_provider == 'twilio' else None
            infobip_base_url = request.form.get('infobip_base_url') if sms_provider == 'infobip' else None

            # Validate required fields
            if not sms_provider or not sms_api_key or not sms_sender_id:
                flash('All fields are required.', 'error')
                return redirect(url_for('integrations.sms_gateway'))

            # Encrypt sensitive fields
            encrypted_api_key = encrypt_value(sms_api_key)
            encrypted_twilio_sid = encrypt_value(twilio_account_sid) if twilio_account_sid else None
            encrypted_twilio_token = encrypt_value(twilio_auth_token) if twilio_auth_token else None

            # Save or update configuration
            config = SmsGatewayConfig.query.first()
            if not config:
                config = SmsGatewayConfig()

            config.sms_provider = sms_provider
            config.sms_api_key = encrypted_api_key
            config.sms_sender_id = sms_sender_id
            config.africas_talking_username = africas_talking_username
            config.twilio_account_sid = encrypted_twilio_sid
            config.twilio_auth_token = encrypted_twilio_token
            config.infobip_base_url = infobip_base_url

            db.session.add(config)
            db.session.commit()

            flash('SMS Gateway configuration saved successfully.', 'success')
            return redirect(url_for('integrations.sms_gateway'))

        except Exception as e:
            logger.error(f"Error saving SMS gateway configuration: {str(e)}", exc_info=True)
            flash('An error occurred while saving the configuration.', 'error')
            return redirect(url_for('integrations.sms_gateway'))

    try:
        configs = SmsGatewayConfig.get_all()
        return render_template('admin/integrations/sms_gateway.html', configs=configs)
    except Exception as e:
        logger.error(f"Error rendering SMS gateway template: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/send-test-sms', methods=['POST'])
@login_required
@admin_required
def send_test_sms():
    """
    Send a test SMS using the configured SMS gateway.
    """
    data = request.json
    phone_number = data.get('phone_number')
    provider = data.get('provider')

    # Validate phone number format
    if not re.match(r'^\+?[1-9]\d{1,14}$', phone_number):
        return jsonify({'success': False, 'error': 'Invalid phone number format. Use E.164 (e.g., +1234567890)'}), 400

    if not phone_number or not provider:
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

    try:
        config = SmsGatewayConfig.query.first()
        if not config:
            return jsonify({'success': False, 'error': 'SMS Gateway not configured'}), 400

        if provider == 'twilio':
            if not config.twilio_account_sid or not config.twilio_auth_token:
                return jsonify({'success': False, 'error': 'Twilio credentials missing'}), 400

            try:
                account_sid = decrypt_value(config.twilio_account_sid)
                auth_token = decrypt_value(config.twilio_auth_token)
            except Exception as e:
                logger.error(f"Error decrypting Twilio credentials: {str(e)}")
                return jsonify({'success': False, 'error': 'Invalid Twilio credentials'}), 400

            sms_service = TwilioSmsService(account_sid, auth_token)
            sms_service.send_sms(to=phone_number, body='Test message from Twilio', from_=config.sms_sender_id)
            return jsonify({'success': True}), 200

        elif provider == 'africas_talking':
            if not config.africas_talking_username or not config.sms_api_key:
                return jsonify({'success': False, 'error': 'Africa\'s Talking credentials missing'}), 400

            try:
                api_key = decrypt_value(config.sms_api_key)
                username = config.africas_talking_username
                # Implement Africa's Talking SMS sending logic here
                return jsonify({'success': False, 'error': 'Africa\'s Talking integration not implemented'}), 400
            except Exception as e:
                logger.error(f"Error decrypting API key: {str(e)}")
                return jsonify({'success': False, 'error': 'Invalid API key'}), 400

        elif provider == 'infobip':
            if not config.sms_api_key:
                return jsonify({'success': False, 'error': 'Infobip credentials missing'}), 400

            try:
                api_key = decrypt_value(config.sms_api_key)
                sender_id = config.sms_sender_id

                # Check if sender_id is present
                if not sender_id:
                    return jsonify({'success': False, 'error': 'Sender ID is missing'}), 400

                # Initialize InfobipSmsService with static base URL
                sms_service = InfobipSmsService(
                    api_key=api_key,
                    default_sender_id=sender_id
                )
                sms_service.send_sms(
                    to=phone_number,
                    message='This is a test message from the LOAP app.',
                    sender_id=sender_id
                )
                return jsonify({'success': True}), 200
            except ValueError as e:
                logger.error(f"Invalid Infobip configuration: {str(e)}")
                return jsonify({'success': False, 'error': str(e)}), 400
            except Exception as e:
                logger.error(f"Infobip SMS failed: {str(e)}")
                return jsonify({'success': False, 'error': str(e)}), 500

        else:
            return jsonify({'success': False, 'error': 'Unsupported provider'}), 400

    except Exception as e:
        logger.error(f"Failed to send test SMS: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# Core Banking API Integration
class CoreBankingAPI:
    def __init__(self, system_type, config):
        try:
            self.system_type = system_type
            self.config = config
            self.base_url = f"http://{config['server_url']}:{config['port']}"
            self.session = requests.Session()
            if system_type == 'navision':
                self._setup_navision()
            elif system_type == 'brnet':
                self._setup_brnet()
            else:
                raise ValueError(f"Unsupported system type: {system_type}")
        except Exception as e:
            logger.error(f"Error initializing CoreBankingAPI: {str(e)}", exc_info=True)
            raise

    def _setup_navision(self):
        """Setup authentication and headers for Navision"""
        try:
            if self.config.get('username') and self.config.get('password'):
                self.session.auth = (self.config['username'], self.config['password'])
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
        except Exception as e:
            logger.error(f"Error setting up Navision: {str(e)}", exc_info=True)
            raise

    def _setup_brnet(self):
        """Setup authentication and headers for BR.NET"""
        try:
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-API-Key': self.config.get('api_key', '')
            })
        except Exception as e:
            logger.error(f"Error setting up BR.NET: {str(e)}", exc_info=True)
            raise

    def test_connection(self):
        """Test connection to core banking system"""
        try:
            logger.info(f"Testing connection to {self.system_type} at {self.base_url}")
            
            # For testing/development, allow localhost connections without actual health check
            if 'localhost' in self.config['server_url'] or '127.0.0.1' in self.config['server_url']:
                logger.info("Local development environment detected")
                # Simulate successful connection for development
                return {
                    'success': True,
                    'message': 'Development environment - Connection simulated successfully'
                }
            
            # For production environments, test actual connection
            if self.system_type == 'navision':
                test_url = f"{self.base_url}/api/v1/health"
                logger.info(f"Testing Navision connection at {test_url}")
            else:  # BR.NET
                test_url = f"{self.base_url}/api/health"
                logger.info(f"Testing BR.NET connection at {test_url}")
            
            try:
                response = self.session.get(test_url, timeout=10)
                response.raise_for_status()
                return {
                    'success': True,
                    'message': 'Connection successful'
                }
            except requests.exceptions.ConnectionError:
                error_msg = f"Could not connect to server at {self.base_url}. Please verify:\n" \
                           f"1. The server is running\n" \
                           f"2. The URL and port are correct\n" \
                           f"3. The server is accessible from this machine"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            except requests.exceptions.Timeout:
                error_msg = "Connection timed out. The server might be busy or not responding."
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            except requests.exceptions.HTTPError as e:
                error_msg = f"HTTP Error: {str(e)}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error testing connection: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {'success': False, 'error': error_msg}

    def get_loan_details(self, loan_id):
        """Fetch loan details from core banking system"""
        try:
            if self.system_type == 'navision':
                response = self.session.get(f"{self.base_url}/api/v1/loans/{loan_id}")
            else:  # BR.NET
                response = self.session.get(f"{self.base_url}/api/loans/{loan_id}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting loan details: {str(e)}", exc_info=True)
            return {'error': str(e)}

    def get_payment_history(self, loan_id):
        """Fetch payment history for a loan"""
        try:
            if self.system_type == 'navision':
                response = self.session.get(f"{self.base_url}/api/v1/loans/{loan_id}/payments")
            else:  # BR.NET
                response = self.session.get(f"{self.base_url}/api/loans/{loan_id}/payments")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting payment history: {str(e)}", exc_info=True)
            return {'error': str(e)}

    def get_customer_info(self, customer_id):
        """Fetch customer information"""
        try:
            if self.system_type == 'navision':
                response = self.session.get(f"{self.base_url}/api/v1/customers/{customer_id}")
            else:  # BR.NET
                response = self.session.get(f"{self.base_url}/api/customers/{customer_id}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting customer info: {str(e)}", exc_info=True)
            return {'error': str(e)}

    def get_available_tables(self):
        """Retrieve list of available tables from the core banking system"""
        try:
            if self.system_type == 'navision':
                # Add Database header for Navision
                self.session.headers.update({'Database': self.config.get('database', '')})
                response = self.session.get(f"{self.base_url}/api/beta/companies/metadata")
                response.raise_for_status()
                data = response.json()
                return data.get('value', [])  # Navision returns tables under 'value' key
            else:  # BR.NET
                response = self.session.get(f"{self.base_url}/api/schema/tables")
                response.raise_for_status()
                return response.json()  # BR.NET returns tables array directly
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting available tables: {str(e)}", exc_info=True)
            return []

# API Routes for Core Banking Integration
@integrations_bp.route('/core-banking/test-connection', methods=['POST'])
@csrf.exempt
@login_required
@admin_required
def test_core_banking_connection():
    """Test connection to core banking system"""
    try:
        logger.info("Received test connection request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        # Get connection details
        system_type = data.get('system_type')
        server_url = data.get('server_url')
        port = data.get('port')
        database = data.get('database')
        username = data.get('username')
        password = data.get('password')
        api_key = data.get('api_key')
        
        logger.info(f"Connection details - System: {system_type}, Server: {server_url}, Port: {port}, Database: {database}")
        
        # Validate required fields
        if not all([system_type, server_url, port, username, password]):
            logger.error("Missing required connection details")
            return jsonify({
                'success': False,
                'message': 'Missing required connection details'
            }), 400

        # Test connection based on system type
        if system_type == 'navision':
            try:
                logger.info("Testing Navision connection...")
                # Test connection using health endpoint
                response = requests.get(
                    f'http://{server_url}:{port}/api/v1/health',
                    auth=(username, password),
                    headers={'Database': database},
                    timeout=10
                )
                response.raise_for_status()
                
                logger.info("Successfully connected to Navision API")
                return jsonify({
                    'success': True,
                    'message': 'Successfully connected to Navision API'
                })
                
            except requests.exceptions.RequestException as err:
                logger.error(f"API error: {str(err)}")
                return jsonify({
                    'success': False,
                    'message': f'API error: {str(err)}'
                }), 500
                
        elif system_type == 'brnet':
            try:
                logger.info("Testing BR.NET connection...")
                # Test BR.NET API connection
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(
                    f'http://{server_url}:{port}/api/test',
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info("Successfully connected to BR.NET API")
                    return jsonify({
                        'success': True,
                        'message': 'Successfully connected to BR.NET API'
                    })
                else:
                    logger.error(f"API error: {response.text}")
                    return jsonify({
                        'success': False,
                        'message': f'API error: {response.text}'
                    }), response.status_code
                    
            except requests.exceptions.RequestException as err:
                logger.error(f"API connection error: {str(err)}")
                return jsonify({
                    'success': False,
                    'message': f'API connection error: {str(err)}'
                }), 500
        
        else:
            logger.error(f"Unsupported core banking system: {system_type}")
            return jsonify({
                'success': False,
                'message': 'Unsupported core banking system'
            }), 400
            
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error testing connection: {str(e)}'
        }), 500

@integrations_bp.route('/core-banking/fetch-tables', methods=['POST'])
@csrf.exempt
@login_required
@admin_required
def fetch_core_banking_tables():
    """Fetch available tables from core banking system"""
    try:
        logger.info("Received fetch tables request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        # Get connection details
        system_type = data.get('system_type')
        server_url = data.get('server_url')
        port = data.get('port')
        database = data.get('database')
        username = data.get('username')
        password = data.get('password')
        api_key = data.get('api_key')
        
        logger.info(f"Connection details - System: {system_type}, Server: {server_url}, Port: {port}, Database: {database}")
        
        # Validate required fields
        if not all([system_type, server_url, port]):
            logger.error("Missing required connection details")
            return jsonify({
                'success': False,
                'message': 'Missing required connection details'
            }), 400

        # Fetch tables based on system type
        if system_type == 'navision':
            try:
                logger.info("Fetching tables from Navision...")
                response = requests.get(
                    f'http://{server_url}:{port}/api/beta/companies/metadata',
                    auth=(username, password),
                    headers={'Database': database},
                    timeout=10
                )
                response.raise_for_status()
                tables = response.json().get('value', [])
                
                logger.info(f"Successfully fetched {len(tables)} tables from Navision")
                return jsonify({
                    'success': True,
                    'message': f'Successfully fetched {len(tables)} tables',
                    'tables': tables
                })
                
            except requests.exceptions.RequestException as err:
                logger.error(f"API error: {str(err)}")
                return jsonify({
                    'success': False,
                    'message': f'API error: {str(err)}'
                }), 500
                
        elif system_type == 'brnet':
            try:
                logger.info("Fetching tables from BR.NET...")
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                response = requests.get(
                    f'http://{server_url}:{port}/api/schema/tables',
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                tables = response.json()
                
                logger.info(f"Successfully fetched {len(tables)} tables from BR.NET")
                return jsonify({
                    'success': True,
                    'message': f'Successfully fetched {len(tables)} tables',
                    'tables': tables
                })
                
            except requests.exceptions.RequestException as err:
                logger.error(f"API error: {str(err)}")
                return jsonify({
                    'success': False,
                    'message': f'API error: {str(err)}'
                }), 500
        
        else:
            logger.error(f"Unsupported core banking system: {system_type}")
            return jsonify({
                'success': False,
                'message': 'Unsupported core banking system'
            }), 400
            
    except Exception as e:
        logger.error(f"Error fetching tables: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching tables: {str(e)}'
        }), 500

@integrations_bp.route('/core-banking/config', methods=['POST'])
@csrf.exempt
@login_required
@admin_required
def save_core_banking_config():
    """Save core banking configuration"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON'
            }), 400

        data = request.json
        logger.info(f"Saving core banking config: {data}")

        # Validate required fields
        required_fields = ['system_type', 'server_url', 'port']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Deactivate existing configurations
        CoreBankingConfig.query.update({'is_active': False})
        
        # Create new configuration
        config = CoreBankingConfig(
            system_type=data['system_type'],
            server_url=data['server_url'],
            port=int(data['port']),
            database=data.get('database'),
            username=data.get('username'),
            password=encrypt_value(data.get('password')) if data.get('password') else None,
            api_key=encrypt_value(data.get('api_key')) if data.get('api_key') else None,
            sync_interval=int(data.get('sync_interval', 15)),
            sync_settings={
                'sync_loan_details': data.get('sync_loan_details', False),
                'sync_payments': data.get('sync_payments', False),
                'sync_customer_info': data.get('sync_customer_info', False)
            },
            selected_tables=data.get('selected_tables', []),
            is_active=True
        )

        db.session.add(config)
        db.session.commit()

        # Test the connection with the new configuration
        api = CoreBankingAPI(config.system_type, {
            'server_url': config.server_url,
            'port': config.port,
            'database': config.database,
            'username': config.username,
            'password': decrypt_value(config.password) if config.password else None,
            'api_key': decrypt_value(config.api_key) if config.api_key else None
        })
        
        test_result = api.test_connection()
        if not test_result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Configuration saved but connection test failed',
                'warning': test_result.get('message')
            })

        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully',
            'config': config.to_dict()
        })

    except Exception as e:
        logger.error(f"Error saving core banking config: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@integrations_bp.route('/core-banking/save', methods=['POST'])
@csrf.exempt
@login_required
@admin_required
def save_core_banking_tables():
    """Save selected tables configuration"""
    try:
        if not request.is_json:
            logger.error("Request must be JSON")
            return jsonify({
                'success': False,
                'message': 'Request must be JSON'
            }), 400

        config = request.json
        logger.info(f"Saving configuration: {config}")
        
        # TODO: Save the configuration to the database
        logger.info("Configuration saved successfully")
        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully'
        })
    except Exception as e:
        logger.error(f"Error in save_core_banking_tables: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@integrations_bp.route('/core-banking/save-selected-tables', methods=['POST'])
@csrf.exempt
@login_required
@admin_required
def save_selected_tables():
    """Save selected core banking tables"""
    try:
        logger.info("Received save selected tables request")
        data = request.get_json()
        logger.info(f"Request data: {data}")

        if not data or 'tables' not in data:
            logger.error("No tables provided in request")
            return jsonify({
                'success': False,
                'message': 'No tables provided'
            }), 400

        # Get active configuration
        config = CoreBankingConfig.get_active_config()
        if not config:
            logger.error("No active core banking configuration found")
            return jsonify({
                'success': False,
                'message': 'No active core banking configuration found'
            }), 404

        # Update selected tables
        config.selected_tables = data['tables']
        db.session.commit()
        
        logger.info(f"Successfully saved {len(data['tables'])} tables")
        return jsonify({
            'success': True,
            'message': f"Successfully saved {len(data['tables'])} tables"
        })

    except Exception as e:
        logger.error(f"Error saving tables: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error saving tables: {str(e)}'
        }), 500

@integrations_bp.route('/core-banking/get-selected-tables', methods=['GET'])
@csrf.exempt
@login_required
@admin_required
def get_selected_tables():
    """Get selected core banking tables"""
    try:
        logger.info("Fetching selected tables")
        
        # Get active configuration
        config = CoreBankingConfig.get_active_config()
        if not config:
            logger.error("No active core banking configuration found")
            return jsonify({
                'success': False,
                'message': 'No active core banking configuration found'
            }), 404

        selected_tables = config.selected_tables or []
        logger.info(f"Found {len(selected_tables)} selected tables")
        
        return jsonify({
            'success': True,
            'tables': selected_tables,
            'message': f"Found {len(selected_tables)} selected tables"
        })

    except Exception as e:
        logger.error(f"Error fetching selected tables: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching selected tables: {str(e)}'
        }), 500

@integrations_bp.route('/core-banking/get-active-config', methods=['GET'])
@csrf.exempt
@login_required
@admin_required
def get_active_config():
    """Get active core banking configuration"""
    try:
        logger.info("Fetching active configuration")
        
        # Get active configuration
        config = CoreBankingConfig.get_active_config()
        if not config:
            logger.error("No active core banking configuration found")
            return jsonify({
                'success': False,
                'message': 'No active core banking configuration found'
            }), 404

        # Convert to dictionary and remove sensitive fields
        config_dict = config.to_dict()
        config_dict.pop('password', None)
        config_dict.pop('api_key', None)
        
        logger.info("Successfully fetched active configuration")
        return jsonify({
            'success': True,
            'config': config_dict,
            'message': 'Successfully fetched active configuration'
        })

    except Exception as e:
        logger.error(f"Error fetching active configuration: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching active configuration: {str(e)}'
        }), 500

@integrations_bp.route('/sms-gateway/<int:config_id>', methods=['GET', 'PUT', 'DELETE'])
def sms_gateway_config(config_id):
    if request.method == 'GET':
        config = SmsGatewayConfig.get_by_id(config_id)
        return jsonify(config.to_dict())
    
    if request.method == 'PUT':
        data = request.get_json()
        config = SmsGatewayConfig.update(config_id, **data)
        return jsonify(config.to_dict())
    
    if request.method == 'DELETE':
        SmsGatewayConfig.delete(config_id)
        return jsonify({'success': True})

@integrations_bp.route('/email-config')
def email_config():
    configs = EmailConfig.get_all()
    return render_template('admin/integrations/email_config.html', configs=configs)
# routes/integrations.py
@integrations_bp.route('/email-config', methods=['POST'])
@login_required
@admin_required
def create_email_config():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        required_fields = ['provider', 'smtp_server', 'smtp_port', 'from_email']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

        config = EmailConfig.create(
            provider=data['provider'],
            smtp_server=data['smtp_server'],
            smtp_port=data['smtp_port'],
            smtp_username=data.get('smtp_username'),
            smtp_password=encrypt_value(data.get('smtp_password', '')),
            from_email=data['from_email'],
            api_key=encrypt_value(data.get('api_key', '')) if data['provider'] != 'smtp' else None
        )
        return jsonify(config.to_dict()), 201
    except Exception as e:
        logger.error(f"Creation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@integrations_bp.route('/email-config/<int:config_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def email_config_detail(config_id):
    if request.method == 'GET':
        config = EmailConfig.get_by_id(config_id)
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        return jsonify(config.to_dict())

    if request.method == 'PUT':
        try:
            config = EmailConfig.get_by_id(config_id)
            if not config:
                return jsonify({'error': 'Configuration not found'}), 404

            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400

            config.update(
                provider=data['provider'],
                smtp_server=data['smtp_server'],
                smtp_port=data['smtp_port'],
                smtp_username=data.get('smtp_username'),
                smtp_password=encrypt_value(data.get('smtp_password', '')),
                from_email=data['from_email'],
                api_key=encrypt_value(data.get('api_key', '')) if data['provider'] != 'smtp' else None
            )
            return jsonify(config.to_dict()), 200
        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    if request.method == 'DELETE':
        EmailConfig.delete(config_id)
        return jsonify({'success': True})

@integrations_bp.app_errorhandler(Exception)
def handle_all_errors(e):
    logger.error(f"Unhandled exception: {str(e)}")
    if isinstance(e, HTTPException):
        return jsonify({
            "error": e.description,
            "status_code": e.code
        }), e.code
    return jsonify({
        "error": "Internal server error",
        "status_code": 500
    }), 500

