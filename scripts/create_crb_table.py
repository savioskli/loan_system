import mysql.connector
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_crb_table():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'loan_system')
        )

        cursor = connection.cursor()

        # Create crb_reports table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS crb_reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            national_id VARCHAR(20) NOT NULL,
            report_data JSON,
            status VARCHAR(20) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            error_message TEXT,
            credit_score INT,
            report_reference VARCHAR(100),
            INDEX idx_national_id (national_id),
            INDEX idx_status (status),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        cursor.execute(create_table_query)
        connection.commit()
        print("CRB reports table created successfully!")

        # Create sample data for testing
        sample_data = [
            {
                'national_id': '12345678',
                'status': 'completed',
                'credit_score': 750,
                'report_reference': 'CRB-2025-001',
                'report_data': json.dumps({
                    'creditScore': 750,
                    'reportReference': 'CRB-2025-001',
                    'summary': {
                        'accounts': 3,
                        'negativeListings': 0,
                        'positiveListings': 3
                    }
                })
            },
            {
                'national_id': '87654321',
                'status': 'completed',
                'credit_score': 550,
                'report_reference': 'CRB-2025-002',
                'report_data': json.dumps({
                    'creditScore': 550,
                    'reportReference': 'CRB-2025-002',
                    'summary': {
                        'accounts': 2,
                        'negativeListings': 1,
                        'positiveListings': 1
                    }
                })
            }
        ]

        # Insert sample data
        insert_query = """
        INSERT INTO crb_reports 
        (national_id, status, credit_score, report_reference, report_data)
        VALUES (%(national_id)s, %(status)s, %(credit_score)s, %(report_reference)s, %(report_data)s)
        """

        for data in sample_data:
            cursor.execute(insert_query, data)

        connection.commit()
        print("Sample data inserted successfully!")

    except mysql.connector.Error as error:
        print(f"Failed to create table in MySQL: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    create_crb_table()
