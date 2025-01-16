from app import create_app, db

def create_tables():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("All tables created successfully!")

if __name__ == '__main__':
    create_tables()
