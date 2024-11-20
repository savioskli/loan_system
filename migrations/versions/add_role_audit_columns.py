"""add role audit columns

Revision ID: add_role_audit_columns
Revises: 14f1ffd2f25e
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_role_audit_columns_2'
down_revision = '14f1ffd2f25e'
branch_labels = None
depends_on = None

def upgrade():
    # Add created_by and updated_by columns to roles table
    op.add_column('roles', sa.Column('created_by', sa.Integer(), sa.ForeignKey('staff.id'), nullable=True))
    op.add_column('roles', sa.Column('updated_by', sa.Integer(), sa.ForeignKey('staff.id'), nullable=True))

def downgrade():
    # Remove created_by and updated_by columns from roles table
    op.drop_column('roles', 'updated_by')
    op.drop_column('roles', 'created_by')
