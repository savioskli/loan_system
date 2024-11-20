from flask import Flask
from extensions import db, init_extensions
import logging
from models.role import Role
from models.staff import Staff
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/loan_system'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_extensions(app)
    return app

def fix_roles_v2():
    try:
        # Get admin user
        admin = Staff.query.filter_by(email='admin@example.com').first()
        if not admin:
            logger.error("Admin user not found!")
            return

        # Update existing roles
        roles = Role.query.all()
        for role in roles:
            # Convert role names to lowercase
            role.name = role.name.lower()
            
            # Set missing audit information
            if not role.created_by:
                role.created_by = admin.id
            if not role.updated_by:
                role.updated_by = admin.id
            if not role.created_at:
                role.created_at = datetime.utcnow()
            if not role.updated_at:
                role.updated_at = datetime.utcnow()

        # Standardize role names
        role_mapping = {
            'admin': 'Administrator role with full access',
            'credit officer': 'Manages loan applications and assessments',
            'branch manager': 'Manages branch operations and staff',
            'staff': 'Regular staff member with basic access'
        }

        # Update or create standard roles
        for role_name, description in role_mapping.items():
            role = Role.query.filter(Role.name.ilike(role_name)).first()
            if role:
                role.description = description
                role.is_active = True
                role.updated_by = admin.id
                role.updated_at = datetime.utcnow()
            else:
                new_role = Role(
                    name=role_name,
                    description=description,
                    is_active=True,
                    created_by=admin.id,
                    updated_by=admin.id
                )
                db.session.add(new_role)

        # Delete any roles not in our standard set
        standard_roles = [name.lower() for name in role_mapping.keys()]
        for role in Role.query.all():
            if role.name.lower() not in standard_roles:
                # Move any staff with this role to 'staff' role
                staff_role = Role.query.filter(Role.name.ilike('staff')).first()
                if staff_role:
                    Staff.query.filter_by(role_id=role.id).update({'role_id': staff_role.id})
                db.session.delete(role)

        # Commit changes
        db.session.commit()
        logger.info("Successfully fixed roles!")

        # Verify changes
        roles = Role.query.all()
        logger.info("\nCurrent roles:")
        for role in roles:
            logger.info(f"Role: {role.name}, ID: {role.id}, Active: {role.is_active}")
            logger.info(f"Description: {role.description}")
            logger.info(f"Created by: {role.created_by}, Updated by: {role.updated_by}")
            staff_count = Staff.query.filter_by(role_id=role.id).count()
            logger.info(f"Staff members with this role: {staff_count}\n")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error fixing roles: {str(e)}", exc_info=True)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        fix_roles_v2()
