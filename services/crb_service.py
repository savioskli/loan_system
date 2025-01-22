import requests
from flask import current_app
from models.crb_report import CRBReport
from extensions import db
import json

class CRBService:
    def __init__(self):
        self.base_url = current_app.config.get('METROPOL_API_BASE_URL', 'https://api.metropol.co.ke')
        self.api_key = current_app.config.get('METROPOL_API_KEY')
        self.username = current_app.config.get('METROPOL_USERNAME')
        self.password = current_app.config.get('METROPOL_PASSWORD')
        
    def _get_auth_token(self):
        """Get authentication token from Metropol API"""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                data={
                    "username": self.username,
                    "password": self.password,
                    "grant_type": "password"
                },
                headers={
                    "Authorization": f"Basic {self.api_key}"
                }
            )
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            current_app.logger.error(f"Error getting Metropol auth token: {str(e)}")
            raise
            
    def generate_report(self, national_id):
        """Generate a CRB report for the given national ID"""
        try:
            # Create initial report record
            report = CRBReport(national_id=national_id)
            db.session.add(report)
            db.session.commit()
            
            # Get auth token
            token = self._get_auth_token()
            
            # Request credit report
            response = requests.post(
                f"{self.base_url}/v1/credit-report",
                json={
                    "nationalId": national_id,
                    "reportType": "INDIVIDUAL",
                    "reportFormat": "JSON"
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            report_data = response.json()
            
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
