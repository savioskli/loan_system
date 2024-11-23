from extensions import db
from app import create_app
from sqlalchemy import text

def check_table():
    try:
        app = create_app()
        with app.app_context():
            with db.engine.connect() as connection:
                # Show table structure
                result = connection.execute(text("DESCRIBE system_settings"))
                print("\nTable structure:")
                for row in result:
                    print(row)
                
                # Show existing data
                result = connection.execute(text("SELECT * FROM system_settings"))
                print("\nExisting data:")
                for row in result:
                    print(row)
                
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    check_table()
