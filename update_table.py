from app import create_app
from utils.dynamic_tables import create_or_update_module_table
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

app = create_app()
with app.app_context():
    success = create_or_update_module_table('CLM02')
    print(f"Table update {'succeeded' if success else 'failed'}")
