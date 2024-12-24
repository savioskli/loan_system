import logging
from typing import Optional
from models.sms_template import SMSTemplate
from models.loan import Loan
from models.sms_log import SMSLog
from models.client import Client

class SMSService:
    def __init__(self, db_session, sms_provider):
        self.db = db_session
        self.sms_provider = sms_provider
        self.logger = logging.getLogger(__name__)

    def get_template(self, template_type: str, days_trigger: Optional[int] = None) -> Optional[SMSTemplate]:
        try:
            query = self.db.query(SMSTemplate).filter(
                SMSTemplate.template_type == template_type,
                SMSTemplate.is_active == True
            )
            if days_trigger is not None:
                query = query.filter(SMSTemplate.days_trigger == days_trigger)
            return query.first()
        except Exception as e:
            self.logger.error(f"Error getting template: {str(e)}")
            return None

    def substitute_variables(self, template_content: str, loan: Loan, client: Client) -> str:
        try:
            return template_content.format(
                client_name=client.name,
                amount=loan.installment_amount,
                account_number=client.account_number,
                support_number="1234567890",
                next_amount=loan.next_installment_amount,
                next_date=loan.next_installment_date,
                remaining_balance=loan.remaining_balance,
            )
        except KeyError as e:
            self.logger.error(f"Missing template variable: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error substituting variables: {str(e)}")
            raise

    def _is_valid_phone_number(self, phone_number: str) -> bool:
        # Add your phone number validation logic here
        return bool(phone_number and len(phone_number) >= 10)

    def send_sms(self, template_type: str, loan_id: int, days_trigger: Optional[int] = None) -> bool:
        try:
            loan = self.db.query(Loan).get(loan_id)
            if not loan:
                self.logger.error(f"Loan not found: {loan_id}")
                return False

            if not loan.client.phone_number:
                self.logger.error(f"Client has no phone number: {loan.client.id}")
                return False

            if not self._is_valid_phone_number(loan.client.phone_number):
                self.logger.error(f"Invalid phone number: {loan.client.phone_number}")
                return False

            template = self.get_template(template_type, days_trigger)
            if not template:
                self.logger.error(f"Template not found: {template_type}, days_trigger: {days_trigger}")
                return False
            
            message = self.substitute_variables(template.content, loan, loan.client)
            
            try:
                response = self.sms_provider.send(
                    to=loan.client.phone_number,
                    message=message
                )
            except Exception as e:
                self.logger.error(f"SMS provider error: {str(e)}")
                response.success = False
            
            sms_log = SMSLog(
                template_id=template.id,
                loan_id=loan.id,
                recipient=loan.client.phone_number,
                message=message,
                status='sent' if response.success else 'failed'
            )
            self.db.add(sms_log)
            self.db.commit()
            
            return response.success
        except Exception as e:
            self.logger.error(f"Error sending SMS: {str(e)}")
            self.db.rollback()
            return False