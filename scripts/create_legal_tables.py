import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.legal_case import LegalCase, LegalCaseAttachment

app = create_app()

with app.app_context():
    print("Creating legal case tables...")
    # Create metadata object with just our tables
    metadata = db.MetaData()
    for table in [LegalCase.__table__, LegalCaseAttachment.__table__]:
        table.tometadata(metadata)
    metadata.create_all(bind=db.engine)
    print("Successfully created legal case tables")
