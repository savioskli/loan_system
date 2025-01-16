from app import create_app, db
from sqlalchemy import text

def create_guarantor_claims_table():
    app = create_app()
    try:
        with app.app_context():
            with open('create_guarantor_claims_table.sql', 'r') as file:
                sql_script = file.read()
            
            # Execute the SQL script
            db.session.execute(text(sql_script))
            db.session.commit()
            print("Guarantor Claims table created successfully!")
    except Exception as e:
        print(f"Error creating Guarantor Claims table: {e}")

if __name__ == '__main__':
    create_guarantor_claims_table()
