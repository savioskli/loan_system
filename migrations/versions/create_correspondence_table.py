"""create correspondence table

Revision ID: create_correspondence_table
Revises: merge_all_heads
Create Date: 2024-12-22 19:39:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'create_correspondence_table'
down_revision = 'merge_all_heads'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'correspondence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_no', sa.String(50), nullable=False),
        sa.Column('client_name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('sent_by', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('recipient', sa.String(100)),
        sa.Column('delivery_status', sa.String(50)),
        sa.Column('delivery_time', sa.DateTime),
        sa.Column('call_duration', sa.Integer),
        sa.Column('call_outcome', sa.String(50)),
        sa.Column('location', sa.String(200)),
        sa.Column('visit_purpose', sa.String(200)),
        sa.Column('visit_outcome', sa.String(200)),
        sa.Column('staff_id', sa.Integer, sa.ForeignKey('staff.id'), nullable=False),
        sa.Column('loan_id', sa.Integer, sa.ForeignKey('loans.id'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('correspondence')
