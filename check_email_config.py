from flask import Flask
from extensions import db
from models.email_config import EmailConfig

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

with app.app_context():
    configs = EmailConfig.query.all()
    print('\nEmail Configurations in Database:')
    for config in configs:
        print(f'\nID: {config.id}')
        print(f'Provider: {config.provider}')
        print(f'SMTP Server: {config.smtp_server}')
        print(f'SMTP Port: {config.smtp_port}')
        print(f'SMTP Username: {config.smtp_username}')
        print(f'From Email: {config.from_email}')
        print(f'Created At: {config.created_at}')
        print(f'Updated At: {config.updated_at}')
