"""remove prospects table

Revision ID: remove_prospects_table
Revises: merge_all_heads
Create Date: 2024-12-11 13:23:34.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'remove_prospects_table'
down_revision = 'merge_all_heads'
branch_labels = None
depends_on = None


def upgrade():
    # Drop foreign keys first
    op.drop_constraint('prospects_ibfk_1', 'prospects', type_='foreignkey')
    op.drop_constraint('prospects_ibfk_2', 'prospects', type_='foreignkey')
    
    # Then drop the table
    op.drop_table('prospects')


def downgrade():
    # Create prospects table
    op.create_table('prospects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_type_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('middle_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('id_number', sa.String(length=50), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('county', sa.String(length=100), nullable=True),
        sa.Column('sub_county', sa.String(length=100), nullable=True),
        sa.Column('postal_address', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('town', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=True),
        sa.Column('form_data', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['client_type_id'], ['client_types.id'], name='prospects_ibfk_1'),
        sa.ForeignKeyConstraint(['created_by'], ['staff.id'], name='prospects_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
    )
