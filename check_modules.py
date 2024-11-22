from flask import Flask
from extensions import db
from models.module import Module
from models.staff import Staff
from models.role import Role
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    modules = Module.query.all()
    print("\nCurrent Modules in Database:")
    print("-" * 80)
    print(f"{'ID':<5} {'Name':<30} {'Code':<20} {'Parent ID':<10} {'Active':<8}")
    print("-" * 80)
    for module in modules:
        print(f"{module.id:<5} {module.name[:30]:<30} {module.code:<20} {module.parent_id if module.parent_id else 'None':<10} {str(module.is_active):<8}")
    print("-" * 80)
