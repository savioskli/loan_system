from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class ClientTypeForm(FlaskForm):
    client_code = StringField('Client Code', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    client_name = StringField('Client Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    effective_from = DateField('Effective From', validators=[DataRequired()])
    effective_to = DateField('Effective To', validators=[], render_kw={"required": False})
    status = BooleanField('Active')
    submit = SubmitField('Save')
