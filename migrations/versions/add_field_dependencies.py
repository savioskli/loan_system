"""add field dependencies table

Revision ID: add_field_dependencies
Revises: 
Create Date: 2024-12-13 13:43:31.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_field_dependencies'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('field_dependencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parent_field_id', sa.Integer(), nullable=False),
        sa.Column('dependent_field_id', sa.Integer(), nullable=False),
        sa.Column('show_on_values', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['parent_field_id'], ['form_fields.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dependent_field_id'], ['form_fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('field_dependencies')
