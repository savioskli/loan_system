"""Add system_type column to core_banking_systems

Revision ID: add_system_type
Revises: create_guarantors_table
Create Date: 2025-01-03 14:52:44.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_system_type'
down_revision = 'create_guarantors_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add system_type column with default value 'generic'
    op.add_column('core_banking_systems',
        sa.Column('system_type', sa.String(20), nullable=False, server_default='generic')
    )


def downgrade():
    # Remove system_type column
    op.drop_column('core_banking_systems', 'system_type')
