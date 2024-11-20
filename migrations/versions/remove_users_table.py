"""remove users table

Revision ID: remove_users_table_001
Revises: 23a278951dc4
Create Date: 2024-01-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'remove_users_table_001'
down_revision = '23a278951dc4'  # This points to the previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Drop the users table and let MySQL handle the foreign key deletions
    op.execute('SET FOREIGN_KEY_CHECKS=0')
    op.drop_table('users')
    op.execute('SET FOREIGN_KEY_CHECKS=1')

def downgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='active'),
        sa.Column('is_active', sa.Boolean(), server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='users_ibfk_1'),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], name='users_ibfk_2'),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], name='approved_users_ibfk_1')
    )
