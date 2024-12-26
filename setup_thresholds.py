import mysql.connector
from datetime import datetime
from config import db_config  # Import database configuration

# SQL for creating the thresholds table
create_table_sql = """
CREATE TABLE IF NOT EXISTS thresholds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    npl_ratio FLOAT NOT NULL COMMENT 'Non-Performing Loan Ratio (%)',
    coverage_ratio FLOAT NOT NULL COMMENT 'Coverage Ratio (%)',
    par_ratio FLOAT NOT NULL COMMENT 'Portfolio at Risk Ratio (%)',
    cost_of_risk FLOAT NOT NULL COMMENT 'Cost of Risk (%)',
    recovery_rate FLOAT NOT NULL COMMENT 'Recovery Rate (%)',
    valid_from DATETIME NOT NULL,
    valid_to DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# Default threshold values
default_threshold = {
    'npl_ratio': 5.0,
    'coverage_ratio': 100.0,
    'par_ratio': 10.0,
    'cost_of_risk': 2.0,
    'recovery_rate': 90.0,
    'valid_from': datetime.utcnow(),
    'valid_to': None,
    'is_active': True
}

def setup_database():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create the table
        print("Creating thresholds table...")
        cursor.execute(create_table_sql)

        # Insert default threshold
        insert_sql = """
        INSERT INTO thresholds (
            npl_ratio, coverage_ratio, par_ratio, cost_of_risk, recovery_rate, 
            valid_from, valid_to, is_active
        ) VALUES (
            %(npl_ratio)s, %(coverage_ratio)s, %(par_ratio)s, %(cost_of_risk)s, 
            %(recovery_rate)s, %(valid_from)s, %(valid_to)s, %(is_active)s
        )
        """
        
        print("Inserting default threshold values...")
        cursor.execute(insert_sql, default_threshold)

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
