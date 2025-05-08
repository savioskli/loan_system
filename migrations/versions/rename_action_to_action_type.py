"""rename action to action_type

Revision ID: rename_action_to_action_type
Revises: update_auction_table_names
Create Date: 2025-05-07 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_action_to_action_type'
down_revision = 'update_auction_table_names'
branch_labels = None
depends_on = None


def upgrade():
    # Rename column 'action' to 'action_type' in auction_history table
    op.alter_column('auction_history', 'action',
               new_column_name='action_type',
               existing_type=sa.String(length=100),
               nullable=False)


def downgrade():
    # Rename column back to 'action' if needed
    op.alter_column('auction_history', 'action_type',
               new_column_name='action',
               existing_type=sa.String(length=100),
               nullable=False)
