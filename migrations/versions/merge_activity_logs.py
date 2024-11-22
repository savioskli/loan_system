"""merge activity logs branches

Revision ID: merge_activity_logs_001
Revises: create_activity_logs_002, add_cascade_delete
Create Date: 2024-11-21 20:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_activity_logs_001'
down_revision = ('create_activity_logs_002', 'add_cascade_delete')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
