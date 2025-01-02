"""fix core banking endpoints table

Revision ID: fix_core_banking_endpoints
Revises: update_core_banking_tables
Create Date: 2024-12-31 13:37:13.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_core_banking_endpoints'
down_revision = 'update_core_banking_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing core_banking_endpoints table if it exists
    op.execute('DROP TABLE IF EXISTS core_banking_endpoints CASCADE')
    
    # Create core_banking_endpoints table with correct schema
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

    # Recreate indexes
    op.create_index('ix_core_banking_endpoints_is_active', 'core_banking_endpoints', ['is_active'])
    op.create_index('ix_core_banking_endpoints_system_id', 'core_banking_endpoints', ['system_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_core_banking_endpoints_system_id')
    op.drop_index('ix_core_banking_endpoints_is_active')
    
    # Drop table
    op.drop_table('core_banking_endpoints')
