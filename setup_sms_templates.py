import mysql.connector
from datetime import datetime
from config import db_config  # Import database configuration

# SQL for creating the sms_templates table
create_table_sql = """
CREATE TABLE IF NOT EXISTS sms_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_value INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# Sample templates
sample_templates = [
    {
        'name': 'Payment Due Reminder',
        'category': 'payment',
        'message': 'Dear {customer_name}, your loan payment of {amount_due} for loan {loan_id} is due on {due_date}. Please ensure timely payment to maintain a good credit record.',
        'trigger_type': 'days_before',
        'trigger_value': 3
    },
    {
        'name': 'Payment Overdue Notice',
        'category': 'overdue',
        'message': 'Dear {customer_name}, your loan payment of {amount_due} for loan {loan_id} is overdue by {days_overdue} days. Please make the payment immediately to avoid additional charges.',
        'trigger_type': 'days_after',
        'trigger_value': 1
    },
    {
        'name': 'High NPL Alert',
        'category': 'alert',
        'message': 'Alert: NPL Ratio has exceeded threshold. Current value: {npl_ratio}%. Please review loan portfolio immediately.',
        'trigger_type': 'threshold',
        'trigger_value': 5
    }
]

def setup_database():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create the table
        print("Creating sms_templates table...")
        cursor.execute(create_table_sql)

        # Insert sample templates
        insert_sql = """
        INSERT INTO sms_templates (name, category, message, trigger_type, trigger_value)
        VALUES (%(name)s, %(category)s, %(message)s, %(trigger_type)s, %(trigger_value)s)
        """
        
        print("Inserting sample templates...")
        for template in sample_templates:
            cursor.execute(insert_sql, template)

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
