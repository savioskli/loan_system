"""fix client types table

Revision ID: fix_client_types_001
Revises: merge_activity_logs_001
Create Date: 2024-01-09

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'fix_client_types_001'
down_revision = 'merge_activity_logs_001'
branch_labels = None
depends_on = None

def upgrade():
    # Rename existing columns
    op.alter_column('client_types', 'code', new_column_name='client_code')
    op.alter_column('client_types', 'name', new_column_name='client_name')
    
    # Add new columns
    op.add_column('client_types', sa.Column('effective_from', sa.Date(), nullable=True))
    op.add_column('client_types', sa.Column('effective_to', sa.Date(), nullable=True))
    op.add_column('client_types', sa.Column('status', sa.Boolean(), server_default='1'))
    
    # Drop unnecessary columns
    op.drop_column('client_types', 'description')
    op.drop_column('client_types', 'form_schema')

def downgrade():
    # Restore original columns
    op.alter_column('client_types', 'client_code', new_column_name='code')
    op.alter_column('client_types', 'client_name', new_column_name='name')
    
    # Drop new columns
    op.drop_column('client_types', 'effective_from')
    op.drop_column('client_types', 'effective_to')
    op.drop_column('client_types', 'status')
    
    # Restore dropped columns
    op.add_column('client_types', sa.Column('description', sa.String(200)))
    op.add_column('client_types', sa.Column('form_schema', sa.JSON))
