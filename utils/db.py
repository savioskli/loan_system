import mysql.connector
from flask import current_app

def get_db_connection():
    """Create and return a new database connection"""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="loan_system"
    )
