from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, FieldList, FormField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional
from models.module import Module
from models.client_type import ClientType
from models.form_section import FormSection
from extensions import db
from flask import current_app
import traceback

class ModuleForm(FlaskForm):
    name = StringField('Module Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    parent_id = SelectField('Parent Module', coerce=int, validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    create_table = SelectField('Create Database Table', choices=[
        ('no', 'No'),
        ('yes', 'Yes')
    ], default='no')

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
    column_name = StringField('Database Column Name', validators=[Optional(), Length(max=100)],
                           description='The database column this field maps to (defaults to field_name in snake_case if empty)')
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
        ('tel', 'Phone Input'),
        ('password', 'Password Input'),
        ('file', 'File Upload'),
        ('system_reference', 'System Reference')
    ], validators=[DataRequired()], coerce=str)
    
    is_system = BooleanField('Is System Field', default=False,
                          description='If checked, this field will be linked to a system reference field')
    system_reference_field_id = SelectField('System Reference Field', 
                                        coerce=int,
                                        validators=[Optional()],
                                        description='Select the system reference field to link to')
    is_visible = BooleanField('Visible in Form', default=True,
                           description='If unchecked, this field will be hidden in the user form but can still be set by the system')
    is_required = BooleanField('Required Field', default=False)
    section_id = SelectField('Form Section', coerce=int, validators=[Optional()], 
                           description='Select the section this field belongs to')
    client_type_restrictions = SelectMultipleField('Client Type Restrictions', 
                                                 coerce=int,
                                                 validators=[Optional()],
                                                 description='Select client types that can access this field')
    
    # Validation rule fields
    min_length = StringField('Minimum Length', validators=[Optional()],
                          description='Minimum number of characters required')
    max_length = StringField('Maximum Length', validators=[Optional()],
                          description='Maximum number of characters allowed')
    pattern = StringField('Pattern (Regex)', validators=[Optional()],
                       description='Regular expression pattern for validation')
    min_value = StringField('Minimum Value', validators=[Optional()],
                         description='Minimum value allowed for number fields')
    max_value = StringField('Maximum Value', validators=[Optional()],
                         description='Maximum value allowed for number fields')
    step = StringField('Step Value', validators=[Optional()],
                    description='Increment step for number fields')
    min_date = StringField('Minimum Date', validators=[Optional()],
                        description='Earliest allowed date')
    max_date = StringField('Maximum Date', validators=[Optional()],
                        description='Latest allowed date')
    custom_validation_message = StringField('Custom Validation Message', validators=[Optional()],
                                        description='Custom message to show when validation fails')

    def __init__(self, *args, module_id=None, **kwargs):
        # Initialize validation rules from data if present
        data = kwargs.get('data', {}) 
        validation_rules = data.pop('validation_rules', {}) if isinstance(data, dict) else {}
        
        super(FormFieldForm, self).__init__(*args, **kwargs)
        
        try:
            # Always initialize section_id choices with at least the None option
            self.section_id.choices = [(0, 'None')]
            
            # Populate additional section choices if module_id is provided
            if module_id:
                try:
                    # Get the current module to check for parent
                    from models.module import Module
                    current_module = Module.query.get(module_id)
                    module_ids = [module_id]  # Start with current module
                    
                    # Include parent module if it exists
                    if current_module and current_module.parent_id:
                        module_ids.append(current_module.parent_id)
                        current_app.logger.info(f"Including parent module {current_module.parent_id} for sections")
                    
                    # Query sections from both current and parent modules
                    sections = FormSection.query.filter(
                        FormSection.is_active == True,
                        FormSection.module_id.in_(module_ids)
                    ).order_by(FormSection.order).all()
                    
                    if sections:
                        self.section_id.choices.extend([(s.id, s.name) for s in sections])
                        
                        # If this is an edit form (obj is provided) and section_id exists
                        obj = kwargs.get('obj')
                        if obj and hasattr(obj, 'section_id'):
                            # Ensure section_id is set correctly, even if it's None
                            if obj.section_id is None:
                                self.section_id.data = 0  # Set to 'None' option
                                current_app.logger.info(f"Setting section_id to None (0)")
                            else:
                                self.section_id.data = obj.section_id
                                current_app.logger.info(f"Setting section_id from obj: {obj.section_id}")
                except Exception as e:
                    current_app.logger.error(f"Error loading sections: {str(e)}")

            # Populate client type choices
            client_types = ClientType.query.filter_by(status=True).order_by(ClientType.client_name).all()
            current_app.logger.info(f"Found {len(client_types)} active client types")
            
            # Create choices list and log each client type
            choices = []
            for ct in client_types:
                current_app.logger.info(f"Adding client type: {ct.client_name} (ID: {ct.id}, Status: {ct.status})")
                choices.append((ct.id, ct.client_name))
            
            self.client_type_restrictions.choices = choices
            current_app.logger.info(f"Client type choices set to: {self.client_type_restrictions.choices}")

            # Initialize data if not set
            if self.client_type_restrictions.data is None:
                self.client_type_restrictions.data = []
            
            # Ensure data is a list
            if not isinstance(self.client_type_restrictions.data, list):
                current_app.logger.warning(f"Converting client_type_restrictions data to list. Current type: {type(self.client_type_restrictions.data)}")
                self.client_type_restrictions.data = list(self.client_type_restrictions.data) if self.client_type_restrictions.data else []
            
            # Set validation rule values from data
            if validation_rules:
                self.min_length.data = validation_rules.get('min_length', '')
                self.max_length.data = validation_rules.get('max_length', '')
                self.pattern.data = validation_rules.get('pattern', '')
                self.min_value.data = validation_rules.get('min_value', '')
                self.max_value.data = validation_rules.get('max_value', '')
                self.step.data = validation_rules.get('step', '')
                self.min_date.data = validation_rules.get('min_date', '')
                self.max_date.data = validation_rules.get('max_date', '')
                self.custom_validation_message.data = validation_rules.get('custom_message', '')
            
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

    def __init__(self, *args, **kwargs):
        super(FieldOptionForm, self).__init__(*args, **kwargs)
        if isinstance(kwargs.get('data'), dict):
            self.label.data = kwargs['data'].get('label', '')
            self.value.data = kwargs['data'].get('value', '')

    def process_formdata(self, valuelist):
        super(FieldOptionForm, self).process_formdata(valuelist)
        # Only store non-empty options
        if self.label.data and self.value.data:
            self.data = {
                'label': self.label.data,
                'value': self.value.data
            }
        else:
            self.data = None

class DynamicFormFieldForm(FormFieldForm):
    options = FieldList(FormField(FieldOptionForm), min_entries=1)
    validation_rules = TextAreaField('Validation Rules (JSON)', validators=[Optional()])

    def __init__(self, *args, module_id=None, **kwargs):
        # Extract options from data if present
        data = kwargs.get('data', {})
        options_data = data.pop('options', []) if isinstance(data, dict) else []
        
        super(DynamicFormFieldForm, self).__init__(*args, module_id=module_id, **kwargs)
        
        # Clear any existing options
        while len(self.options) > 0:
            self.options.pop_entry()
            
        # Add options from data
        for option in options_data:
            if isinstance(option, dict) and option.get('label') and option.get('value'):
                self.options.append_entry(option)
