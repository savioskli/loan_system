"""create client attachments table

Revision ID: create_client_attachments
Revises: None
Create Date: 2025-05-21 14:42:20.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_client_attachments'
down_revision = None

def upgrade():
    op.create_table('client_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_type_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('attachment_type', sa.String(length=50), nullable=False),
        sa.Column('size_limit', sa.Integer(), nullable=True),
        sa.Column('is_mandatory', sa.Boolean(), default=False),
        sa.Column('status', sa.String(length=20), default='active'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['client_type_id'], ['client_types.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['staff.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['staff.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_client_attachments_client_type_id', 'client_attachments', ['client_type_id'])

def downgrade():
    op.drop_index('ix_client_attachments_client_type_id')
    op.drop_table('client_attachments')
