"""empty message

Revision ID: a5ec725474b9
Revises: add_role_audit_columns_2, add_role_id_to_staff
Create Date: 2024-11-20 15:32:51.392856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5ec725474b9'
down_revision = ('add_role_audit_columns_2', 'add_role_id_to_staff')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
