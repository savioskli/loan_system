import mysql.connector
from config import db_config

def setup_roles():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create roles table if it doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            code VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_table_sql)

        # Sample roles
        roles = [
            {
                'name': 'Collection Officer',
                'code': 'COLL_OFF',
                'description': 'Responsible for following up on loan collections and maintaining customer relationships'
            },
            {
                'name': 'Collection Supervisor',
                'code': 'COLL_SUP',
                'description': 'Oversees collection officers and manages escalated cases'
            },
            {
                'name': 'Branch Manager',
                'code': 'BRANCH_MGR',
                'description': 'Manages branch operations and staff'
            },
            {
                'name': 'System Administrator',
                'code': 'SYS_ADMIN',
                'description': 'Manages system configuration and user access'
            }
        ]

        # Insert roles
        insert_sql = """
        INSERT INTO roles (name, code, description, is_active)
        VALUES (%(name)s, %(code)s, %(description)s, 1)
        ON DUPLICATE KEY UPDATE
        description = VALUES(description),
        is_active = 1
        """

        for role in roles:
            try:
                cursor.execute(insert_sql, role)
                print(f"Added/Updated role: {role['name']}")
            except mysql.connector.Error as err:
                print(f"Error adding role {role['name']}: {err}")

        # Commit the changes
        conn.commit()
        print("\nRoles setup completed successfully!")

        # Display current roles
        cursor.execute("SELECT name, code FROM roles WHERE is_active = 1 ORDER BY name")
        roles = cursor.fetchall()
        print("\nCurrent active roles in the system:")
        for role in roles:
            print(f"- {role[0]} ({role[1]})")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_roles()
