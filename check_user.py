from app import app, db, Staff, generate_password_hash, check_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_user_credentials(username, password):
    user = Staff.query.filter_by(username=username).first()
    
    if user:
        logger.info(f"Found user: {username}")
        logger.info(f"User active status: {user.is_active}")
        logger.info(f"User role: {user.role}")
        logger.debug(f"Stored password hash: {user.password_hash}")
        
        # Check if password matches
        if check_password_hash(user.password_hash, password):
            logger.info("Password verification successful!")
            return True
        else:
            logger.info("Password verification failed!")
            return False
    else:
        logger.info(f"No user found with username: {username}")
        return False

# Check the specific user
username = "savioskli"
password = "124124"

with app.app_context():
    print(f"\nChecking credentials for user: {username}")
    result = check_user_credentials(username, password)
    print(f"Login would be: {'successful' if result else 'failed'}")
