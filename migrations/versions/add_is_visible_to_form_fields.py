"""add is_visible to form_fields

Revision ID: 1234567890ab
Revises: 
Create Date: 2025-05-31 10:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add the new column with a default of True (visible)
    op.add_column('form_fields', sa.Column('is_visible', sa.Boolean(), nullable=False, server_default='1'))
    
    # Create an index for better query performance
    op.create_index(op.f('ix_form_fields_is_visible'), 'form_fields', ['is_visible'], unique=False)

def downgrade():
    # Remove the index first
    op.drop_index(op.f('ix_form_fields_is_visible'), table_name='form_fields')
    
    # Remove the column
    op.drop_column('form_fields', 'is_visible')
