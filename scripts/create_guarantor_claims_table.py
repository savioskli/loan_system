import mysql.connector
from config import db_config

def create_guarantor_claims_table():
    """Create the guarantor_claims table if it doesn't exist."""
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database='loan_system',
            auth_plugin=db_config['auth_plugin']
        )
        cursor = conn.cursor()

        # Create guarantor_claims table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS guarantor_claims (
            id INT AUTO_INCREMENT PRIMARY KEY,
            loan_id VARCHAR(50) NOT NULL,
            loan_no VARCHAR(50) NOT NULL,
            borrower_id VARCHAR(50) NOT NULL,
            borrower_name VARCHAR(255) NOT NULL,
            guarantor_id VARCHAR(50) NOT NULL,
            guarantor_name VARCHAR(255) NOT NULL,
            claim_amount DECIMAL(15,2) NOT NULL,
            claim_date DATE NOT NULL,
            status ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending',
            notes TEXT,
            document_path TEXT,
            created_by INT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_by INT,
            updated_at DATETIME,
            INDEX idx_loan_id (loan_id),
            INDEX idx_guarantor_id (guarantor_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        conn.commit()
        print("Guarantor claims table created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_guarantor_claims_table()
