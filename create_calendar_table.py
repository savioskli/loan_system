import mysql.connector
from mysql.connector import Error
import os

def create_calendar_table():
    try:
        # Database configuration
        config = {
            'host': 'localhost',  # or your MySQL host
            'user': 'root',       # your MySQL username
            'password': '',       # your MySQL password
            'database': 'loan_system'  # your database name
        }

        # Create connection
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Read the SQL file
            with open('migrations/create_calendar_events.sql', 'r') as file:
                sql_commands = file.read()
            
            # Execute the SQL commands
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command + ';')
            
            # Commit the changes
            connection.commit()
            print("Calendar events table created successfully!")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    create_calendar_table()
