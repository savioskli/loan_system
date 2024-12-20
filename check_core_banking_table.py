import mysql.connector
from mysql.connector import Error

# Database connection parameters
DB_NAME = "loan_system"
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "3306"

def check_table():
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

        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'core_banking_config'")
        if cursor.fetchone():
            print("Table 'core_banking_config' exists!")
            
            # Show table structure
            cursor.execute("DESCRIBE core_banking_config")
            print("\nTable Structure:")
            print("Field".ljust(20), "Type".ljust(30), "Null", "Key", "Default", "Extra")
            print("-" * 100)
            for row in cursor.fetchall():
                print(str(row[0]).ljust(20), str(row[1]).ljust(30), str(row[2]).ljust(6), str(row[3]).ljust(5), str(row[4]).ljust(8), row[5])
            
            # Check if there are any records
            cursor.execute("SELECT COUNT(*) FROM core_banking_config")
            count = cursor.fetchone()[0]
            print(f"\nNumber of records: {count}")
            
            if count > 0:
                cursor.execute("SELECT id, system_type, server_url, port, `database`, username, sync_interval, is_active, created_at FROM core_banking_config")
                print("\nExisting Configurations:")
                print("ID".ljust(5), "System".ljust(15), "Server".ljust(30), "Port".ljust(8), "Database".ljust(20), "Username".ljust(20), "Interval", "Active", "Created")
                print("-" * 130)
                for row in cursor.fetchall():
                    print(
                        str(row[0]).ljust(5),
                        str(row[1]).ljust(15),
                        str(row[2]).ljust(30),
                        str(row[3]).ljust(8),
                        str(row[4] or '').ljust(20),
                        str(row[5] or '').ljust(20),
                        str(row[6]).ljust(8),
                        str(row[7]).ljust(6),
                        row[8]
                    )
        else:
            print("Table 'core_banking_config' does not exist!")

    except Error as e:
        print(f"Error checking table: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    check_table()
