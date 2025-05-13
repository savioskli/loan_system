from functools import wraps
from flask import request, g, current_app
from flask_login import current_user
from models.audit import AuditLog
import json

def log_audit_action(action_type, entity_type, entity_id=None, description=None):
    """
    Decorator to log audit actions for route functions.
    
    Args:
        action_type (str): Type of action (create, update, delete, view)
        entity_type (str): Type of entity being acted upon (loan, client, etc.)
        entity_id (int, optional): ID of the entity. If None, will try to extract from request.
        description (str, optional): Description of the action. If None, will use a default.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the result from the original function
            result = f(*args, **kwargs)
            
            try:
                # Determine entity_id if not provided
                _entity_id = entity_id
                if _entity_id is None and 'id' in kwargs:
                    _entity_id = kwargs['id']
                elif _entity_id is None and request.view_args and 'id' in request.view_args:
                    _entity_id = request.view_args['id']
                
                # Determine description if not provided
                _description = description
                if _description is None:
                    _description = f"{action_type.title()} {entity_type} {_entity_id if _entity_id else ''}"
                
                # Get IP address and user agent
                ip_address = request.remote_addr
                user_agent = request.user_agent.string if request.user_agent else None
                
                # Create audit log entry
                AuditLog.log_action(
                    action_type=action_type,
                    entity_type=entity_type,
                    entity_id=_entity_id,
                    description=_description,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
            except Exception as e:
                current_app.logger.error(f"Error logging audit action: {str(e)}")
            
            return result
        return decorated_function
    return decorator

def log_data_change(old_data, new_data, action_type, entity_type, entity_id, description=None):
    """
    Log a data change with before and after values.
    
    Args:
        old_data (dict): Previous state of the data
        new_data (dict): New state of the data
        action_type (str): Type of action (usually 'update')
        entity_type (str): Type of entity being acted upon
        entity_id (int): ID of the entity
        description (str, optional): Description of the change
    """
    try:
        if description is None:
            description = f"{action_type.title()} {entity_type} {entity_id}"
        
        # Get IP address and user agent
        ip_address = request.remote_addr
        user_agent = request.user_agent.string if request.user_agent else None
        
        # Create audit log entry with old and new values
        AuditLog.log_action(
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_value=old_data,
            new_value=new_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
    except Exception as e:
        current_app.logger.error(f"Error logging data change: {str(e)}")

def audit_middleware():
    """
    Middleware function to be called before each request to set up audit context.
    Can be used with app.before_request
    """
    g.audit_data = {}
    
    # Store original request data for comparison later
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            if request.is_json:
                g.audit_data['request_json'] = request.get_json()
            elif request.form:
                g.audit_data['request_form'] = {key: request.form[key] for key in request.form}
        except Exception as e:
            current_app.logger.error(f"Error in audit middleware: {str(e)}")
