from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    branch_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)

with app.app_context():
    branches = Branch.query.all()
    print("\nBranch List:")
    print("-" * 80)
    print(f"{'ID':<5} {'Branch Name':<30} {'Location':<30} {'Status':<10}")
    print("-" * 80)
    for branch in branches:
        status = "Active" if branch.is_active else "Inactive"
        print(f"{branch.id:<5} {branch.branch_name:<30} {branch.location:<30} {status:<10}")
    print("-" * 80)
