"""merge all heads

Revision ID: merge_all_heads
Revises: merge_heads, fix_client_types, add_client_type_restrictions
Create Date: 2024-11-23 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_all_heads'
down_revision = ('merge_heads', 'fix_client_types', 'add_client_type_restrictions')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
