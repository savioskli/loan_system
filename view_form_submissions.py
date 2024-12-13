from flask import Flask
from extensions import db
from sqlalchemy import text
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def view_form_submissions():
    """View all form submissions with related data."""
    try:
        with app.app_context():
            # Query to get submissions with module, client type, and staff info
            sql = text("""
                SELECT 
                    fs.id,
                    fs.status,
                    fs.form_data,
                    fs.created_at,
                    m.code as module_code,
                    m.name as module_name,
                    ct.client_name as client_type,
                    CONCAT(s.first_name, ' ', s.last_name) as submitted_by
                FROM form_submissions fs
                JOIN modules m ON fs.module_id = m.id
                JOIN client_types ct ON fs.client_type_id = ct.id
                JOIN staff s ON fs.created_by = s.id
                ORDER BY fs.created_at DESC;
            """)
            
            result = db.session.execute(sql)
            
            # Print submissions in a readable format
            for row in result:
                print("\n" + "="*80)
                print(f"Submission ID: {row.id}")
                print(f"Module: {row.module_code} - {row.module_name}")
                print(f"Client Type: {row.client_type}")
                print(f"Status: {row.status}")
                print(f"Submitted By: {row.submitted_by}")
                print(f"Created At: {row.created_at}")
                print("\nForm Data:")
                # Pretty print the JSON data
                form_data = json.loads(row.form_data) if isinstance(row.form_data, str) else row.form_data
                for key, value in form_data.items():
                    print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error viewing form submissions: {str(e)}")

if __name__ == '__main__':
    view_form_submissions()
