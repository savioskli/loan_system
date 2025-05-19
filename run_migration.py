from flask import Flask, current_app
from extensions import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/loan_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    from migrations.add_rich_content_to_chat import upgrade_chat_messages
    result = upgrade_chat_messages()
    print(f'Migration result: {result}')
