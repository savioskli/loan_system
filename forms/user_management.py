from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, Regexp
from wtforms import ValidationError
from models.role import Role
from models.staff import Staff

class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[
        DataRequired(message='Role name is required'),
        Length(min=2, max=50, message='Role name must be between 2 and 50 characters')
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=200, message='Description cannot exceed 200 characters')
    ])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Role')

    def __init__(self, *args, **kwargs):
        self._obj = kwargs.get('obj', None)  # Store the original object
        super(RoleForm, self).__init__(*args, **kwargs)
        # Convert string 'y' to boolean True for is_active field
        if isinstance(self.is_active.data, str):
            self.is_active.data = self.is_active.data.lower() in ['true', 't', 'yes', 'y', '1']

    def validate_name(self, field):
        """Validate the role name field"""
        try:
            if not field.data:
                raise ValidationError('Role name is required')
            
            # Strip whitespace
            name = field.data.strip()
            if not name:
                raise ValidationError('Role name cannot be empty')
            
            # Check length
            if len(name) < 2:
                raise ValidationError('Role name must be at least 2 characters long')
            if len(name) > 50:
                raise ValidationError('Role name cannot exceed 50 characters')
            
            # Convert to lowercase for case-insensitive comparison
            name_lower = name.lower()
            if name_lower in ['admin', 'superadmin', 'administrator']:
                raise ValidationError('This role name is reserved')
            
            try:
                from sqlalchemy.exc import SQLAlchemyError
                # Check for existing role with same name (case-insensitive)
                try:
                    print(f"Form validation - checking for existing role: {name}")  # Debug print
                    print(f"Current role object: {self._obj}")  # Debug print
                    
                    # If we're editing an existing role, exclude it from the duplicate check
                    query = Role.query.filter(Role.name.ilike(name))
                    if self._obj:
                        query = query.filter(Role.id != self._obj.id)
                    
                    existing_role = query.first()
                    print(f"Form validation - existing role result: {existing_role}")  # Debug print
                    
                    if existing_role:
                        raise ValidationError('A role with this name already exists')
                        
                except SQLAlchemyError as db_error:
                    print(f"Form validation - database error: {str(db_error)}")  # Debug print
                    raise ValidationError(f'Database error: {str(db_error)}')
                    
            except ImportError as import_error:
                print(f"Form validation - import error: {str(import_error)}")  # Debug print
                raise ValidationError('System configuration error')
                
        except ValidationError:
            raise
        except Exception as e:
            print(f"Form validation - unexpected error: {str(e)}")  # Debug print
            raise ValidationError(f'Validation error: {str(e)}')

class UserApprovalForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')

class UserCreateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50, message='Username must be between 3 and 50 characters'),
        Regexp(r'^[\w.-]+$', message='Username can only contain letters, numbers, dots, and dashes')
    ])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20, message='Phone number cannot exceed 20 characters'),
        Regexp(r'^\+?1?\d{9,15}$', message='Please enter a valid phone number. Format: +1234567890')
    ])
    branch_id = SelectField('Branch', coerce=int, validators=[Optional()])
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        Optional(),  # Make password optional for editing
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        Optional(),  # Make confirm password optional for editing
        EqualTo('password', message='Passwords must match')
    ])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Changes')

    def __init__(self, *args, **kwargs):
        self._obj = kwargs.get('obj', None)  # Store the original object
        super(UserCreateForm, self).__init__(*args, **kwargs)
        # Convert string 'y' to boolean True for is_active field
        if isinstance(self.is_active.data, str):
            self.is_active.data = self.is_active.data.lower() in ['true', 't', 'yes', 'y', '1']

    def validate_password(self, field):
        if not self.password.data and not hasattr(self, '_obj'):
            # If this is a new user (no _obj), password is required
            raise ValidationError('Password is required for new users')

    def validate_username(self, field):
        if not field.data:
            return
        
        from models.staff import Staff
        # Check if username already exists (case-insensitive)
        query = Staff.query.filter(Staff.username.ilike(field.data.strip()))
        if self._obj:
            query = query.filter(Staff.id != self._obj.id)
        
        if query.first():
            raise ValidationError('This username is already taken')
