import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from models.notification import GuarantorNotification, NotificationAttachment, NotificationRecipient
from database import get_db
from werkzeug.utils import secure_filename

class NotificationService:
    @staticmethod
    def create_notification(
        customer_id: str,
        customer_name: str,
        account_no: str,
        notification_type: str,
        notification_category: str,
        message: str,
        guarantor_ids: List[str],
        created_by: int,
        attachments: Optional[List[dict]] = None,
        db: Session = next(get_db())
    ) -> GuarantorNotification:
        """Create a new notification with recipients and attachments"""
        try:
            # Create notification
            notification = GuarantorNotification(
                customer_id=customer_id,
                customer_name=customer_name,
                account_no=account_no,
                notification_type=notification_type,
                notification_category=notification_category,
                message=message,
                created_by=created_by
            )
            db.add(notification)
            db.flush()

            # Add recipients
            for guarantor_id in guarantor_ids:
                # Get guarantor details from mock core banking
                guarantor = NotificationService.get_guarantor_details(guarantor_id)
                if guarantor:
                    recipient = NotificationRecipient(
                        notification_id=notification.id,
                        guarantor_id=guarantor_id,
                        guarantor_name=guarantor['name'],
                        phone_number=guarantor.get('phone_no'),
                        email=guarantor.get('email')
                    )
                    db.add(recipient)

            # Add attachments if any
            if attachments:
                for attachment_data in attachments:
                    attachment = NotificationAttachment(
                        file_name=secure_filename(attachment_data['filename']),
                        file_path=attachment_data['filepath'],
                        file_type=attachment_data['filetype'],
                        uploaded_by=created_by
                    )
                    notification.attachments.append(attachment)

            db.commit()
            return notification
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_notification(notification_id: int, db: Session = next(get_db())) -> Optional[GuarantorNotification]:
        """Get a notification by ID"""
        return db.query(GuarantorNotification).filter(GuarantorNotification.id == notification_id).first()

    @staticmethod
    def get_notifications_by_customer(customer_id: str, db: Session = next(get_db())) -> List[GuarantorNotification]:
        """Get all notifications for a customer"""
        return db.query(GuarantorNotification).filter(GuarantorNotification.customer_id == customer_id).all()

    @staticmethod
    def get_notifications_by_guarantor(guarantor_id: str, db: Session = next(get_db())) -> List[GuarantorNotification]:
        """Get all notifications for a guarantor"""
        return (
            db.query(GuarantorNotification)
            .join(NotificationRecipient)
            .filter(NotificationRecipient.guarantor_id == guarantor_id)
            .all()
        )

    @staticmethod
    def send_notification(notification_id: int, db: Session = next(get_db())) -> bool:
        """Send the notification to all recipients"""
        try:
            notification = NotificationService.get_notification(notification_id, db)
            if not notification:
                return False

            success = True
            for recipient in notification.recipients:
                try:
                    if notification.notification_type in ['SMS', 'Both'] and recipient.phone_number:
                        # TODO: Implement SMS sending
                        pass

                    if notification.notification_type in ['Email', 'Both'] and recipient.email:
                        # TODO: Implement email sending
                        pass

                    recipient.is_sent = True
                    recipient.sent_at = datetime.utcnow()
                except Exception as e:
                    success = False
                    recipient.error_message = str(e)

            notification.status = 'Sent' if success else 'Failed'
            notification.sent_at = datetime.utcnow()
            db.commit()
            return success
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_guarantor_details(guarantor_id: str) -> Optional[dict]:
        """Get guarantor details from mock core banking"""
        # TODO: Implement actual API call to mock core banking
        # For now, return mock data
        return {
            'id': guarantor_id,
            'name': 'John Doe',
            'phone_no': '+254700000000',
            'email': 'john@example.com'
        }

    @staticmethod
    def save_attachment(file, uploaded_by: int, db: Session = next(get_db())) -> NotificationAttachment:
        """Save an uploaded file as an attachment"""
        try:
            filename = secure_filename(file.filename)
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), 'uploads', 'notifications')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Create attachment record
            attachment = NotificationAttachment(
                file_name=filename,
                file_path=file_path,
                file_type=file_type,
                uploaded_by=uploaded_by
            )
            db.add(attachment)
            db.commit()
            
            return attachment
        except Exception as e:
            db.rollback()
            raise e
