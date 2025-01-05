"""Remove loan_id from correspondence table

Revision ID: remove_loan_id_from_correspondence
Revises: # you'll need to put the previous migration ID here
Create Date: 2025-01-05 18:56:03.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'remove_loan_id_from_correspondence'
down_revision = None  # Update this with the previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    # Drop the foreign key constraint first
    op.drop_constraint('correspondence_ibfk_2', 'correspondence', type_='foreignkey')
    
    # Then drop the column
    op.drop_column('correspondence', 'loan_id')


def downgrade():
    # Add back the loan_id column
    op.add_column('correspondence', sa.Column('loan_id', mysql.INTEGER(), nullable=False))
    
    # Re-add the foreign key constraint
    op.create_foreign_key('correspondence_ibfk_2', 'correspondence', 'loans', ['loan_id'], ['id'])
