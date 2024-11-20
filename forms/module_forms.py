from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Optional
from models.module import Module

class ModuleForm(FlaskForm):
    name = StringField('Module Name', validators=[DataRequired(), Length(max=100)])
    code = StringField('Module Code', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    parent_id = SelectField('Parent Module', coerce=int, validators=[Optional()])
    is_active = BooleanField('Active', default=True)

    def __init__(self, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)
        # Populate parent module choices
        self.parent_id.choices = [(0, 'None')] + [
            (m.id, m.name) for m in Module.query.filter_by(parent_id=None).all()
        ]

class FormFieldForm(FlaskForm):
    field_name = StringField('Field Name', validators=[DataRequired(), Length(max=100)])
    field_label = StringField('Field Label', validators=[DataRequired(), Length(max=100)])
    field_placeholder = StringField('Placeholder Text', validators=[Optional(), Length(max=200)])
    validation_text = StringField('Validation Message', validators=[Optional(), Length(max=200)],
                                description='Message to show when validation fails')
    field_type = SelectField('Field Type', choices=[
        ('text', 'Text Input'),
        ('number', 'Number Input'),
        ('date', 'Date Input'),
        ('select', 'Select Dropdown'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkboxes'),
        ('textarea', 'Text Area'),
        ('email', 'Email Input'),
        ('phone', 'Phone Input'),
        ('password', 'Password Input'),
        ('file', 'File Upload')
    ], validators=[DataRequired()])
    is_required = BooleanField('Required Field', default=False)
    
class FieldOptionForm(FlaskForm):
    label = StringField('Option Label', validators=[DataRequired()])
    value = StringField('Option Value', validators=[DataRequired()])

class DynamicFormFieldForm(FormFieldForm):
    options = FieldList(FormField(FieldOptionForm), min_entries=1)
    validation_rules = TextAreaField('Validation Rules (JSON)', validators=[Optional()],
                                   description='Example: {"min": 0, "max": 100, "pattern": "^[A-Za-z]+$"}')
