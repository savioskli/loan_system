"""add staff columns

Revision ID: add_staff_columns_001
Revises: d7982b877310
Create Date: 2024-01-09 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_staff_columns_001'
down_revision = 'd7982b877310'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to staff table
    op.add_column('staff', sa.Column('status', sa.String(20), server_default='active'))
    op.add_column('staff', sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('staff.id'), nullable=True))
    op.add_column('staff', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('staff', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))
    
    # Update existing staff records to have 'active' status
    op.execute("UPDATE staff SET status = 'active' WHERE status IS NULL")

def downgrade():
    # Remove columns from staff table
    op.drop_column('staff', 'status')
    op.drop_column('staff', 'approved_by_id')
    op.drop_column('staff', 'approved_at')
    op.drop_column('staff', 'updated_at')
