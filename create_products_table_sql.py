from app import create_app
from extensions import db
from models.product import Product
from sqlalchemy import text

app = create_app()
with app.app_context():
    sql = text('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(10) NOT NULL UNIQUE,
        status VARCHAR(20) NOT NULL DEFAULT 'Active',
        interest_rate VARCHAR(10),
        rate_method VARCHAR(20),
        processing_fee VARCHAR(50),
        maintenance_fee VARCHAR(50),
        insurance_fee VARCHAR(20),
        frequency VARCHAR(10),
        min_amount DECIMAL(20, 2) NOT NULL DEFAULT 1.00,
        max_amount DECIMAL(20, 2) NOT NULL,
        min_term INTEGER NOT NULL DEFAULT 1,
        max_term INTEGER NOT NULL,
        collateral TEXT,
        income_statement TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    ''')
    db.session.execute(sql)
    db.session.commit()
