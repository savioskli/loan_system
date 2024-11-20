from models.user import User
from models.role import Role
from extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime

class UserService:
    @staticmethod
    def get_all_users():
        """Get all users with their roles and branches."""
        return User.query.order_by(User.created_at.desc()).all()
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def create_user(user_data):
        """Create a new user with the provided data."""
        try:
            # Validate required fields
            required_fields = ['name', 'email', 'password', 'role_id']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    raise ValueError(f"Missing required field: {field}")
            
            # Hash the password
            hashed_password = generate_password_hash(user_data['password'])
            
            # Create new user
            new_user = User(
                name=user_data['name'].strip(),
                email=user_data['email'].lower().strip(),
                password_hash=hashed_password,
                role_id=user_data['role_id'],
                branch_id=user_data.get('branch_id'),  # This can be None
                status='active'
            )

            # Validate the user object
            if not new_user.name or not new_user.email:
                raise ValueError("Name and email are required")

            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def update_user(user_id, data):
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            # Update user information
            user.name = data['name']
            user.email = data['email']
            
            # Update password if provided
            if data.get('password'):
                user.password_hash = generate_password_hash(data['password'])
            
            # Update role if provided
            if data.get('role_id'):
                role = Role.query.get(data['role_id'])
                if not role:
                    return False, "Selected role not found"
                user.role_id = data['role_id']
            
            # Update branch if provided
            if data.get('branch_id'):
                user.branch_id = data['branch_id']
            
            # Update status if provided
            if data.get('is_active') is not None:
                user.status = 'active' if data['is_active'] else 'inactive'
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True, "User updated successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def delete_user(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            db.session.delete(user)
            db.session.commit()
            return True, "User deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def change_user_status(user_id, status):
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            user.status = status
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True, f"User status changed to {status}"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
