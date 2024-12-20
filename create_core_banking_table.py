import mysql.connector
from mysql.connector import Error

# Database connection parameters
DB_NAME = "loan_system"
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "3306"

def create_core_banking_table():
    conn = None
    cursor = None
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor()

        # Create the table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS core_banking_config (
            id INT AUTO_INCREMENT PRIMARY KEY,
            system_type VARCHAR(50) NOT NULL,
            server_url VARCHAR(255) NOT NULL,
            port INT NOT NULL,
            `database` VARCHAR(255),
            username VARCHAR(255),
            password VARCHAR(255),
            api_key VARCHAR(255),
            sync_interval INT NOT NULL DEFAULT 15,
            sync_settings JSON DEFAULT ('{}'),
            selected_tables JSON DEFAULT ('[]'),
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_table_sql)

        # Create index on is_active
        create_index_sql = """
        CREATE INDEX ix_core_banking_config_is_active 
        ON core_banking_config (is_active);
        """
        cursor.execute(create_index_sql)

        conn.commit()
        print("Core banking config table created successfully!")

    except Error as e:
        print(f"Error creating table: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    create_core_banking_table()
