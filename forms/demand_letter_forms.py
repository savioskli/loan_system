from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    TextAreaField, 
    SelectField, 
    DecimalField,
    SubmitField,
    HiddenField
)
from wtforms.validators import (
    DataRequired, 
    NumberRange, 
    Length,
    Optional
)

class DemandLetterForm(FlaskForm):
    """
    Form for creating demand letters
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Import models dynamically to avoid circular imports
        from models.letter_template import LetterType, LetterTemplate
        
        # Dynamically populate letter type choices
        self.letter_type_id.choices = [
            (str(type.id), type.name) 
            for type in LetterType.query.filter_by(is_active=True).all()
        ]
        
        # Dynamically populate letter template choices
        self.letter_template_id.choices = [
            (str(template.id), template.name) 
            for template in LetterTemplate.query.filter_by(is_active=True).all()
        ]
    
    member_id = SelectField(
        'Member', 
        validators=[DataRequired()],
        coerce=str,
        choices=[('', 'Select Member')]  # Default empty choice
    )
    
    member_name = StringField(
        'Member Name', 
        validators=[Optional()]  # Make optional to allow dynamic population
    )
    
    member_number = StringField(
        'Member Number', 
        validators=[Optional()],  
        description="Member Number (optional)"
    )
    
    loan_id = SelectField(
        'Loan Account', 
        validators=[DataRequired()],
        coerce=str,
        choices=[('', 'Select Loan Account')]  # Default empty choice
    )
    
    letter_type_id = SelectField(
        'Letter Type', 
        validators=[DataRequired()],
        coerce=str,
        choices=[('', 'Select Letter Type')]  # Default empty choice
    )
    
    letter_template_id = SelectField(
        'Letter Template', 
        validators=[DataRequired()],
        coerce=str,
        choices=[('', 'Select Letter Template')]  # Default empty choice
    )
    
    amount_outstanding = DecimalField(
        'Amount Outstanding', 
        validators=[
            DataRequired(), 
            NumberRange(min=0, message="Amount must be a positive number")
        ],
        places=2
    )
    
    letter_content = TextAreaField(
        'Letter Content', 
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Create Demand Letter')
    
    def validate_member_number(self, field):
        # If member_number is empty, use member_name as a fallback
        if not field.data and self.member_name.data:
            field.data = self.member_name.data
