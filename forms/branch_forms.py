from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from models.branch import Branch

class BranchForm(FlaskForm):
    code = StringField('Branch Code', validators=[
        DataRequired(),
        Length(min=2, max=20, message='Branch code must be between 2 and 20 characters')
    ])
    name = StringField('Branch Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Branch name must be between 2 and 100 characters')
    ])
    address = TextAreaField('Address', validators=[
        Optional(),
        Length(max=200, message='Address cannot exceed 200 characters')
    ])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Branch')

    def validate_code(self, field):
        if self.code.data:
            branch = Branch.query.filter_by(code=field.data).first()
            if branch and (not hasattr(self, 'branch_id') or branch.id != self.branch_id):
                raise ValidationError('This branch code is already in use.')

class NewBranchForm(BranchForm):
    submit = SubmitField('Create Branch')

class EditBranchForm(BranchForm):
    submit = SubmitField('Update Branch')

    def __init__(self, branch_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.branch_id = branch_id
