from app import app, db
from models.staff import Staff

def create_admin_user():
    with app.app_context():
        # Check if admin already exists
        admin = Staff.query.filter_by(email='admin@example.com').first()
        if admin:
            print("Admin user already exists")
            return
        
        # Create admin user
        admin = Staff(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='admin123',  # This will be hashed by the model
            role='admin',
            is_active=True,
            branch_id=None  # Admin doesn't need a branch
        )
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")

if __name__ == '__main__':
    create_admin_user()
