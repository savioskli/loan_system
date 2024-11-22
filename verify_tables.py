from app import create_app
from extensions import db
from models.product import Product  # Import the Product model
from models.staff import Staff
from models.system_settings import SystemSettings
from models.activity_log import ActivityLog
from models.branch import Branch
from models.role import Role
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Show table structure
    sql = text("DESCRIBE products;")
    result = db.session.execute(sql)
    print("\nProducts table structure:")
    for row in result:
        print(row)
