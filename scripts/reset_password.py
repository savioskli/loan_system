from app import app, db
from models.staff import Staff

def reset_password():
    with app.app_context():
        user = Staff.query.filter_by(username='savioskli').first()
        if user:
            user.set_password('password123')
            db.session.commit()
            print(f"Password reset for user {user.username}")
        else:
            print("User not found")

if __name__ == '__main__':
    reset_password()
