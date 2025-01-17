from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length

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
    letter_type_id = SelectField('Letter Type', coerce=int, validators=[DataRequired()])
    name = StringField('Template Name', validators=[
        DataRequired(), 
        Length(min=3, max=100, message='Name must be between 3 and 100 characters')
    ])
    template_content = TextAreaField('Template Content', validators=[
        DataRequired(),
        Length(min=10, message='Template content is too short')
    ])
    is_active = BooleanField('Active', default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from models.letter_template import LetterType
        self.letter_type_id.choices = [(lt.id, lt.name) for lt in LetterType.query.all()]
