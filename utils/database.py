import mysql.connector
from flask import current_app

def get_db_connection():
    """Get a connection to the database."""
    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        return connection
    except mysql.connector.Error as err:
        current_app.logger.error(f"Error connecting to database: {err}")
        raise
