from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, DateField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Optional

class LegalCaseForm(FlaskForm):
    loan_id = StringField('Loan ID', validators=[DataRequired()])
    case_number = StringField('Case Number', validators=[DataRequired()])
    court_name = StringField('Court Name', validators=[DataRequired()])
    case_type = SelectField('Case Type', 
                          choices=[
                              ('civil', 'Civil Case'),
                              ('criminal', 'Criminal Case'),
                              ('bankruptcy', 'Bankruptcy'),
                              ('other', 'Other')
                          ],
                          validators=[DataRequired()])
    filing_date = DateField('Filing Date', validators=[DataRequired()])
    status = SelectField('Status',
                        choices=[
                            ('active', 'Active'),
                            ('pending', 'Pending'),
                            ('resolved', 'Resolved'),
                            ('dismissed', 'Dismissed')
                        ],
                        validators=[DataRequired()])
    plaintiff = StringField('Plaintiff', validators=[DataRequired()])
    defendant = StringField('Defendant', validators=[DataRequired()])
    amount_claimed = FloatField('Amount Claimed', validators=[DataRequired()])
    lawyer_name = StringField('Lawyer Name', validators=[Optional()])
    lawyer_contact = StringField('Lawyer Contact', validators=[Optional()])
    description = TextAreaField('Case Description', validators=[Optional()])
    next_hearing_date = DateField('Next Hearing Date', validators=[Optional()])
    attachments = MultipleFileField('Attachments')
