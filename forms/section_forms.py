from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional

class FormSectionForm(FlaskForm):
    name = StringField('Section Name', 
                      validators=[DataRequired(), Length(max=100)],
                      render_kw={"class": "form-control"})
    
    description = TextAreaField('Description',
                              validators=[Optional(), Length(max=500)],
                              render_kw={"class": "form-control", "rows": 3})
    
    order = IntegerField('Display Order',
                        validators=[Optional()],
                        default=0,
                        render_kw={"class": "form-control"})
    
    is_active = BooleanField('Active',
                            default=True,
                            render_kw={"class": "form-check-input"})
    
    client_type_restrictions = SelectMultipleField('Client Types',
                                                 validators=[Optional()],
                                                 coerce=int,
                                                 render_kw={"class": "form-control"})
    
    product_restrictions = SelectMultipleField('Products',
                                             validators=[Optional()],
                                             coerce=int,
                                             render_kw={"class": "form-control"})
