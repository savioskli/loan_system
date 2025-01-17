from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    TextAreaField, 
    SelectField, 
    DecimalField,
    SubmitField
)
from wtforms.validators import (
    DataRequired, 
    NumberRange, 
    Length
)

class DemandLetterForm(FlaskForm):
    """
    Form for creating demand letters
    """
    member_id = SelectField(
        'Member', 
        validators=[DataRequired()], 
        coerce=int,
        choices=[]  # Will be populated dynamically in the route
    )
    
    letter_type_id = SelectField(
        'Letter Type', 
        validators=[DataRequired()], 
        coerce=int,
        choices=[]  # Will be populated dynamically in the route
    )
    
    letter_template_id = SelectField(
        'Letter Template', 
        validators=[DataRequired()], 
        coerce=int,
        choices=[]  # Will be populated dynamically based on letter type
    )
    
    amount_outstanding = DecimalField(
        'Amount Outstanding', 
        validators=[
            DataRequired(), 
            NumberRange(min=0, message='Amount must be non-negative')
        ],
        places=2
    )
    
    letter_content = TextAreaField(
        'Letter Content', 
        validators=[
            DataRequired(), 
            Length(min=10, max=5000, message='Letter content must be between 10 and 5000 characters')
        ]
    )
    
    submit = SubmitField('Create Demand Letter')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically populate letter type choices
        from models.letter_template import LetterType
        self.letter_type_id.choices = [
            (type.id, type.name) 
            for type in LetterType.query.filter_by(is_active=True).all()
        ]
        
        # Letter template choices will be populated dynamically via JavaScript
