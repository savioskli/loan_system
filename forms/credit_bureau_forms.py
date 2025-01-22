from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL, Length

class CreditBureauForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    provider = SelectField('Provider', choices=[
        ('metropol', 'Metropol CRB'),
        ('transunion', 'TransUnion')
    ], validators=[DataRequired()])
    base_url = StringField('Base URL', validators=[DataRequired(), URL(), Length(max=255)])
    api_key = StringField('API Key', validators=[DataRequired(), Length(max=255)])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=255)])
    is_active = BooleanField('Active')
