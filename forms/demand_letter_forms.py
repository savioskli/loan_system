from flask_wtf import FlaskForm
from wtforms import (
    SelectField, 
    TextAreaField, 
    DecimalField, 
    StringField
)
from wtforms.validators import (
    DataRequired, 
    Length, 
    Optional, 
    NumberRange
)

class DemandLetterForm(FlaskForm):
    """
    Form for creating demand letters
    """
    member_id = SelectField(
        'Member', 
        validators=[DataRequired(message='Please select a member')],
        coerce=int
    )
    
    letter_type_id = SelectField(
        'Letter Type', 
        validators=[DataRequired(message='Please select a letter type')],
        coerce=int
    )
    
    letter_template_id = SelectField(
        'Letter Template', 
        validators=[DataRequired(message='Please select a letter template')],
        coerce=int
    )
    
    amount_outstanding = DecimalField(
        'Amount Outstanding', 
        validators=[
            DataRequired(message='Amount outstanding is required'),
            NumberRange(min=0, message='Amount must be a positive number')
        ],
        places=2
    )
    
    letter_content = TextAreaField(
        'Letter Content', 
        validators=[
            Optional(),
            Length(max=2000, message='Letter content cannot exceed 2000 characters')
        ]
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically populate member choices
        from models.member import Member
        self.member_id.choices = [
            (member.id, member.full_name) 
            for member in Member.query.filter_by(is_active=True).all()
        ]
        
        # Dynamically populate letter type choices
        from models.letter_template import LetterType
        self.letter_type_id.choices = [
            (type.id, type.name) 
            for type in LetterType.query.filter_by(is_active=True).all()
        ]
        
        # Letter template choices will be populated dynamically via JavaScript
