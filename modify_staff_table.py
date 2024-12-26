import mysql.connector
from datetime import datetime
from config import db_config  # Import database configuration

# SQL for modifying the staff table
alter_table_sql = """
ALTER TABLE staff
ADD COLUMN last_login TIMESTAMP NULL DEFAULT NULL;
"""

def modify_staff_table():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Add the last_login column
        print("Adding last_login column to staff table...")
        cursor.execute(alter_table_sql)

        # Commit the changes
        conn.commit()
        print("Staff table modification completed successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if err.errno == 1060:  # Duplicate column error
            print("The last_login column already exists in the staff table.")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    modify_staff_table()