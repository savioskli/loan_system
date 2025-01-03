import mysql.connector
from config import db_config

# Connect to MySQL
conn = mysql.connector.connect(**db_config)

cursor = conn.cursor(dictionary=True)

# Query core banking systems
cursor.execute("SELECT id, name, base_url, database_name, selected_tables, auth_type FROM core_banking_systems")
systems = cursor.fetchall()

print("\nCore Banking Systems Configuration:")
print("-" * 50)

for system in systems:
    print(f"\nSystem ID: {system['id']}")
    print(f"Name: {system['name']}")
    print(f"Base URL: {system['base_url']}")
    print(f"Database Name: {system['database_name']}")
    print(f"Selected Tables: {system['selected_tables']}")
    print(f"Auth Type: {system['auth_type']}")
    print("-" * 50)

cursor.close()
conn.close()
