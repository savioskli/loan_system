from app import create_app
from extensions import db
from models.product import Product

app = create_app()
with app.app_context():
    db.create_all()
