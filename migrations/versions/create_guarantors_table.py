"""Create guarantors table

Revision ID: create_guarantors_table
Revises: create_thresholds
Create Date: 2024-12-30 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_guarantors_table'
down_revision = 'create_thresholds'
branch_labels = None
depends_on = None


def upgrade():
    # Create guarantors table
    op.create_table('guarantors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guarantor_no', sa.String(length=20), nullable=False),
        sa.Column('customer_no', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('id_no', sa.String(length=20), nullable=False),
        sa.Column('phone_no', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=80), nullable=True),
        sa.Column('relationship', sa.String(length=50), nullable=True),
        sa.Column('occupation', sa.String(length=50), nullable=True),
        sa.Column('monthly_income', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_no'], ['clients.client_no'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('guarantor_no'),
        sa.UniqueConstraint('id_no')
    )


def downgrade():
    # Drop guarantors table
    op.drop_table('guarantors')
