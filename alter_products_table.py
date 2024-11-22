from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    sql = text('''
    ALTER TABLE products 
    MODIFY interest_rate VARCHAR(10) NOT NULL;
    ''')
    db.session.execute(sql)
    db.session.commit()
