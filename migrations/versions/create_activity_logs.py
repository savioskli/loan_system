"""create activity logs table

Revision ID: create_activity_logs_002
Revises: 553c90805d53
Create Date: 2024-11-21 16:59:10.781382

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'create_activity_logs_002'
down_revision = '553c90805d53'
branch_labels = None
depends_on = None


def upgrade():
    # Create activity_logs table if it doesn't exist
    op.execute('DROP TABLE IF EXISTS activity_logs')
    op.create_table('activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('details', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['staff.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # Create index on timestamp for faster querying
    op.create_index(op.f('ix_activity_logs_timestamp'), 'activity_logs', ['timestamp'], unique=False)


def downgrade():
    # Drop index first
    op.drop_index(op.f('ix_activity_logs_timestamp'), table_name='activity_logs')
    # Then drop the table
    op.execute('DROP TABLE IF EXISTS activity_logs')
