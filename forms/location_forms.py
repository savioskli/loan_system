from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from models.location import County, SubCounty, Ward

class CountyForm(FlaskForm):
    name = StringField('County Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    code = StringField('County Code', validators=[
        DataRequired(),
        Length(min=1, max=10)
    ])
    submit = SubmitField('Save County')
    
    def validate_name(self, field):
        if self.county and self.county.name == field.data:
            return
        county = County.query.filter_by(name=field.data).first()
        if county:
            raise ValidationError('County name already exists.')
            
    def validate_code(self, field):
        if self.county and self.county.code == field.data:
            return
        county = County.query.filter_by(code=field.data).first()
        if county:
            raise ValidationError('County code already exists.')

class SubCountyForm(FlaskForm):
    name = StringField('Sub-County Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    county_id = SelectField('County', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Sub-County')
    
    def validate_name(self, field):
        if self.subcounty and self.subcounty.name == field.data and self.subcounty.county_id == int(self.county_id.data):
            return
        subcounty = SubCounty.query.filter_by(
            name=field.data,
            county_id=int(self.county_id.data)
        ).first()
        if subcounty:
            raise ValidationError('Sub-County name already exists in this county.')

class WardForm(FlaskForm):
    name = StringField('Ward Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    subcounty_id = SelectField('Sub-County', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Ward')
    
    def validate_name(self, field):
        if self.ward and self.ward.name == field.data and self.ward.subcounty_id == int(self.subcounty_id.data):
            return
        ward = Ward.query.filter_by(
            name=field.data,
            subcounty_id=int(self.subcounty_id.data)
        ).first()
        if ward:
            raise ValidationError('Ward name already exists in this sub-county.')
