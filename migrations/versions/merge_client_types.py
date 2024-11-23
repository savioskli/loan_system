"""merge client types branches

Revision ID: merge_client_types_001
Revises: fix_client_types, create_products_table
Create Date: 2024-11-23 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_client_types_001'
down_revision = ('fix_client_types', 'create_products_table')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
