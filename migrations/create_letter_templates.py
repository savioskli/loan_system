"""Create letter templates and letter types tables

Revision ID: create_letter_templates
Revises: 
Create Date: 2025-01-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade():
    # Create letter types table
    op.create_table(
        'letter_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create letter templates table
    op.create_table(
        'letter_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('letter_type_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('template_content', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['letter_type_id'], ['letter_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Seed initial letter types
    letter_types = table('letter_types',
        column('name'),
        column('description')
    )
    
    op.bulk_insert(letter_types, [
        {'name': 'Demand Letter', 'description': 'Letter sent for loan repayment'},
        {'name': 'Approval Letter', 'description': 'Loan approval communication'},
        {'name': 'Rejection Letter', 'description': 'Loan rejection notification'},
        {'name': 'Reminder Letter', 'description': 'Loan payment reminder'}
    ])

def downgrade():
    op.drop_table('letter_templates')
    op.drop_table('letter_types')
