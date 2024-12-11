from app import create_app, db
from sqlalchemy import text

def add_depends_on_field():
    app = create_app()
    with app.app_context():
        try:
            # Add the depends_on column
            db.session.execute(text("""
                ALTER TABLE form_fields 
                ADD COLUMN depends_on VARCHAR(50) DEFAULT NULL
            """))
            db.session.commit()
            print("Successfully added depends_on field to form_fields table")
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    add_depends_on_field()
