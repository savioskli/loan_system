from app import create_app
from models.module import Module

app = create_app()
with app.app_context():
    module = Module.query.filter_by(code='CLM02').first()
    print(f'Module ID: {module.id}')
