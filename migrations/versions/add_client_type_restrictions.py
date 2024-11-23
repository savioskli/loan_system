"""add client type restrictions

Revision ID: add_client_type_restrictions
Revises: merge_client_types_001
Create Date: 2023-11-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import JSON

# revision identifiers, used by Alembic.
revision = 'add_client_type_restrictions'
down_revision = 'merge_client_types_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add client_type_restrictions column to form_fields table
    op.add_column('form_fields',
        sa.Column('client_type_restrictions', JSON,
                  comment='List of client type IDs that can see this field')
    )


def downgrade():
    # Remove client_type_restrictions column from form_fields table
    op.drop_column('form_fields', 'client_type_restrictions')
