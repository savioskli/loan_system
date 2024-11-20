"""empty message

Revision ID: d7982b877310
Revises: 3b52ea732bec, remove_users_table_001
Create Date: 2024-11-20 20:33:48.725036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7982b877310'
down_revision = ('3b52ea732bec', 'remove_users_table_001')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
