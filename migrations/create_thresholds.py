"""create thresholds table

Revision ID: create_thresholds
Revises: create_email_templates
Create Date: 2024-12-26 14:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'create_thresholds'
down_revision = 'create_email_templates'
branch_labels = None
depends_on = None

def upgrade():
    # Create thresholds table
    op.create_table(
        'thresholds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('npl_ratio', sa.Float(), nullable=False, comment='Non-Performing Loan Ratio (%)'),
        sa.Column('coverage_ratio', sa.Float(), nullable=False, comment='Coverage Ratio (%)'),
        sa.Column('par_ratio', sa.Float(), nullable=False, comment='Portfolio at Risk Ratio (%)'),
        sa.Column('cost_of_risk', sa.Float(), nullable=False, comment='Cost of Risk (%)'),
        sa.Column('recovery_rate', sa.Float(), nullable=False, comment='Recovery Rate (%)'),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_to', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id')
    )

    # Add index for faster queries on validity period
    op.create_index(
        'idx_thresholds_validity',
        'thresholds',
        ['valid_from', 'valid_to', 'is_active']
    )

    # Insert default values
    op.execute("""
        INSERT INTO thresholds (
            npl_ratio, coverage_ratio, par_ratio, cost_of_risk, recovery_rate, valid_from
        ) VALUES (
            5.0, 100.0, 10.0, 2.0, 90.0, CURRENT_TIMESTAMP
        )
    """)

def downgrade():
    op.drop_index('idx_thresholds_validity')
    op.drop_table('thresholds')
