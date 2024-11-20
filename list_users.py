from app import app, db, Staff

with app.app_context():
    users = Staff.query.all()
    print("\nRegistered users in the system:")
    print("-" * 50)
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Active: {user.is_active}")
        print("-" * 50)
