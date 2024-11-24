"""add form sections

Revision ID: add_form_sections
Revises: 553c90805d53
Create Date: 2024-01-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_form_sections'
down_revision = '553c90805d53'
branch_labels = None
depends_on = None


def upgrade():
    # Create form_sections table
    op.create_table(
        'form_sections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add section_id to form_fields table
    op.add_column('form_fields',
        sa.Column('section_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_form_fields_section',
        'form_fields', 'form_sections',
        ['section_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Remove foreign key constraint and section_id column from form_fields
    op.drop_constraint('fk_form_fields_section', 'form_fields', type_='foreignkey')
    op.drop_column('form_fields', 'section_id')
    
    # Drop form_sections table
    op.drop_table('form_sections')
