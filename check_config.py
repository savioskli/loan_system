import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import mysql.connector
from flask import Flask
from models import db
from models.core_banking import CoreBankingSystem
from models.user import User
from models.staff import Staff, Role
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    # Query the core banking systems table
    systems = CoreBankingSystem.query.all()

    print("\nCore Banking Systems Configuration:")
    print("-" * 50)

    for system in systems:
        print(f"\nSystem ID: {system.id}")
        print(f"Name: {system.name}")
        print(f"Base URL: {system.base_url}")
        print(f"Database Name: {system.database_name}")
        print(f"Selected Tables: {system.selected_tables}")
        print(f"Auth Type: {system.auth_type}")
        print(f"Auth Credentials: {system.auth_credentials}")
        print("-" * 50)
