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
            try:
                print("Checking for existing role with name:", name)  # Debug print
                existing_role = Role.query.filter(Role.name.ilike(name)).first()
                print("Existing role query result:", existing_role)  # Debug print
                if existing_role:
                    return None, "A role with this name already exists"
            except Exception as e:
                print(f"Database error while checking existing role: {str(e)}")  # Debug print
                print(f"Error type: {type(e)}")  # Debug print
                import traceback
                print(f"Traceback: {traceback.format_exc()}")  # Debug print
                return None, f"Database error: {str(e)}"

            # Create new role
            try:
                print("Creating new role object")  # Debug print
                role = Role(
                    name=name,
                    description=description.strip() if description else None,
                    is_active=is_active,
                    created_by=created_by
                )
                
                print("Adding role to session")  # Debug print
                db.session.add(role)
                print("Committing session")  # Debug print
                db.session.commit()
                print("Role created successfully:", role.name)  # Debug print
                return role, None
                
            except Exception as e:
                print(f"Database error while creating role: {str(e)}")  # Debug print
                print(f"Error type: {type(e)}")  # Debug print
                import traceback
                print(f"Traceback: {traceback.format_exc()}")  # Debug print
                db.session.rollback()
                return None, f"Database error: {str(e)}"
            
        except Exception as e:
            print(f"Unexpected error in create_role: {str(e)}")  # Debug print
            print(f"Error type: {type(e)}")  # Debug print
            import traceback
            print(f"Traceback: {traceback.format_exc()}")  # Debug print
            if db.session.is_active:
                db.session.rollback()
            return None, f"Error creating role: {str(e)}"

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
            
            db.session.delete(role)
            db.session.commit()
            current_app.logger.info(f'Role deleted: {role.name}')
            return None
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error deleting role {role_id}: {str(e)}')
            return str(e)
