from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class LetterTypeForm(FlaskForm):
    name = StringField('Letter Type Name', validators=[
        DataRequired(), 
        Length(min=3, max=100, message='Name must be between 3 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description cannot exceed 500 characters')
    ])
    is_active = BooleanField('Active', default=True)

class LetterTemplateForm(FlaskForm):
    """
    Form for creating and editing letter templates
    """
    letter_type_id = SelectField(
        'Letter Type', 
        validators=[DataRequired(message='Please select a letter type')],
        coerce=int
    )
    
    name = StringField(
        'Template Name', 
        validators=[
            DataRequired(message='Template name is required'),
            Length(min=3, max=100, message='Name must be between 3 and 100 characters')
        ]
    )
    
    template_content = TextAreaField(
        'Template Content', 
        validators=[
            DataRequired(message='Template content is required'),
            Length(min=10, max=2000, message='Template content must be between 10 and 2000 characters')
        ],
        description='Use placeholders: {member_name}, {member_number}, {account_no}, {amount_outstanding}'
    )
    
    is_active = BooleanField(
        'Active', 
        default=True,
        description='Enable or disable this letter template'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from models.letter_template import LetterType
        self.letter_type_id.choices = [(lt.id, lt.name) for lt in LetterType.query.all()]
