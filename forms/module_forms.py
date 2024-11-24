from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, FieldList, FormField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional
from models.module import Module
from models.client_type import ClientType
from flask import current_app
import traceback

class ModuleForm(FlaskForm):
    name = StringField('Module Name', validators=[DataRequired(), Length(max=100)])
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
    ], validators=[DataRequired()], coerce=str)
    is_required = BooleanField('Required Field', default=False)
    client_type_restrictions = SelectMultipleField('Client Type Restrictions', 
                                                 coerce=int,
                                                 validators=[Optional()],
                                                 description='Select client types that can access this field')

    def __init__(self, *args, **kwargs):
        super(FormFieldForm, self).__init__(*args, **kwargs)
        try:
            # Populate client type choices
            client_types = ClientType.query.filter_by(status=True).order_by(ClientType.client_name).all()
            current_app.logger.info(f"Found {len(client_types)} active client types")
            
            # Create choices list and log each client type
            choices = []
            for ct in client_types:
                current_app.logger.info(f"Processing client type: ID={ct.id}, Name={ct.client_name}, Status={ct.status}")
                choices.append((ct.id, ct.client_name))
            
            self.client_type_restrictions.choices = choices
            current_app.logger.info(f"Final choices set: {self.client_type_restrictions.choices}")

            # Initialize data if not set
            if self.client_type_restrictions.data is None:
                self.client_type_restrictions.data = []
            
            # Ensure data is a list
            if not isinstance(self.client_type_restrictions.data, list):
                current_app.logger.warning(f"Converting client_type_restrictions data to list. Current type: {type(self.client_type_restrictions.data)}")
                self.client_type_restrictions.data = list(self.client_type_restrictions.data) if self.client_type_restrictions.data else []
            
            current_app.logger.info(f"Current client_type_restrictions data: {self.client_type_restrictions.data}")
            
        except Exception as e:
            current_app.logger.error(f"Error in FormFieldForm initialization: {str(e)}\n{traceback.format_exc()}")
            self.client_type_restrictions.choices = []
            self.client_type_restrictions.data = []

    def process_formdata(self, valuelist):
        super().process_formdata(valuelist)
        # Ensure client_type_restrictions is always a list
        if hasattr(self, 'client_type_restrictions'):
            if self.client_type_restrictions.data is None:
                self.client_type_restrictions.data = []
            elif not isinstance(self.client_type_restrictions.data, list):
                self.client_type_restrictions.data = list(self.client_type_restrictions.data)

class FieldOptionForm(FlaskForm):
    label = StringField('Option Label', validators=[DataRequired()])
    value = StringField('Option Value', validators=[DataRequired()])

class DynamicFormFieldForm(FormFieldForm):
    options = FieldList(FormField(FieldOptionForm), min_entries=1)
    validation_rules = TextAreaField('Validation Rules (JSON)', validators=[Optional()],
                                   description='Example: {"min": 0, "max": 100, "pattern": "^[A-Za-z]+$"}')
