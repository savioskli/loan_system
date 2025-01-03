"""
Core banking models for managing external banking system integrations
"""
from extensions import db
from datetime import datetime
import json
from utils.encryption import encrypt_value, decrypt_value
import mysql.connector

class CoreBankingSystem(db.Model):
    """Model for storing core banking system configurations"""
    __tablename__ = 'core_banking_systems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    base_url = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text)
    auth_type = db.Column(db.String(20), nullable=False)  # none, basic, bearer, api_key, oauth2
    auth_credentials = db.Column(db.Text)  # Encrypted JSON string
    headers = db.Column(db.Text)  # JSON string
    database_name = db.Column(db.String(100))  # Name of the database to use
    selected_tables = db.Column(db.Text)  # JSON string of selected tables and their configurations
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    endpoints = db.relationship('CoreBankingEndpoint', backref='system', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('CoreBankingLog', backref='system', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(CoreBankingSystem, self).__init__(**kwargs)
        if isinstance(self.headers, dict):
            self.headers = json.dumps(self.headers)
        if isinstance(self.auth_credentials, dict):
            self.auth_credentials = encrypt_value(json.dumps(self.auth_credentials))
        if isinstance(self.selected_tables, dict):
            self.selected_tables = json.dumps(self.selected_tables)

    @property
    def headers_dict(self):
        """Get headers as dictionary"""
        if not self.headers:
            return {}
        return json.loads(self.headers)

    @property
    def auth_credentials_dict(self):
        """Get auth credentials as dictionary"""
        if not self.auth_credentials:
            return {}
        decrypted = decrypt_value(self.auth_credentials)
        return json.loads(decrypted) if decrypted else {}

    @property
    def selected_tables_dict(self):
        """Get selected tables as dictionary"""
        if not self.selected_tables:
            return {}
        return json.loads(self.selected_tables)

    def get_auth_headers(self):
        """Generate authentication headers based on auth type"""
        if not self.auth_type or self.auth_type == 'none':
            return {}

        auth_creds = self.auth_credentials_dict
        headers = {}

        if self.auth_type == 'basic':
            import base64
            if 'username' in auth_creds and 'password' in auth_creds:
                auth_string = f"{auth_creds['username']}:{auth_creds['password']}"
                auth_bytes = auth_string.encode('ascii')
                base64_bytes = base64.b64encode(auth_bytes)
                base64_string = base64_bytes.decode('ascii')
                headers['Authorization'] = f'Basic {base64_string}'

        elif self.auth_type == 'bearer':
            if 'token' in auth_creds:
                headers['Authorization'] = f"Bearer {auth_creds['token']}"

        elif self.auth_type == 'api_key':
            if 'key_name' in auth_creds and 'key_value' in auth_creds:
                headers[auth_creds['key_name']] = auth_creds['key_value']

        elif self.auth_type == 'oauth2':
            # OAuth2 implementation would typically involve token management
            if 'access_token' in auth_creds:
                headers['Authorization'] = f"Bearer {auth_creds['access_token']}"

        return headers

    def validate_auth_credentials(self):
        """Validate authentication credentials based on auth type"""
        if not self.auth_type or self.auth_type == 'none':
            return True

        auth_creds = self.auth_credentials_dict
        
        if self.auth_type == 'basic':
            return all(k in auth_creds for k in ['username', 'password'])
            
        elif self.auth_type == 'bearer':
            return 'token' in auth_creds
            
        elif self.auth_type == 'api_key':
            return all(k in auth_creds for k in ['key_name', 'key_value'])
            
        elif self.auth_type == 'oauth2':
            return all(k in auth_creds for k in ['client_id', 'client_secret', 'token_url'])
            
        return False

    def get_database_connection(self):
        """Get a connection to the core banking database"""
        auth_creds = self.auth_credentials_dict
        try:
            connection = mysql.connector.connect(
                host=self.base_url,
                port=self.port,
                user=auth_creds.get('username'),
                password=auth_creds.get('password')
            )
            return connection
        except mysql.connector.Error as err:
            raise Exception(f"Failed to connect to database: {str(err)}")

    def list_databases(self):
        """List all available databases"""
        connection = self.get_database_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            return databases
        finally:
            connection.close()

    def list_tables(self):
        """List all tables in the selected database"""
        if not self.database_name:
            raise Exception("No database selected")

        connection = self.get_database_connection()
        try:
            connection.database = self.database_name
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            return tables
        finally:
            connection.close()

    def get_table_schema(self, table_name):
        """Get the schema for a specific table"""
        if not self.database_name:
            raise Exception("No database selected")

        connection = self.get_database_connection()
        try:
            connection.database = self.database_name
            cursor = connection.cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            schema = []
            for col in columns:
                schema.append({
                    'name': col[0],
                    'type': col[1],
                    'null': col[2],
                    'key': col[3],
                    'default': col[4],
                    'extra': col[5]
                })
            return schema
        finally:
            connection.close()

    def select_database(self, database_name):
        """Select a database to use"""
        if database_name not in self.list_databases():
            raise Exception(f"Database '{database_name}' does not exist")
        self.database_name = database_name
        db.session.commit()

    def configure_tables(self, table_configs):
        """Configure which tables to use and their mappings
        
        Args:
            table_configs (dict): Dictionary of table configurations
                Example: {
                    'customers': {
                        'name': 'customers',
                        'key_field': 'customer_id',
                        'mappings': {
                            'customer_id': 'id',
                            'customer_name': 'name',
                            'phone_number': 'phone'
                        }
                    }
                }
        """
        # Validate that all tables exist
        available_tables = self.list_tables()
        for table_name in table_configs:
            if table_name not in available_tables:
                raise Exception(f"Table '{table_name}' does not exist in database '{self.database_name}'")
            
            # Validate that mapped fields exist in the table
            schema = self.get_table_schema(table_name)
            schema_fields = [field['name'] for field in schema]
            
            for field in table_configs[table_name].get('mappings', {}).keys():
                if field not in schema_fields:
                    raise Exception(f"Field '{field}' does not exist in table '{table_name}'")

        self.selected_tables = json.dumps(table_configs)
        db.session.commit()

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'base_url': self.base_url,
            'port': self.port,
            'description': self.description,
            'auth_type': self.auth_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CoreBankingEndpoint(db.Model):
    """Model for storing core banking API endpoints"""
    __tablename__ = 'core_banking_endpoints'

    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('core_banking_systems.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)
    headers = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(CoreBankingEndpoint, self).__init__(**kwargs)
        if isinstance(self.parameters, dict):
            self.parameters = json.dumps(self.parameters)
        if isinstance(self.headers, dict):
            self.headers = json.dumps(self.headers)

    @property
    def parameters_dict(self):
        """Get parameters as dictionary"""
        if not self.parameters:
            return {}
        return json.loads(self.parameters)

    @property
    def headers_dict(self):
        """Get headers as dictionary"""
        if not self.headers:
            return {}
        return json.loads(self.headers)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'system_id': self.system_id,
            'name': self.name,
            'path': self.path,
            'method': self.method,
            'description': self.description,
            'parameters': self.parameters_dict,
            'headers': self.headers_dict,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CoreBankingLog(db.Model):
    """Model for logging core banking API requests and responses"""
    __tablename__ = 'core_banking_logs'

    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('core_banking_systems.id', ondelete='CASCADE'), nullable=False)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('core_banking_endpoints.id', ondelete='SET NULL'), nullable=True)
    request_method = db.Column(db.String(10), nullable=False)
    request_url = db.Column(db.String(255), nullable=False)
    request_headers = db.Column(db.Text)
    request_body = db.Column(db.Text)
    response_status = db.Column(db.Integer)
    response_headers = db.Column(db.Text)
    response_body = db.Column(db.Text)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    endpoint = db.relationship('CoreBankingEndpoint')

    def __init__(self, **kwargs):
        super(CoreBankingLog, self).__init__(**kwargs)
        if isinstance(self.request_headers, dict):
            self.request_headers = json.dumps(self.request_headers)
        if isinstance(self.response_headers, dict):
            self.response_headers = json.dumps(self.response_headers)
        if isinstance(self.request_body, dict):
            self.request_body = json.dumps(self.request_body)
        if isinstance(self.response_body, dict):
            self.response_body = json.dumps(self.response_body)

    @property
    def request_headers_dict(self):
        """Get request headers as dictionary"""
        if not self.request_headers:
            return {}
        return json.loads(self.request_headers)

    @property
    def response_headers_dict(self):
        """Get response headers as dictionary"""
        if not self.response_headers:
            return {}
        return json.loads(self.response_headers)

    @property
    def request_body_dict(self):
        """Get request body as dictionary"""
        if not self.request_body:
            return {}
        try:
            return json.loads(self.request_body)
        except json.JSONDecodeError:
            return {'raw': self.request_body}

    @property
    def response_body_dict(self):
        """Get response body as dictionary"""
        if not self.response_body:
            return {}
        try:
            return json.loads(self.response_body)
        except json.JSONDecodeError:
            return {'raw': self.response_body}

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'system_id': self.system_id,
            'endpoint_id': self.endpoint_id,
            'request_method': self.request_method,
            'request_url': self.request_url,
            'request_headers': self.request_headers_dict,
            'request_body': self.request_body_dict,
            'response_status': self.response_status,
            'response_headers': self.response_headers_dict,
            'response_body': self.response_body_dict,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
