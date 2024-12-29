from extensions import db
from flask import Flask
from models.collection_schedule import CollectionSchedule
from models.loan import Loan
from models.staff import Staff

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print('Database tables created successfully.')
