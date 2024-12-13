from flask import Flask
from extensions import db
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_form_submissions_table():
    """Create the form_submissions table."""
    try:
        with app.app_context():
            # Create form_submissions table
            sql = text("""
                CREATE TABLE IF NOT EXISTS form_submissions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    module_id INT NOT NULL,
                    client_type_id INT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    form_data JSON NOT NULL,
                    created_by INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (module_id) REFERENCES modules(id),
                    FOREIGN KEY (client_type_id) REFERENCES client_types(id),
                    FOREIGN KEY (created_by) REFERENCES staff(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            db.session.execute(sql)
            db.session.commit()
            print("Form submissions table created successfully!")
            
    except Exception as e:
        print(f"Error creating form submissions table: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    create_form_submissions_table()
