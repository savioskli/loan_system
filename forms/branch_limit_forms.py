from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from models.branch import Branch
from models.branch_limit import BranchLimit

class BranchLimitForm(FlaskForm):
    branch_id = SelectField('Branch', coerce=int, validators=[DataRequired()])
    min_amount = DecimalField('Minimum Amount', places=2, validators=[DataRequired()])
    max_amount = DecimalField('Maximum Amount', places=2, validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Limit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.branch_id.choices = [(b.id, f"{b.code} - {b.name}") 
                                for b in Branch.query.filter_by(is_active=True).order_by(Branch.name).all()]

    def validate_max_amount(self, field):
        if self.min_amount.data and field.data:
            if field.data < self.min_amount.data:
                raise ValidationError('Maximum amount must be greater than minimum amount')

class NewBranchLimitForm(BranchLimitForm):
    submit = SubmitField('Create Limit')

    def validate_branch_id(self, field):
        existing = BranchLimit.query.filter_by(branch_id=field.data, is_active=True).first()
        if existing:
            raise ValidationError('An active limit already exists for this branch')

class EditBranchLimitForm(BranchLimitForm):
    submit = SubmitField('Update Limit')

    def __init__(self, limit_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_id = limit_id

    def validate_branch_id(self, field):
        existing = BranchLimit.query.filter_by(branch_id=field.data, is_active=True).first()
        if existing and existing.id != self.limit_id:
            raise ValidationError('An active limit already exists for this branch')
