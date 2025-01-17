from models.letter_template import LetterTemplate
from models.client import Client
from models.loan import Loan

class LetterTemplateGenerator:
    @staticmethod
    def generate_letter(template_id, client_id, loan_id=None):
        """
        Generate a letter from a template with dynamic placeholders
        
        :param template_id: ID of the letter template
        :param client_id: ID of the client
        :param loan_id: Optional loan ID for loan-specific details
        :return: Rendered letter content
        """
        # Fetch the template
        template = LetterTemplate.query.get_or_404(template_id)
        
        # Fetch client details
        client = Client.query.get_or_404(client_id)
        
        # Prepare placeholders
        placeholders = {
            'member_name': f"{client.first_name} {client.last_name}",
            'member_number': client.member_number or 'N/A',
            'account_no': client.account_number or 'N/A',
            'email': client.email or 'N/A',
            'phone': client.phone_number or 'N/A'
        }
        
        # If loan is provided, add loan-specific details
        if loan_id:
            loan = Loan.query.get(loan_id)
            if loan:
                placeholders.update({
                    'loan_amount': f"{loan.principal_amount:,.2f}",
                    'amount_outstanding': f"{loan.outstanding_balance:,.2f}",
                    'loan_purpose': loan.purpose or 'N/A',
                    'loan_status': loan.status or 'N/A'
                })
        
        # Replace placeholders in template
        letter_content = template.template_content.format(**placeholders)
        
        return letter_content

    @staticmethod
    def list_available_placeholders():
        """
        List all available placeholders for letter templates
        """
        return [
            # Client Placeholders
            '{member_name}', 
            '{member_number}', 
            '{account_no}', 
            '{email}', 
            '{phone}',
            
            # Loan Placeholders
            '{loan_amount}', 
            '{amount_outstanding}', 
            '{loan_purpose}', 
            '{loan_status}'
        ]
