"""Add username field to staff model

Revision ID: 1cce31ce23be
Revises: add_staff_columns_001
Create Date: 2024-11-20 21:04:17.953099

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1cce31ce23be'
down_revision = 'add_staff_columns_001'
branch_labels = None
depends_on = None


def upgrade():
    # Update existing records with a default username based on email
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE staff 
            SET username = CONCAT(
                SUBSTRING_INDEX(email, '@', 1),
                CONCAT('_', id)
            )
            WHERE username IS NULL OR username = ''
            """
        )
    )

    # Now make username required and unique
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.String(length=50),
               nullable=False)
        batch_op.create_unique_constraint('uq_staff_username', ['username'])


def downgrade():
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.drop_constraint('uq_staff_username', type_='unique')
        batch_op.alter_column('username',
               existing_type=sa.String(length=50),
               nullable=True)
