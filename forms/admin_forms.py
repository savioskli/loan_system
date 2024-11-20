from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Length

class SystemSettingsForm(FlaskForm):
    system_name = StringField('System Name', validators=[
        DataRequired(message='System name is required'),
        Length(max=100, message='System name must be less than 100 characters')
    ])
    system_description = TextAreaField('System Description', validators=[
        Length(max=500, message='System description must be less than 500 characters')
    ])
    system_logo = FileField('System Logo')
    theme_mode = SelectField('Theme Mode', choices=[
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode')
    ])
    theme_primary_color = StringField('Primary Color', validators=[
        DataRequired(message='Primary color is required')
    ])
    theme_secondary_color = StringField('Secondary Color', validators=[
        DataRequired(message='Secondary color is required')
    ])
