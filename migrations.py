from app import app, db
from flask_migrate import Migrate, init, migrate, upgrade

migrate = Migrate(app, db)

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
