import mysql.connector
from mysql.connector import Error

try:
    # Connect to the database
    connection = mysql.connector.connect(
        host='localhost',
        database='loan_system',
        user='root',
        password=''
    )

    if connection.is_connected():
        cursor = connection.cursor()
        
        # Add attachment_path column
        alter_query = """
        ALTER TABLE correspondence 
        ADD COLUMN attachment_path VARCHAR(500)
        """
        
        cursor.execute(alter_query)
        connection.commit()
        print("Successfully added attachment_path column to correspondence table")

except Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Database connection closed.")
