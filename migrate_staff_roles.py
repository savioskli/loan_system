from app import create_app
from extensions import db
from models.staff import Staff
from models.role import Role

def migrate_staff_roles():
    app = create_app()
    with app.app_context():
        # Get all staff members
        staff_members = Staff.query.all()
        
        # Create a mapping of role names to role IDs
        roles = Role.query.all()
        role_map = {role.name.lower(): role.id for role in roles}
        
        # Ensure we have at least a default role
        default_role = Role.query.filter_by(name='staff').first()
        if not default_role:
            default_role = Role(name='staff', description='Default staff role')
            db.session.add(default_role)
            db.session.commit()
            role_map['staff'] = default_role.id
        
        # Update each staff member's role
        for staff in staff_members:
            old_role = getattr(staff, 'role', 'staff').lower()
            staff.role_id = role_map.get(old_role, role_map['staff'])
        
        db.session.commit()
        print("Staff roles migration completed successfully!")

if __name__ == '__main__':
    migrate_staff_roles()
