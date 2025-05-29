from flask import Flask
from extensions import db
from models.module import Module
from models.form_field import FormField
from models.staff import Staff
from models.role import Role
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    try:
        # First delete all form fields
        print("Deleting all form fields...")
        FormField.query.delete()
        
        # Delete child modules first (modules with parent_id not null)
        print("Deleting child modules...")
        Module.query.filter(Module.parent_id.isnot(None)).delete()
        
        # Then delete parent modules
        print("Deleting parent modules...")
        Module.query.filter(Module.parent_id.is_(None)).delete()
        
        # Commit the changes
        db.session.commit()
        print("Successfully cleared all modules and form fields from the database.")
        
        # Verify the tables are empty
        module_count = Module.query.count()
        form_count = FormField.query.count()
        print(f"\nVerification:")
        print(f"Modules remaining: {module_count}")
        print(f"Form fields remaining: {form_count}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {str(e)}")
        print("Changes have been rolled back.")
