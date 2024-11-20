from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from models.branch import Branch
from decimal import Decimal

class BranchForm(FlaskForm):
    branch_code = StringField('Branch Code', validators=[
        DataRequired(),
        Length(min=2, max=20, message='Branch code must be between 2 and 20 characters')
    ])
    branch_name = StringField('Branch Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Branch name must be between 2 and 100 characters')
    ])
    lower_limit = DecimalField('Lower Limit', validators=[
        DataRequired(),
        NumberRange(min=0, message='Lower limit must be greater than or equal to 0')
    ])
    upper_limit = DecimalField('Upper Limit', validators=[
        DataRequired(),
        NumberRange(min=0, message='Upper limit must be greater than or equal to 0')
    ])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Branch')

    def validate_branch_code(self, field):
        if self.branch_code.data:
            branch = Branch.query.filter_by(branch_code=field.data).first()
            if branch and (not hasattr(self, 'branch_id') or branch.id != self.branch_id):
                raise ValidationError('This branch code is already in use.')

    def validate_upper_limit(self, field):
        if self.lower_limit.data and field.data:
            if Decimal(str(field.data)) <= Decimal(str(self.lower_limit.data)):
                raise ValidationError('Upper limit must be greater than lower limit.')

class NewBranchForm(BranchForm):
    submit = SubmitField('Create Branch')

class EditBranchForm(BranchForm):
    submit = SubmitField('Update Branch')

    def __init__(self, branch_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.branch_id = branch_id
