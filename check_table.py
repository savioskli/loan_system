from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    result = db.session.execute(text('DESCRIBE products;'))
    print("\nColumn names in products table:")
    for row in result:
        print(row[0])
