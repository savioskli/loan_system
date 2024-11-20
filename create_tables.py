from app import app, db
from models.role import Role
from models.user import User
from datetime import datetime

def create_default_roles():
    # Check if admin role exists
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(
            name='Admin',
            description='System Administrator with full access',
            permissions={'all': True},
            is_active=True
        )
        db.session.add(admin_role)
    
    # Check if user role exists
    user_role = Role.query.filter_by(name='User').first()
    if not user_role:
        user_role = Role(
            name='User',
            description='Standard user with basic access',
            permissions={'view': True, 'submit': True},
            is_active=True
        )
        db.session.add(user_role)
    
    try:
        db.session.commit()
        print("Default roles created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default roles: {e}")

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
    
    # Create default roles
    create_default_roles()
