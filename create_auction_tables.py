import mysql.connector
from mysql.connector import Error

def create_auction_tables():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='loan_system'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create auction table
            create_auction_table = """
            CREATE TABLE IF NOT EXISTS auction (
                id INT AUTO_INCREMENT PRIMARY KEY,
                loan_id VARCHAR(50) NOT NULL,
                client_name TEXT NOT NULL,
                property_description TEXT NOT NULL,
                property_type VARCHAR(100),
                valuation_amount DECIMAL(15,2) NOT NULL,
                reserve_price DECIMAL(15,2) NOT NULL,
                auction_date DATETIME NOT NULL,
                auction_venue TEXT,
                auctioneer_name VARCHAR(100),
                auctioneer_contact VARCHAR(100),
                advertisement_date DATE,
                advertisement_medium VARCHAR(100),
                status VARCHAR(20) DEFAULT 'Scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """

            # Create auction_attachment table
            create_attachment_table = """
            CREATE TABLE IF NOT EXISTS auction_attachment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                auction_id INT NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (auction_id) REFERENCES auction(id) ON DELETE CASCADE
            );
            """

            # Create auction_history table
            create_history_table = """
            CREATE TABLE IF NOT EXISTS auction_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                auction_id INT NOT NULL,
                action VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (auction_id) REFERENCES auction(id) ON DELETE CASCADE
            );
            """

            # Create auction_history_attachment table
            create_history_attachment_table = """
            CREATE TABLE IF NOT EXISTS auction_history_attachment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                history_id INT NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (history_id) REFERENCES auction_history(id) ON DELETE CASCADE
            );
            """

            # Execute the create table queries
            cursor.execute(create_auction_table)
            cursor.execute(create_attachment_table)
            cursor.execute(create_history_table)
            cursor.execute(create_history_attachment_table)

            # Create indexes
            cursor.execute("CREATE INDEX idx_auction_loan_id ON auction(loan_id);")
            cursor.execute("CREATE INDEX idx_auction_status ON auction(status);")

            connection.commit()
            print("Auction tables created successfully!")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    create_auction_tables()