from datetime import datetime
from typing import Optional
from models.progress_update import ProgressUpdate
from models.collection_schedule import CollectionSchedule
from extensions import db
from werkzeug.datastructures import FileStorage
import os

class ProgressUpdateService:
    @staticmethod
    def create_progress_update(
        collection_schedule_id: int,
        status: str,
        amount: Optional[float] = None,
        collection_method: Optional[str] = None,
        notes: Optional[str] = None,
        attachment: Optional[FileStorage] = None
    ) -> ProgressUpdate:
        # Verify collection schedule exists
        collection_schedule = CollectionSchedule.query.get(collection_schedule_id)
        if not collection_schedule:
            raise ValueError("Collection schedule not found")

        # Handle file upload if present
        attachment_url = None
        if attachment:
            filename = f"progress_update_{collection_schedule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{attachment.filename}"
            upload_dir = os.path.join(os.getcwd(), 'static', 'uploads', 'progress_updates')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            attachment.save(file_path)
            attachment_url = f"/static/uploads/progress_updates/{filename}"

        # Create progress update
        progress_update = ProgressUpdate(
            collection_schedule_id=collection_schedule_id,
            status=status,
            amount=amount,
            collection_method=collection_method,
            notes=notes,
            attachment_url=attachment_url
        )

        try:
            db.session.add(progress_update)
            db.session.commit()
            return progress_update
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_progress_updates(collection_schedule_id: int) -> list[ProgressUpdate]:
        return ProgressUpdate.query\
            .filter_by(collection_schedule_id=collection_schedule_id)\
            .order_by(ProgressUpdate.created_at.desc())\
            .all()
