from models.staff import Staff
from extensions import db
from datetime import datetime

class StaffService:
    @staticmethod
    def get_all_staff():
        """Get all staff members with their roles and branches."""
        return Staff.query.order_by(Staff.created_at.desc()).all()
    
    @staticmethod
    def get_staff_by_id(staff_id):
        """Get a staff member by ID."""
        return Staff.query.get(staff_id)
    
    @staticmethod
    def create_staff(staff_data):
        """Create a new staff member with the provided data."""
        try:
            # Validate required fields
            required_fields = ['email', 'first_name', 'last_name', 'password', 'role_id']
            for field in required_fields:
                if field not in staff_data or not staff_data[field]:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create new staff member
            new_staff = Staff(
                email=staff_data['email'].lower().strip(),
                first_name=staff_data['first_name'].strip(),
                last_name=staff_data['last_name'].strip(),
                password=staff_data['password'],
                role_id=staff_data['role_id'],
                phone=staff_data.get('phone', '').strip() or None,
                branch_id=staff_data.get('branch_id'),
                is_active=staff_data.get('is_active', True)
            )

            db.session.add(new_staff)
            db.session.commit()
            return new_staff
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to create staff member: {str(e)}")
    
    @staticmethod
    def update_staff(staff_id, data):
        """Update a staff member's information."""
        try:
            staff = Staff.query.get(staff_id)
            if not staff:
                return False, "Staff member not found"
            
            # Update staff information
            if 'first_name' in data:
                staff.first_name = data['first_name'].strip()
            if 'last_name' in data:
                staff.last_name = data['last_name'].strip()
            if 'email' in data:
                staff.email = data['email'].lower().strip()
            if 'phone' in data:
                staff.phone = data['phone'].strip() or None
            if 'branch_id' in data:
                staff.branch_id = data['branch_id']
            if 'role_id' in data:
                staff.role_id = data['role_id']
            if 'is_active' in data:
                staff.is_active = data['is_active']
            if 'password' in data:
                staff.set_password(data['password'])
            
            db.session.commit()
            return True, "Staff member updated successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to update staff member: {str(e)}"
