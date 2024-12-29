import mysql.connector
from config import db_config

def setup_branches():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create branches table if it doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS branches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            code VARCHAR(20) NOT NULL UNIQUE,
            address TEXT,
            phone VARCHAR(20),
            email VARCHAR(100),
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_table_sql)

        # Sample branches
        branches = [
            {
                'name': 'Main Branch',
                'code': 'MAIN',
                'address': 'Central Business District, Nairobi',
                'is_active': 1
            },
            {
                'name': 'Downtown Branch',
                'code': 'DWNTN',
                'address': 'Downtown Area, Nairobi',
                'is_active': 1
            },
            {
                'name': 'East Branch',
                'code': 'EAST',
                'address': 'Eastern District, Nairobi',
                'is_active': 1
            },
            {
                'name': 'West Branch',
                'code': 'WEST',
                'address': 'Western District, Nairobi',
                'is_active': 1
            }
        ]

        # Insert branches
        insert_sql = """
        INSERT INTO branches (name, code, address, is_active)
        VALUES (%(name)s, %(code)s, %(address)s, %(is_active)s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        address = VALUES(address),
        is_active = VALUES(is_active)
        """

        for branch in branches:
            try:
                cursor.execute(insert_sql, branch)
                print(f"Added/Updated branch: {branch['name']}")
            except mysql.connector.Error as err:
                print(f"Error adding branch {branch['name']}: {err}")

        # Commit the changes
        conn.commit()
        print("\nBranches setup completed successfully!")

        # Display current branches
        cursor.execute("SELECT name, code, address FROM branches WHERE is_active = 1 ORDER BY name")
        branches = cursor.fetchall()
        print("\nCurrent active branches in the system:")
        for branch in branches:
            print(f"- {branch[0]} ({branch[1]}) - {branch[2]}")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_branches()
