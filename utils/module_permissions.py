from models.module_role_access import ModuleRoleAccess
from flask_login import current_user

def check_module_access(module_id, access_type):
    """
    Check if the current user has the specified access type for a module.
    
    Args:
        module_id (int): The ID of the module to check
        access_type (str): The type of access to check ('create', 'read', 'update', 'delete')
    
    Returns:
        bool: True if user has access, False otherwise
    """
    if not current_user or not current_user.is_authenticated:
        return False
        
    # Admin users have full access to all modules
    if hasattr(current_user, 'role') and current_user.role and current_user.role.name.lower() == 'admin':
        return True
        
    # Get user's role
    if not hasattr(current_user, 'role') or not current_user.role:
        return False
        
    # Check if user has the required permission
    access = ModuleRoleAccess.query.filter_by(
        role_id=current_user.role.id,
        module_id=module_id
    ).first()
    
    if access:
        if access_type == 'create' and access.can_create:
            return True
        elif access_type == 'read' and access.can_read:
            return True
        elif access_type == 'update' and access.can_update:
            return True
        elif access_type == 'delete' and access.can_delete:
            return True
    
    return False

def get_accessible_modules(access_type='read'):
    """
    Get all modules that the current user has the specified access type for.
    
    Args:
        access_type (str): The type of access to check ('create', 'read', 'update', 'delete')
    
    Returns:
        list: List of module IDs that the user has access to
    """
    from models.module import Module
    
    if not current_user or not current_user.is_authenticated:
        return []
        
    # Admin users have access to all modules
    if hasattr(current_user, 'role') and current_user.role and current_user.role.name.lower() == 'admin':
        # Return all active module IDs
        return [module.id for module in Module.query.filter_by(is_active=True).all()]
        
    accessible_modules = set()
    if not hasattr(current_user, 'role') or not current_user.role:
        return list(accessible_modules)
        
    accesses = ModuleRoleAccess.query.filter_by(role_id=current_user.role.id).all()
    
    for access in accesses:
        if access_type == 'create' and access.can_create:
            accessible_modules.add(access.module_id)
        elif access_type == 'read' and access.can_read:
            accessible_modules.add(access.module_id)
        elif access_type == 'update' and access.can_update:
            accessible_modules.add(access.module_id)
        elif access_type == 'delete' and access.can_delete:
            accessible_modules.add(access.module_id)
                
    return list(accessible_modules)
