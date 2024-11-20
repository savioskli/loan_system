from flask import request, current_app
from models.activity_log import ActivityLog
from extensions import db
from datetime import datetime

def log_activity(user_id, action, details=None):
    """
    Log user activity in the system.
    
    Args:
        user_id (int): ID of the user performing the action
        action (str): Type of action performed
        details (str, optional): Additional details about the action
    """
    try:
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr,
            timestamp=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        current_app.logger.info(f"Activity logged: {action} by user {user_id}")
    except Exception as e:
        db.session.rollback()
        # Log the error but don't raise it to avoid disrupting the main application flow
        current_app.logger.error(f"Failed to log activity: {str(e)}", exc_info=True)
