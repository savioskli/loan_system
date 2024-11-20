from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('loan_officer', 'Loan Officer'),
        ('credit_analyst', 'Credit Analyst'),
        ('manager', 'Manager'),
        ('admin', 'Admin')
    ])
    submit = SubmitField('Register')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField('Role', choices=[
        ('loan_officer', 'Loan Officer'),
        ('credit_analyst', 'Credit Analyst'),
        ('manager', 'Manager'),
        ('admin', 'Admin')
    ])
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class SystemSettingsForm(FlaskForm):
    system_name = StringField('System Name', validators=[DataRequired(), Length(max=100)])
    system_description = TextAreaField('System Description', validators=[Length(max=500)])
    theme_primary_color = StringField('Primary Color', validators=[DataRequired(), Length(max=7)])
    theme_secondary_color = StringField('Secondary Color', validators=[DataRequired(), Length(max=7)])
    theme_mode = SelectField('Theme Mode', choices=[('light', 'Light'), ('dark', 'Dark')])
    system_logo = FileField('System Logo', validators=[
        FileAllowed(['jpg', 'png', 'gif'], 'Images only!')
    ])
    enable_registration = BooleanField('Enable Self Registration')
    
    # Database Settings
    db_host = StringField('Database Host', validators=[DataRequired()])
    db_port = StringField('Database Port', validators=[DataRequired()])
    db_name = StringField('Database Name', validators=[DataRequired()])
    
    def populate_from_settings(self, settings):
        """Populate form with current settings"""
        self.system_name.data = settings.get_setting('system_name', '')
        self.system_description.data = settings.get_setting('system_description', '')
        self.theme_primary_color.data = settings.get_setting('theme_primary_color', '#1a56db')
        self.theme_secondary_color.data = settings.get_setting('theme_secondary_color', '#7e3af2')
        self.theme_mode.data = settings.get_setting('theme_mode', 'light')
        self.enable_registration.data = settings.get_setting('enable_registration', False)
        self.db_host.data = settings.get_setting('db_host', 'localhost')
        self.db_port.data = settings.get_setting('db_port', '3306')
        self.db_name.data = settings.get_setting('db_name', 'loan_system')
