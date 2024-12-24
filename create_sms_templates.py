import mysql.connector
from mysql.connector import Error

def create_sms_templates_table():
    connection = None
    cursor = None
    try:
        # Database configuration
        config = {
            'host': 'localhost',  # or your MySQL host
            'user': 'root',       # your MySQL username
            'password': '',       # your MySQL password
            'database': 'loan_system'  # your database name
        }

        # Create connection
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Drop table if exists
        drop_table_query = "DROP TABLE IF EXISTS sms_templates;"
        cursor.execute(drop_table_query)
        connection.commit()
        
        # Create the table
        create_table_query = """
        CREATE TABLE sms_templates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            days_trigger INT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_type_days (type, days_trigger)
        );
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        print("SMS templates table created successfully")

        # Optional: Insert some sample templates
        sample_templates = [
            ("LOAN_APPROVED", "Dear {client_name}, your loan of KES {amount} has been approved. Account: {account_number}. For support call {support_number}", None),
            ("PAYMENT_REMINDER", "Dear {client_name}, your loan payment of KES {next_amount} is due on {next_date}. Current balance: KES {remaining_balance}", 3),
            ("PAYMENT_OVERDUE", "Dear {client_name}, your loan payment of KES {next_amount} is overdue. Please pay to avoid penalties. For support call {support_number}", -1)
        ]

        insert_query = """
        INSERT INTO sms_templates (type, content, days_trigger)
        VALUES (%s, %s, %s)
        """
        
        cursor.executemany(insert_query, sample_templates)
        connection.commit()
        print("Sample templates inserted successfully")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_sms_templates_table()