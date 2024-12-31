import mysql.connector
from config import db_config

def create_tables():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Create core_banking_systems table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_banking_systems (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            base_url VARCHAR(255) NOT NULL,
            port INT,
            description TEXT,
            auth_type VARCHAR(50),
            auth_credentials JSON,
            headers JSON,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)

        # Create core_banking_endpoints table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_banking_endpoints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            system_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            endpoint VARCHAR(255) NOT NULL,
            method VARCHAR(10) NOT NULL,
            description TEXT,
            request_schema JSON,
            response_schema JSON,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (system_id) REFERENCES core_banking_systems(id)
        )
        """)

        # Create core_banking_logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_banking_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            system_id INT NOT NULL,
            endpoint_id INT NOT NULL,
            request_method VARCHAR(10) NOT NULL,
            request_url TEXT NOT NULL,
            request_headers JSON,
            request_body TEXT,
            response_status INT,
            response_body TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (system_id) REFERENCES core_banking_systems(id),
            FOREIGN KEY (endpoint_id) REFERENCES core_banking_endpoints(id)
        )
        """)

        conn.commit()
        print("Core banking tables created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
