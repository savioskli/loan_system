import requests
from flask import current_app
from models import db
from models.guarantor import Guarantor
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import xlsxwriter
from datetime import datetime

class GuarantorService:
    @staticmethod
    def get_guarantors_by_customer(client_no):
        """Fetch guarantors from mock core banking system"""
        try:
            response = requests.get(f"{current_app.config['CORE_BANKING_URL']}/api/guarantors/{client_no}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error fetching guarantors: {str(e)}")
            return None

    @staticmethod
    def sync_guarantors(client_no):
        """Sync guarantors from core banking to local database"""
        guarantors_data = GuarantorService.get_guarantors_by_customer(client_no)
        if not guarantors_data:
            return False

        try:
            # Delete existing guarantors for this customer
            Guarantor.query.filter_by(customer_no=client_no).delete()

            # Add new guarantors
            for guarantor_data in guarantors_data:
                guarantor = Guarantor(
                    guarantor_no=guarantor_data['guarantor_no'],
                    customer_no=client_no,
                    name=guarantor_data['name'],
                    id_no=guarantor_data['id_no'],
                    phone_no=guarantor_data['phone_no'],
                    email=guarantor_data['email'],
                    relationship=guarantor_data['relationship'],
                    occupation=guarantor_data['occupation'],
                    monthly_income=guarantor_data['monthly_income'],
                    status=guarantor_data['status']
                )
                db.session.add(guarantor)

            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error syncing guarantors: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def create_guarantor(data):
        """Create a new guarantor"""
        try:
            guarantor = Guarantor(
                guarantor_no=f"GRT{datetime.now().strftime('%Y%m%d%H%M%S')}",
                customer_no=data['customer_id'],
                name=data['name'],
                id_no=data['id_no'],
                phone_no=data['phone_no'],
                email=data.get('email'),
                relationship=data['relationship'],
                occupation=data['occupation'],
                monthly_income=float(data['monthly_income']),
                status='Active'
            )
            db.session.add(guarantor)
            db.session.commit()
            return guarantor
        except Exception as e:
            current_app.logger.error(f"Error creating guarantor: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def update_guarantor(guarantor_no, data):
        """Update guarantor information"""
        try:
            guarantor = Guarantor.query.filter_by(guarantor_no=guarantor_no).first()
            if not guarantor:
                return False

            guarantor.name = data['name']
            guarantor.id_no = data['id_no']
            guarantor.phone_no = data['phone_no']
            guarantor.email = data.get('email')
            guarantor.relationship = data['relationship']
            guarantor.occupation = data['occupation']
            guarantor.monthly_income = float(data['monthly_income'])

            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error updating guarantor: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def update_status(guarantor_no, status, reason):
        """Update guarantor status"""
        try:
            guarantor = Guarantor.query.filter_by(guarantor_no=guarantor_no).first()
            if not guarantor:
                return False

            guarantor.status = status
            # You might want to store the reason in a status history table
            
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error updating guarantor status: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def generate_pdf_report(guarantor_no):
        """Generate PDF report for guarantor"""
        try:
            guarantor = Guarantor.query.filter_by(guarantor_no=guarantor_no).first()
            if not guarantor:
                return None

            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            
            # Add content to PDF
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, 750, "Guarantor Details Report")
            
            p.setFont("Helvetica", 12)
            y = 700
            for label, value in [
                ("Guarantor Number:", guarantor.guarantor_no),
                ("Name:", guarantor.name),
                ("ID Number:", guarantor.id_no),
                ("Phone:", guarantor.phone_no),
                ("Email:", guarantor.email or "N/A"),
                ("Relationship:", guarantor.relationship),
                ("Occupation:", guarantor.occupation),
                ("Monthly Income:", f"KES {guarantor.monthly_income:,.2f}"),
                ("Status:", guarantor.status),
            ]:
                p.drawString(50, y, label)
                p.drawString(200, y, str(value))
                y -= 25

            p.save()
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            current_app.logger.error(f"Error generating PDF: {str(e)}")
            return None

    @staticmethod
    def generate_excel_report(client_no):
        """Generate Excel report for customer's guarantors"""
        try:
            guarantors = Guarantor.query.filter_by(customer_no=client_no).all()
            
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()

            # Add headers
            headers = ['Guarantor No', 'Name', 'ID Number', 'Phone', 'Email', 
                      'Relationship', 'Occupation', 'Monthly Income', 'Status']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            # Add data
            for row, guarantor in enumerate(guarantors, start=1):
                worksheet.write(row, 0, guarantor.guarantor_no)
                worksheet.write(row, 1, guarantor.name)
                worksheet.write(row, 2, guarantor.id_no)
                worksheet.write(row, 3, guarantor.phone_no)
                worksheet.write(row, 4, guarantor.email or "N/A")
                worksheet.write(row, 5, guarantor.relationship)
                worksheet.write(row, 6, guarantor.occupation)
                worksheet.write(row, 7, guarantor.monthly_income)
                worksheet.write(row, 8, guarantor.status)

            workbook.close()
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            current_app.logger.error(f"Error generating Excel report: {str(e)}")
            return None

    @staticmethod
    def get_all_guarantors():
        """Get all guarantors from local database"""
        return Guarantor.query.all()

    @staticmethod
    def get_guarantor_by_no(guarantor_no):
        """Get specific guarantor by number"""
        try:
            # First get all guarantors and find the matching one
            response = requests.get('http://localhost:5003/api/guarantors/search')
            if response.status_code == 200:
                guarantors = response.json()
                return next((g for g in guarantors if g['id_no'] == guarantor_no), None)
            return None
        except Exception as e:
            current_app.logger.error(f"Error fetching guarantor: {str(e)}")
            return None

    @staticmethod
    def get_customer_guarantors(client_no):
        """Get all guarantors for a specific customer"""
        try:
            response = requests.get(f'http://localhost:5003/api/guarantors/{client_no}')
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            current_app.logger.error(f"Error fetching guarantors: {str(e)}")
            return []
