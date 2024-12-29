import mysql.connector
from datetime import datetime
from config import db_config  # Import database configuration

# SQL for creating the collection_schedules table
create_table_sql = """
CREATE TABLE IF NOT EXISTS collection_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    loan_id INT NOT NULL,
    schedule_date DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL COMMENT 'scheduled, completed, missed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id),
    FOREIGN KEY (loan_id) REFERENCES loans(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

def setup_database():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create the table
        print("Creating collection_schedules table...")
        cursor.execute(create_table_sql)

        # Commit the changes
        conn.commit()
        print("Database setup completed successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database()
