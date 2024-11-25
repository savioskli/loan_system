from app import create_app
from models.module import Module

app = create_app()
with app.app_context():
    module = Module.query.filter_by(code='CLM01').first()
    if module:
        print(f'Module ID: {module.id}')
        print(f'Module Name: {module.name}')
        print(f'Module Description: {module.description}')
        print(f'\nActive Sections:')
        for section in module.sections.filter_by(is_active=True).all():
            print(f'\nSection: {section.name}')
            print(f'Fields:')
            for field in section.fields.all():
                print(f'  - {field.field_name}: {field.field_type} (Required: {field.is_required})')
