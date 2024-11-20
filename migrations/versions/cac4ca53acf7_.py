"""empty message

Revision ID: cac4ca53acf7
Revises: drop_old_settings_columns, merge_heads
Create Date: 2024-11-20 22:22:03.848690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cac4ca53acf7'
down_revision = ('drop_old_settings_columns', 'merge_heads')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
