from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from datetime import date, datetime

class ClientTypeForm(FlaskForm):
    client_code = StringField('Client Code', validators=[
        DataRequired(message="Client Code is required."),
        Length(min=2, max=20, message="Client Code must be between 2 and 20 characters.")
    ])
    client_name = StringField('Client Name', validators=[
        DataRequired(message="Client Name is required."),
        Length(min=2, max=100, message="Client Name must be between 2 and 100 characters.")
    ])
    effective_from = DateField('Effective From', 
                             validators=[DataRequired(message="Effective From date is required.")],
                             format='%Y-%m-%d',
                             render_kw={"type": "date"})
    effective_to = DateField('Effective To', 
                           validators=[Optional()],
                           format='%Y-%m-%d',
                           render_kw={"type": "date"})
    status = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def validate_effective_from(self, field):
        if not field.data:
            raise ValidationError('Effective From date is required.')
        if isinstance(field.data, str):
            try:
                field.data = datetime.strptime(field.data, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Invalid date format. Use YYYY-MM-DD.')

    def validate_effective_to(self, field):
        if field.data:
            if isinstance(field.data, str):
                try:
                    field.data = datetime.strptime(field.data, '%Y-%m-%d').date()
                except ValueError:
                    raise ValidationError('Invalid date format. Use YYYY-MM-DD.')
            
            if self.effective_from.data and field.data < self.effective_from.data:
                raise ValidationError('Effective To date must be after Effective From date.')
