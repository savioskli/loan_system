from extensions import db
from models.branch import Branch
from app import create_app
from sqlalchemy import text

def add_is_active_column():
    try:
        app = create_app()
        # Add is_active column if it doesn't exist
        with app.app_context():
            with db.engine.connect() as connection:
                # Check if column exists
                result = connection.execute(text(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = 'loan_system' "
                    "AND TABLE_NAME = 'branches' "
                    "AND COLUMN_NAME = 'is_active'"
                ))
                column_exists = result.scalar() > 0

                if not column_exists:
                    connection.execute(text("ALTER TABLE branches ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                    print("Successfully added is_active column to branches table")
                else:
                    print("is_active column already exists")
                
                # Update all existing records to have is_active = True
                connection.execute(text("UPDATE branches SET is_active = TRUE WHERE is_active IS NULL"))
                print("Successfully updated existing records")
                connection.commit()
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    add_is_active_column()
