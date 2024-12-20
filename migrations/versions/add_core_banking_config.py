"""add core banking config table

Revision ID: add_core_banking_config
Revises: 
Create Date: 2024-12-20 16:51:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_core_banking_config'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create core_banking_config table
    op.create_table('core_banking_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('system_type', sa.String(length=50), nullable=False),
        sa.Column('server_url', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('database', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('sync_interval', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('sync_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('selected_tables', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Add index on is_active to optimize queries for active config
    op.create_index(op.f('ix_core_banking_config_is_active'), 'core_banking_config', ['is_active'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_core_banking_config_is_active'), table_name='core_banking_config')
    
    # Drop table
    op.drop_table('core_banking_config')
