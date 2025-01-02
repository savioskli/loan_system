"""update core banking tables

Revision ID: update_core_banking_tables
Revises: add_core_banking_config
Create Date: 2024-12-31 13:33:21.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_core_banking_tables'
down_revision = 'add_core_banking_config'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old core_banking_config table
    op.drop_table('core_banking_config')

    # Create core_banking_systems table
    op.create_table('core_banking_systems',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('base_url', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('auth_type', sa.String(length=20), nullable=False),
        sa.Column('auth_credentials', sa.Text(), nullable=True),
        sa.Column('headers', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create core_banking_endpoints table
    op.create_table('core_banking_endpoints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('system_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parameters', sa.Text(), nullable=True),
        sa.Column('headers', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['system_id'], ['core_banking_systems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create core_banking_logs table
    op.create_table('core_banking_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('system_id', sa.Integer(), nullable=False),
        sa.Column('endpoint_id', sa.Integer(), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=False),
        sa.Column('request_url', sa.String(length=255), nullable=False),
        sa.Column('request_headers', sa.Text(), nullable=True),
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_headers', sa.Text(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['system_id'], ['core_banking_systems.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['endpoint_id'], ['core_banking_endpoints.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_core_banking_systems_is_active', 'core_banking_systems', ['is_active'])
    op.create_index('ix_core_banking_endpoints_is_active', 'core_banking_endpoints', ['is_active'])
    op.create_index('ix_core_banking_endpoints_system_id', 'core_banking_endpoints', ['system_id'])
    op.create_index('ix_core_banking_logs_system_id', 'core_banking_logs', ['system_id'])
    op.create_index('ix_core_banking_logs_endpoint_id', 'core_banking_logs', ['endpoint_id'])
    op.create_index('ix_core_banking_logs_created_at', 'core_banking_logs', ['created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_core_banking_logs_created_at')
    op.drop_index('ix_core_banking_logs_endpoint_id')
    op.drop_index('ix_core_banking_logs_system_id')
    op.drop_index('ix_core_banking_endpoints_system_id')
    op.drop_index('ix_core_banking_endpoints_is_active')
    op.drop_index('ix_core_banking_systems_is_active')

    # Drop tables
    op.drop_table('core_banking_logs')
    op.drop_table('core_banking_endpoints')
    op.drop_table('core_banking_systems')

    # Recreate original core_banking_config table
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

    # Recreate original index
    op.create_index('ix_core_banking_config_is_active', 'core_banking_config', ['is_active'], unique=False)
