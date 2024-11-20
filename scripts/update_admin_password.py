from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text
import sys

# Database connection
engine = create_engine('mysql://root@localhost/loan_system')

# New password
new_password = "admin123"  # You can change this to any password you prefer
password_hash = generate_password_hash(new_password)

# Update the password
with engine.connect() as connection:
    connection.execute(
        text("UPDATE staff SET password_hash = :password WHERE email = 'admin@example.com'"),
        {"password": password_hash}
    )
    connection.commit()

print(f"Password updated successfully for admin@example.com")
print(f"New password is: {new_password}")
