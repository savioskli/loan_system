from extensions import db
from models.role import Role
from models.staff import Staff
from datetime import datetime
from flask import Flask
from extensions import init_extensions

def fix_roles():
    try:
        # First, check if we have any staff members
        admin_staff = Staff.query.filter(Staff.role_id.isnot(None)).first()
        admin_id = admin_staff.id if admin_staff else None

        # Create default roles if they don't exist
        default_roles = {
            'admin': 'Administrator role with full access',
            'staff': 'Default staff role'
        }
        
        created_roles = []
        for role_name, description in default_roles.items():
            role = Role.query.filter(Role.name.ilike(role_name)).first()
            if not role:
                role = Role(
                    name=role_name,
                    description=description,
                    is_active=True,
                    created_by=admin_id,
                )
                db.session.add(role)
                created_roles.append(role)
        
        if created_roles:
            db.session.flush()  # Get IDs for created roles
            print("Default roles created successfully")

        # Get the staff role for default assignments
        staff_role = Role.query.filter(Role.name.ilike('staff')).first()
        admin_role = Role.query.filter(Role.name.ilike('admin')).first()

        # Fix any staff members without role_id
        if staff_role:
            staff_without_role = Staff.query.filter(Staff.role_id.is_(None)).all()
            for staff in staff_without_role:
                staff.role_id = staff_role.id

            # If we don't have any admin, assign the first staff member as admin
            admin_exists = Staff.query.filter(Staff.role_id == admin_role.id).first() if admin_role else None
            if not admin_exists and staff_without_role:
                staff_without_role[0].role_id = admin_role.id
                print(f"Assigned {staff_without_role[0].email} as admin")

        # Commit all changes
        db.session.commit()
        print(f"Fixed {len(staff_without_role) if 'staff_without_role' in locals() else 0} staff members without roles")

    except Exception as e:
        db.session.rollback()
        print(f"Error fixing roles: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/loan_system'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_extensions(app)
    
    with app.app_context():
        fix_roles()
