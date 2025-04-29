import os
import os
import json
import requests
from flask import current_app
from models.crb_report import CRBReport
from extensions import db
from datetime import datetime

class CRBService:
    def __init__(self, bureau=None):
        # If bureau object is provided, use its credentials
        # Otherwise fall back to config values
        self.bureau = bureau
        
        if bureau and bureau.provider.lower() == 'metropol':
            # Store bureau credentials
            self.base_url = bureau.base_url
            self.api_key = bureau.api_key
            self.username = bureau.username
            self.password = bureau.password
        else:
            # Fall back to config values
            self.base_url = current_app.config.get('METROPOL_API_BASE_URL', 'https://api.metropol.co.ke')
            self.api_key = current_app.config.get('METROPOL_API_KEY')
            self.username = current_app.config.get('METROPOL_USERNAME')
            self.password = current_app.config.get('METROPOL_PASSWORD')
            
        # Log the credentials (masked for security)
        current_app.logger.info(f"CRBService initialized with: ")
        current_app.logger.info(f"  base_url: {self.base_url}")
        if self.api_key:
            current_app.logger.info(f"  api_key: {self.api_key[:5]}... (masked)")
        else:
            current_app.logger.warning("  api_key: MISSING")
            
        if self.username:
            current_app.logger.info(f"  username: {self.username}")
        else:
            current_app.logger.warning("  username: MISSING")
            
        if self.password:
            current_app.logger.info(f"  password: {'*' * 8} (masked)")
        else:
            current_app.logger.warning("  password: MISSING")
        
    def _validate_credentials(self):
        """Validate that all required credentials are present and not sample values"""
        if not self.base_url:
            current_app.logger.error("Metropol API base URL is missing")
            return False
        if not self.api_key:
            current_app.logger.error("Metropol API key is missing")
            return False
        if not self.username:
            current_app.logger.error("Metropol username is missing")
            return False
        if not self.password:
            current_app.logger.error("Metropol password is missing")
            return False
            
        # Check if using sample credentials
        if self.api_key == 'sample_api_key' or self.username == 'sample_username' or self.password == 'sample_password':
            current_app.logger.error("Using sample credentials. Please update with real Metropol API credentials.")
            raise ValueError("You are using sample credentials. Please update the credit bureau with real Metropol API credentials before generating CRB reports.")
            
        return True
    
    def _get_auth_token(self):
        """Get authentication token from Metropol API"""
        try:
            # Validate credentials first
            if not self._validate_credentials():
                raise ValueError("Invalid or missing credentials for Metropol API")
            # Log the authentication attempt
            current_app.logger.info(f"Attempting to authenticate with Metropol API: {self.base_url}/oauth/token")
            current_app.logger.info(f"Using credentials: username={self.username}, api_key={self.api_key[:5]}...")
            
            response = requests.post(
                f"{self.base_url}/oauth/token",
                data={
                    "username": self.username,
                    "password": self.password,
                    "grant_type": "password"
                },
                headers={
                    "Authorization": f"Basic {self.api_key}"
                },
                timeout=30  # Set a reasonable timeout
            )
            
            # Log the response status
            current_app.logger.info(f"Metropol authentication response status: {response.status_code}")
            
            # Check if the response is successful
            if response.status_code != 200:
                error_msg = f"Authentication failed with status code {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data}"
                except:
                    error_msg += f": {response.text}"
                current_app.logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Parse the response
            data = response.json()
            if 'access_token' not in data:
                error_msg = f"No access token in response: {data}"
                current_app.logger.error(error_msg)
                raise ValueError(error_msg)
                
            current_app.logger.info("Successfully authenticated with Metropol API")
            return data.get('access_token')
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error connecting to Metropol API: {str(e)}"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)
        except ValueError as e:
            # Re-raise ValueError exceptions
            raise
        except Exception as e:
            error_msg = f"Error getting Metropol auth token: {str(e)}"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)
            
    def generate_report(self, customer_data, report_type='full'):
        """Generate a CRB report for the given customer data"""
        report = None
        try:
            # Log the input data
            current_app.logger.info(f"CRBService.generate_report called with data: {customer_data}, report_type: {report_type}")
            
            # Check if bureau credentials are valid
            if not self._validate_credentials():
                error_msg = "Credit bureau credentials are invalid or missing"
                current_app.logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Extract customer information
            national_id = customer_data.get('national_id')
            customer_name = customer_data.get('customer_name', '')
            phone_number = customer_data.get('phone_number', '')
            email = customer_data.get('email', '')
            
            # Validate required fields
            if not national_id:
                raise ValueError("National ID is required")
                
            # Create initial report record
            report = CRBReport(
                national_id=national_id,
                status='pending'
            )
            db.session.add(report)
            db.session.commit()
            
            # Log the created report
            current_app.logger.info(f"Created pending CRB report with ID: {report.id}")
            
            # Write to debug log
            debug_log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'crb_debug.log')
            with open(debug_log_file, 'a') as f:
                f.write(f"=== {datetime.now()} - CRB Report Generation - ID: {report.id} ===\n")
                f.write(f"Customer Data: {customer_data}\n")
                f.write(f"Report Type: {report_type}\n")
                f.write(f"Bureau: {self.bureau.name if self.bureau else 'None'}\n")
            
            # Log the request
            current_app.logger.info(f"Generating CRB report for National ID: {national_id}")
            
            # Get auth token
            token = self._get_auth_token()
            
            # Map report type to Metropol report type
            metropol_report_type = "FULL"
            if report_type == 'summary':
                metropol_report_type = "SUMMARY"
            elif report_type == 'score_only':
                metropol_report_type = "SCORE_ONLY"
            
            # Prepare request payload
            payload = {
                "nationalId": national_id,
                "reportType": metropol_report_type,
                "reportFormat": "JSON"
            }
            
            # Add optional fields if available
            if customer_name:
                names = customer_name.split()
                if len(names) >= 2:
                    payload["firstName"] = names[0]
                    payload["lastName"] = names[-1]
                    if len(names) > 2:
                        payload["middleName"] = ' '.join(names[1:-1])
                        
            if phone_number:
                payload["phoneNumber"] = phone_number
                
            if email:
                payload["email"] = email
            
            # Log the payload
            current_app.logger.info(f"Metropol API request payload: {payload}")
            
            # Request credit report
            try:
                current_app.logger.info(f"Making API request to: {self.base_url}/v1/credit-report")
                
                response = requests.post(
                    f"{self.base_url}/v1/credit-report",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    timeout=30  # Set a reasonable timeout
                )
                
                # Log the response status
                current_app.logger.info(f"Metropol API response status: {response.status_code}")
                
                # Check if the response is successful
                if response.status_code != 200:
                    error_msg = f"API request failed with status code {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg += f": {error_data}"
                    except:
                        error_msg += f": {response.text}"
                    current_app.logger.error(error_msg)
                    raise ValueError(error_msg)
                    
                # Parse the response
                report_data = response.json()
                if not report_data:
                    error_msg = "Empty response from Metropol API"
                    current_app.logger.error(error_msg)
                    raise ValueError(error_msg)
                    
                # Log successful response
                current_app.logger.info(f"Successfully retrieved CRB report for National ID: {national_id}")
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Network error connecting to Metropol API: {str(e)}"
                current_app.logger.error(error_msg)
                raise ValueError(error_msg)
            except ValueError as e:
                # Re-raise ValueError exceptions
                raise
            except Exception as e:
                error_msg = f"Error calling Metropol API: {str(e)}"
                current_app.logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Update report record
            report.report_data = report_data
            report.status = 'completed'
            report.credit_score = report_data.get('creditScore')
            report.report_reference = report_data.get('reportReference')
            db.session.commit()
            
            return report
            
        except Exception as e:
            if report:
                report.status = 'failed'
                report.error_message = str(e)
                db.session.commit()
            current_app.logger.error(f"Error generating CRB report: {str(e)}")
            raise
            
    def get_report(self, report_id):
        """Retrieve a CRB report by ID"""
        return CRBReport.query.get_or_404(report_id)
        
    def get_reports(self, page=1, per_page=10):
        """Get paginated list of CRB reports"""
        return CRBReport.query.order_by(CRBReport.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
