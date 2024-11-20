"""merge heads

Revision ID: merge_heads
Revises: add_updated_fields, fix_settings_columns
Create Date: 2024-11-20 22:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('add_updated_fields', 'fix_settings_columns')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
