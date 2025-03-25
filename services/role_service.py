from flask import current_app
from extensions import db
from models.role import Role
from models.staff import Staff
from typing import List, Optional, Tuple
from datetime import datetime

class RoleService:
    @staticmethod
    def list_roles() -> Tuple[List[Role], Optional[str]]:
        """
        Get all roles ordered by name
        Returns: Tuple of (list of roles, error message if any)
        """
        try:
            roles = Role.query.order_by(Role.name).all()
            return roles, None
        except Exception as e:
            current_app.logger.error(f'Error listing roles: {str(e)}')
            return [], None

    @staticmethod
    def create_role(name: str, description: str = None, is_active: bool = True, created_by: int = None) -> Tuple[Optional[Role], Optional[str]]:
        """
        Create a new role
        Returns: Tuple of (created role if successful, error message if any)
        """
        print("Starting create_role with:", {  # Debug print
            'name': name,
            'description': description,
            'is_active': is_active,
            'created_by': created_by
        })
        
        if not isinstance(is_active, bool):
            is_active = bool(is_active)
            
        try:
            # Basic validation
            if not name or not name.strip():
                return None, "Role name is required"
            
            name = name.strip()
            if len(name) < 2 or len(name) > 50:
                return None, "Role name must be between 2 and 50 characters"
            
            # Check for existing role with same name (case-insensitive)
            existing_role = Role.query.filter(Role.name.ilike(name)).first()
            if existing_role:
                return None, f"Role with name '{name}' already exists"
            
            # Create new role
            role = Role(
                name=name,
                description=description,
                is_active=is_active,
                created_by=created_by
            )
            
            db.session.add(role)
            db.session.commit()
            return role, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating role: {str(e)}')
            return None, str(e)

    @staticmethod
    def get_role(role_id: int) -> Tuple[Optional[Role], Optional[str]]:
        """
        Get a role by ID
        Returns: Tuple of (role if found, error message if any)
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                return None, "Role not found"
            return role, None
        except Exception as e:
            current_app.logger.error(f'Error getting role {role_id}: {str(e)}')
            return None, str(e)

    @staticmethod
    def update_role(role_id: int, name: str, description: str, is_active: bool, updated_by: int) -> Tuple[Optional[Role], Optional[str]]:
        """
        Update an existing role
        Returns: Tuple of (updated role if successful, error message if any)
        """
        try:
            print(f"Updating role {role_id} with name: {name}")  # Debug print
            
            # Get the role to update
            role = Role.query.get(role_id)
            if not role:
                print(f"Role {role_id} not found")  # Debug print
                return None, "Role not found"

            print(f"Current role name: {role.name}")  # Debug print

            # Basic validation
            if not name or not name.strip():
                return None, "Role name is required"
            
            name = name.strip()
            if len(name) < 2 or len(name) > 50:
                return None, "Role name must be between 2 and 50 characters"
            
            # Check for existing role with same name (case-insensitive), excluding current role
            existing_role = Role.query.filter(
                Role.name.ilike(name),
                Role.id != role_id
            ).first()
            
            print(f"Existing role check result: {existing_role}")  # Debug print
            if existing_role:
                print(f"Found existing role with name '{name}': ID={existing_role.id}")  # Debug print
                return None, "A role with this name already exists"

            # Update role
            print(f"Updating role {role_id} from '{role.name}' to '{name}'")  # Debug print
            role.name = name
            role.description = description.strip() if description else None
            role.is_active = is_active
            role.updated_by = updated_by
            role.updated_at = datetime.utcnow()

            db.session.commit()
            print(f"Successfully updated role: {role.name}")  # Debug print
            current_app.logger.info(f'Role updated: {role.name} by user ID {updated_by}')
            return role, None
            
        except Exception as e:
            print(f"Error updating role: {str(e)}")  # Debug print
            db.session.rollback()
            current_app.logger.error(f'Error updating role {role_id}: {str(e)}')
            return None, str(e)

    @staticmethod
    def delete_role(role_id: int) -> Optional[str]:
        """
        Delete a role by ID
        Returns: Error message if any, None if successful
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                return f"Role with ID {role_id} not found"
            
            # Check if role name is reserved
            if role.name.lower() in ['admin', 'administrator', 'superadmin']:
                return "Cannot delete system reserved roles"
            
            # Check if any staff members are using this role
            staff_count = Staff.query.filter_by(role_id=role_id).count()
            if staff_count > 0:
                return f"Cannot delete role '{role.name}' as it is assigned to {staff_count} staff member(s)"
            
            db.session.delete(role)
            db.session.commit()
            current_app.logger.info(f'Role deleted: {role.name}')
            return None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error deleting role {role_id}: {str(e)}')
            return str(e)
