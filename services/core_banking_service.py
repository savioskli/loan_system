"""
Core banking service for managing banking operations
"""
from .config_manager import ConfigManager
from .api_manager import APIManager
from models.core_banking import CoreBankingSystem, CoreBankingEndpoint, CoreBankingLog
from extensions import db

class CoreBankingService:
    def __init__(self, system_id):
        """Initialize core banking service"""
        self.system_id = system_id
        self.config_manager = ConfigManager()
        self.api_manager = APIManager(system_id)

    def get_account_balance(self, account_id, endpoint_id):
        """Get account balance"""
        try:
            return self.api_manager.get(endpoint_id, params={'account_id': account_id})
        except Exception as e:
            raise Exception(f"Failed to get account balance: {str(e)}")

    def get_transaction_history(self, account_id, start_date, end_date, endpoint_id):
        """Get transaction history"""
        try:
            params = {
                'account_id': account_id,
                'start_date': start_date,
                'end_date': end_date
            }
            return self.api_manager.get(endpoint_id, params=params)
        except Exception as e:
            raise Exception(f"Failed to get transaction history: {str(e)}")

    def make_transfer(self, from_account, to_account, amount, currency, endpoint_id, reference=None):
        """Make a funds transfer"""
        try:
            data = {
                'from_account': from_account,
                'to_account': to_account,
                'amount': amount,
                'currency': currency,
                'reference': reference
            }
            return self.api_manager.post(endpoint_id, json=data)
        except Exception as e:
            raise Exception(f"Failed to make transfer: {str(e)}")

    def get_exchange_rate(self, from_currency, to_currency, endpoint_id):
        """Get exchange rate"""
        try:
            params = {
                'from_currency': from_currency,
                'to_currency': to_currency
            }
            return self.api_manager.get(endpoint_id, params=params)
        except Exception as e:
            raise Exception(f"Failed to get exchange rate: {str(e)}")

    def get_loan_status(self, loan_id, endpoint_id):
        """Get loan status"""
        try:
            return self.api_manager.get(endpoint_id, params={'loan_id': loan_id})
        except Exception as e:
            raise Exception(f"Failed to get loan status: {str(e)}")

    def create_loan(self, customer_id, amount, term, endpoint_id, **kwargs):
        """Create a new loan"""
        try:
            data = {
                'customer_id': customer_id,
                'amount': amount,
                'term': term,
                **kwargs
            }
            return self.api_manager.post(endpoint_id, json=data)
        except Exception as e:
            raise Exception(f"Failed to create loan: {str(e)}")

    def make_loan_payment(self, loan_id, amount, endpoint_id, payment_method=None):
        """Make a loan payment"""
        try:
            data = {
                'loan_id': loan_id,
                'amount': amount,
                'payment_method': payment_method
            }
            return self.api_manager.post(endpoint_id, json=data)
        except Exception as e:
            raise Exception(f"Failed to make loan payment: {str(e)}")

    def get_customer_info(self, customer_id, endpoint_id):
        """Get customer information"""
        try:
            return self.api_manager.get(endpoint_id, params={'customer_id': customer_id})
        except Exception as e:
            raise Exception(f"Failed to get customer info: {str(e)}")

    def update_customer_info(self, customer_id, endpoint_id, **kwargs):
        """Update customer information"""
        try:
            data = {
                'customer_id': customer_id,
                **kwargs
            }
            return self.api_manager.put(endpoint_id, json=data)
        except Exception as e:
            raise Exception(f"Failed to update customer info: {str(e)}")

    def get_system_status(self, endpoint_id):
        """Get core banking system status"""
        try:
            return self.api_manager.get(endpoint_id)
        except Exception as e:
            raise Exception(f"Failed to get system status: {str(e)}")

    def get_request_logs(self, endpoint_id=None, start_date=None, end_date=None, status=None):
        """Get API request logs"""
        try:
            query = CoreBankingLog.query.filter_by(system_id=self.system_id)
            
            if endpoint_id:
                query = query.filter_by(endpoint_id=endpoint_id)
            if status:
                query = query.filter_by(response_status=status)
            if start_date:
                query = query.filter(CoreBankingLog.created_at >= start_date)
            if end_date:
                query = query.filter(CoreBankingLog.created_at <= end_date)
            
            return query.order_by(CoreBankingLog.created_at.desc()).all()
        except Exception as e:
            raise Exception(f"Failed to get request logs: {str(e)}")

    def get_active_endpoints(self):
        """Get all active endpoints for the system"""
        try:
            return CoreBankingEndpoint.query.filter_by(
                system_id=self.system_id,
                is_active=True
            ).all()
        except Exception as e:
            raise Exception(f"Failed to get active endpoints: {str(e)}")

    def validate_endpoint_schema(self, endpoint_id, data, schema_type='request'):
        """Validate request/response data against endpoint schema"""
        try:
            endpoint = CoreBankingEndpoint.query.get(endpoint_id)
            if not endpoint:
                raise Exception("Endpoint not found")

            schema = (endpoint.request_schema_dict if schema_type == 'request' 
                     else endpoint.response_schema_dict)
            
            if not schema:
                return True  # No schema to validate against
            
            from jsonschema import validate
            validate(instance=data, schema=schema)
            return True
        except Exception as e:
            raise Exception(f"Schema validation failed: {str(e)}")
