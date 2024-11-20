from app import app, db
from models.staff import Staff

def update_roles():
    with app.app_context():
        # Update all roles to proper case
        Staff.query.filter_by(role='admin').update({Staff.role: 'Admin'})
        Staff.query.filter_by(role='staff').update({Staff.role: 'Staff'})
        db.session.commit()

        # Print all users and their roles for verification
        users = Staff.query.all()
        print("\nUpdated user roles:")
        for user in users:
            print(f"Username: {user.username}, Role: {user.role}")

if __name__ == '__main__':
    update_roles()
