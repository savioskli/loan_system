"""Add module and form field tables

Revision ID: 553c90805d53
Revises: cac4ca53acf7
Create Date: 2024-11-21 08:26:06.016377

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '553c90805d53'
down_revision = 'cac4ca53acf7'
branch_labels = None
depends_on = None


def upgrade():
    # Create modules table
    op.create_table('modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['modules.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Create form_fields table
    op.create_table('form_fields',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('field_label', sa.String(length=100), nullable=False),
        sa.Column('field_placeholder', sa.String(length=200), nullable=True),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.Column('validation_text', sa.String(length=200), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('field_order', sa.Integer(), nullable=True),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('validation_rules', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('form_fields')
    op.drop_table('modules')
