"""Update auction table names

Revision ID: update_auction_table_names
Revises: 
Create Date: 2025-05-07 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_auction_table_names'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Rename tables to match SQLAlchemy model names
    op.rename_table('auction_history', 'auction_history_old')
    op.rename_table('auction_history_attachment', 'auction_history_attachments_old')
    
    # Create new tables with correct names
    op.create_table('auction_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('auction_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['auction_id'], ['auction.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('auction_history_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('history_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['history_id'], ['auction_history.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data from old tables to new tables
    op.execute('''
        INSERT INTO auction_history (id, auction_id, action, description, created_at, created_by)
        SELECT id, auction_id, action, description, created_at, created_by
        FROM auction_history_old
    ''')
    
    op.execute('''
        INSERT INTO auction_history_attachments (id, history_id, file_name, file_path, file_type, uploaded_at)
        SELECT id, history_id, file_name, file_path, file_type, uploaded_at
        FROM auction_history_attachments_old
    ''')
    
    # Drop old tables
    op.drop_table('auction_history_old')
    op.drop_table('auction_history_attachments_old')

def downgrade():
    # This is a one-way migration, downgrade is not supported
    pass
