from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from models.organization import Organization

class OrganizationForm(FlaskForm):
    name = StringField('Organization Name', validators=[
        DataRequired(),
        Length(min=2, max=255)
    ])
    code = StringField('Organization Code', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    description = TextAreaField('Description')
    is_active = BooleanField('Is Active', default=True)

    def validate_code(self, field):
        org = Organization.query.filter_by(code=field.data).first()
        if org:
            raise ValidationError('This organization code is already in use.')
