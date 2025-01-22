import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_credit_bureau_table():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'loan_system')
        )

        cursor = connection.cursor()

        # Create credit_bureaus table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS credit_bureaus (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            provider VARCHAR(50) NOT NULL,
            base_url VARCHAR(255) NOT NULL,
            api_key VARCHAR(255) NOT NULL,
            username VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_provider (provider),
            INDEX idx_is_active (is_active)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        cursor.execute(create_table_query)
        connection.commit()
        print("Credit bureaus table created successfully!")

        # Add sample Metropol configuration
        sample_config = {
            'name': 'Metropol CRB',
            'provider': 'metropol',
            'base_url': 'https://api.metropol.co.ke',
            'api_key': 'sample_api_key',
            'username': 'sample_username',
            'password': 'sample_password',
            'is_active': True
        }

        # Insert sample configuration
        insert_query = """
        INSERT INTO credit_bureaus 
        (name, provider, base_url, api_key, username, password, is_active)
        VALUES (%(name)s, %(provider)s, %(base_url)s, %(api_key)s, %(username)s, %(password)s, %(is_active)s)
        """

        cursor.execute(insert_query, sample_config)
        connection.commit()
        print("Sample configuration added successfully!")

    except mysql.connector.Error as error:
        print(f"Failed to create table in MySQL: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    create_credit_bureau_table()
