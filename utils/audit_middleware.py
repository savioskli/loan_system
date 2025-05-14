from flask import request, g, current_app, session
from flask_login import current_user
from models.audit import AuditLog
import json
import re

# Patterns to identify sensitive routes that should be audited
SENSITIVE_PATTERNS = [
    # Loan-related actions
    r'/loans/\d+/(edit|update|delete)',
    r'/loans/create',
    r'/loans/\d+/status',
    r'/loans/\d+/disburse',
    
    # Repayment actions
    r'/repayments/create',
    r'/repayments/\d+/(edit|delete)',
    
    # Field visits
    r'/field-visits/\d+/(edit|complete|delete)',
    r'/field-visits/create',
    
    # User/staff management
    r'/users/\d+/(edit|delete|activate|deactivate)',
    r'/users/create',
    r'/roles/\d+/(edit|delete)',
    r'/roles/create',
    
    # System settings
    r'/settings',
    r'/system-settings',
    
    # Client management
    r'/clients/\d+/(edit|delete)',
    r'/clients/create',
    
    # Post-disbursement modules
    r'/post-disbursement/modules/\d+/(edit|delete|toggle_hide)',
    r'/post-disbursement/modules/create',
    
    # Guarantor and collateral
    r'/guarantors/\d+/(edit|delete)',
    r'/guarantors/create',
    r'/collateral/\d+/(edit|delete)',
    r'/collateral/create',
]

def init_audit_middleware(app):
    """Initialize the audit middleware for the Flask app"""
    
    @app.before_request
    def before_request():
        """Store original request data for comparison later"""
        g.audit_data = {}
        
        # Only store data for non-GET requests to avoid excessive logging
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            try:
                # Store the path for pattern matching
                g.audit_data['path'] = request.path
                
                # Store request data
                if request.is_json:
                    g.audit_data['request_json'] = request.get_json()
                elif request.form:
                    g.audit_data['request_form'] = {key: request.form[key] for key in request.form}
                    
                # Check if this is a sensitive route that should be audited
                g.audit_data['should_audit'] = any(re.match(pattern, request.path) for pattern in SENSITIVE_PATTERNS)
                
            except Exception as e:
                current_app.logger.error(f"Error in audit middleware: {str(e)}")
    
    @app.after_request
    def after_request(response):
        """Log audit data after the request if needed"""
        try:
            # Only proceed if we should audit this request
            if hasattr(g, 'audit_data') and g.audit_data.get('should_audit', False):
                path = g.audit_data.get('path', '')
                
                # Determine action type based on request method and path
                action_type = 'view'
                if request.method == 'POST' and ('create' in path or path.endswith('/new')):
                    action_type = 'create'
                elif request.method in ['PUT', 'PATCH', 'POST'] and ('edit' in path or 'update' in path):
                    action_type = 'update'
                elif request.method == 'DELETE' or 'delete' in path:
                    action_type = 'delete'
                
                # Determine entity type from the path
                entity_type = 'unknown'
                entity_id = None
                
                # Extract entity type and ID from path
                path_parts = path.strip('/').split('/')
                if len(path_parts) >= 1:
                    # The first part is usually the entity type (loans, clients, etc.)
                    entity_type = path_parts[0]
                    # Remove trailing 's' if present (loans -> loan)
                    if entity_type.endswith('s'):
                        entity_type = entity_type[:-1]
                
                # Try to extract entity ID
                if len(path_parts) >= 2:
                    try:
                        entity_id = int(path_parts[1])
                    except (ValueError, TypeError):
                        pass
                
                # Create a description
                description = f"{action_type.title()} {entity_type} {entity_id if entity_id else ''}"                
                
                # Get request data
                request_data = {}
                if 'request_json' in g.audit_data:
                    request_data = g.audit_data['request_json']
                elif 'request_form' in g.audit_data:
                    request_data = g.audit_data['request_form']
                
                # Create audit log entry
                user_id = current_user.id if current_user and current_user.is_authenticated else None
                
                AuditLog.log_action(
                    action_type=action_type,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    description=description,
                    new_value=request_data,  # Store request data as new_value
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string if request.user_agent else None
                )
                
        except Exception as e:
            current_app.logger.error(f"Error in audit after_request: {str(e)}")
            
        return response
