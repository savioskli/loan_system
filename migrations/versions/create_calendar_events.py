"""create calendar events table

Revision ID: create_calendar_events
Revises: add_attachment_path
Create Date: 2024-12-23 20:21:03.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_calendar_events'
down_revision = 'add_attachment_path'
branch_labels = None
depends_on = None


def upgrade():
    # Create calendar_events table
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('all_day', sa.Boolean(), default=False),
        sa.Column('status', sa.String(length=20), default='scheduled'),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('loan_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['created_by_id'], ['staff.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['loan_id'], ['loans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_calendar_events_start_time', 'start_time'),
        sa.Index('idx_calendar_events_created_by', 'created_by_id'),
        sa.Index('idx_calendar_events_client', 'client_id'),
        sa.Index('idx_calendar_events_loan', 'loan_id')
    )


def downgrade():
    # Drop calendar_events table
    op.drop_table('calendar_events')
