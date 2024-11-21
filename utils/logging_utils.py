from flask import request, current_app
from models.activity_log import ActivityLog
from extensions import db
from datetime import datetime
import traceback

def log_activity(user_id, action, details=None):
    """
    Log user activity in the system.
    
    Args:
        user_id (int): ID of the user performing the action
        action (str): Type of action performed
        details (str, optional): Additional details about the action
    """
    try:
        current_app.logger.info(f"Creating activity log: user={user_id}, action={action}")
        
        # Create new activity log entry
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr
        )
        current_app.logger.info("Activity object created")
        
        # Explicitly begin a new transaction
        db.session.begin(nested=True)
        
        # Add and commit in a try block
        try:
            db.session.add(activity)
            current_app.logger.info("Activity added to session")
            db.session.commit()
            current_app.logger.info(f"Activity logged successfully: {action} by user {user_id}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error while logging activity: {str(e)}\n{traceback.format_exc()}")
            raise
            
    except Exception as e:
        current_app.logger.error(f"Failed to log activity: {str(e)}\n{traceback.format_exc()}")
        # Re-raise the exception to ensure we know if logging fails
        raise
