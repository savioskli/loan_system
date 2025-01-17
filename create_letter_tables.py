import mysql.connector
from config import db_config

def create_letter_tables():
    # Establish connection
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    try:
        # Create letter_types table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS letter_types (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
        """)

        # Create letter_templates table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS letter_templates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            letter_type_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            template_content TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (letter_type_id) REFERENCES letter_types(id) ON DELETE CASCADE
        )
        """)

        # Insert initial letter types if not exists
        cursor.execute("""
        INSERT IGNORE INTO letter_types (name, description) VALUES 
        ('Demand Letter', 'Letter sent for loan repayment'),
        ('Approval Letter', 'Loan approval communication'),
        ('Rejection Letter', 'Loan rejection notification'),
        ('Reminder Letter', 'Loan payment reminder')
        """)

        # Commit changes
        connection.commit()
        print("Letter types and templates tables created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()

    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()

if __name__ == '__main__':
    create_letter_tables()
