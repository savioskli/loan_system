from flask import Flask
from extensions import db, init_extensions
import logging
from models.role import Role
from models.staff import Staff

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_debug_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/loan_system'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # Log all SQL queries
    init_extensions(app)
    return app

def check_database():
    try:
        # Check roles table
        logger.info("Checking roles table...")
        roles = Role.query.all()
        logger.info(f"Found {len(roles)} roles")
        for role in roles:
            logger.info(f"Role: {role.name}, ID: {role.id}, Active: {role.is_active}")
            logger.info(f"Created by: {role.created_by}, Updated by: {role.updated_by}")
            
        # Check staff table
        logger.info("\nChecking staff table...")
        staff = Staff.query.all()
        logger.info(f"Found {len(staff)} staff members")
        for s in staff:
            logger.info(f"Staff: {s.email}, Role ID: {s.role_id}")
            
        # Check foreign key relationships
        logger.info("\nChecking staff-role relationships...")
        staff_with_invalid_roles = Staff.query.filter(
            ~Staff.role_id.in_(db.session.query(Role.id))
        ).all()
        if staff_with_invalid_roles:
            logger.error(f"Found {len(staff_with_invalid_roles)} staff with invalid role IDs")
            for s in staff_with_invalid_roles:
                logger.error(f"Staff {s.email} has invalid role_id: {s.role_id}")
                
    except Exception as e:
        logger.error(f"Error during database check: {str(e)}", exc_info=True)

if __name__ == '__main__':
    app = create_debug_app()
    with app.app_context():
        check_database()
