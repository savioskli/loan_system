"""Update auction staff foreign keys

Revision ID: update_auction_staff_foreign_keys
Revises: 
Create Date: 2025-05-07 15:50:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_auction_staff_foreign_keys'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop old columns
    op.drop_column('auction', 'assigned_staff_name')
    op.drop_column('auction', 'supervisor_name')
    
    # Modify staff ID columns to have foreign key constraints
    op.alter_column('auction', 'assigned_staff_id',
        existing_type=sa.Integer(),
        nullable=True
    )
    op.alter_column('auction', 'supervisor_id',
        existing_type=sa.Integer(),
        nullable=True
    )
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_auction_assigned_staff', 'auction', 'staff',
        ['assigned_staff_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_auction_supervisor', 'auction', 'staff',
        ['supervisor_id'], ['id'], ondelete='SET NULL'
    )

def downgrade():
    # Remove foreign key constraints
    op.drop_constraint('fk_auction_assigned_staff', 'auction', type_='foreignkey')
    op.drop_constraint('fk_auction_supervisor', 'auction', type_='foreignkey')
    
    # Add back the name columns
    op.add_column('auction', sa.Column('assigned_staff_name', sa.String(100)))
    op.add_column('auction', sa.Column('supervisor_name', sa.String(100)))
