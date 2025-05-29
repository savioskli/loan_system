from app import create_app
from models.form_field import FormField

app = create_app()
with app.app_context():
    from app import db
    
    # Print table info
    print("\nTable name:", FormField.__table__.fullname)
    print("\nColumns:")
    for column in FormField.__table__.columns:
        print(f"- {column.name}: {column.type} (nullable={column.nullable}, default={column.default})")
    
    # Check if is_system is in columns
    print("\nIs 'is_system' in columns:", 'is_system' in FormField.__table__.columns)
    
    # Print the actual column definition
    if 'is_system' in FormField.__table__.columns:
        col = FormField.__table__.columns['is_system']
        print(f"\nColumn 'is_system' details:")
        print(f"- Type: {col.type}")
        print(f"- Nullable: {col.nullable}")
        print(f"- Default: {col.default}")
    
    # Print the model's __init__ method
    print("\nModel's __init__ method:")
    print(FormField.__init__.__code__.co_consts)
    
    # Check for any column properties
    print("\nColumn properties:")
    for name, prop in FormField.__mapper__.attrs.items():
        if hasattr(prop, 'columns'):
            for col in prop.columns:
                print(f"- {name}: {col}")
