from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, Optional

class GeneralSettingsForm(FlaskForm):
    site_name = StringField('Site Name', 
                          validators=[DataRequired(), Length(min=2, max=100)],
                          description="The name of your site that appears in the header and title")
    
    site_description = TextAreaField('Site Description',
                                  validators=[Optional(), Length(max=500)],
                                  description="A brief description of your site")
    
    site_logo = FileField('Site Logo',
                        validators=[
                            Optional(),
                            FileAllowed(['jpg', 'png'], 'Images only!')
                        ],
                        description="Upload your site logo (PNG or JPG)")
    
    theme_mode = RadioField('Theme Mode',
                         choices=[
                             ('light', 'Light Mode'),
                             ('dark', 'Dark Mode'),
                             ('system', 'System Default')
                         ],
                         default='light',
                         description="Choose the color theme for your site")
    
    primary_color = StringField('Primary Color',
                             validators=[
                                 DataRequired(),
                                 Length(min=4, max=7)  # For hex color codes
                             ],
                             default="#3B82F6",
                             description="Main color for buttons and highlights")
    
    secondary_color = StringField('Secondary Color',
                               validators=[
                                   DataRequired(),
                                   Length(min=4, max=7)  # For hex color codes
                               ],
                               default="#1E40AF",
                               description="Secondary color for accents")
