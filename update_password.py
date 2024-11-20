from app import db, Staff, app
from werkzeug.security import generate_password_hash

def update_user_password():
    try:
        with app.app_context():
            user = Staff.query.filter_by(username='savioskli').first()
            if user:
                user.password_hash = generate_password_hash('123123')
                db.session.commit()
                print("Password updated successfully for user savioskli")
            else:
                print("User savioskli not found")
    except Exception as e:
        print(f"Error updating password: {str(e)}")

if __name__ == '__main__':
    update_user_password()
