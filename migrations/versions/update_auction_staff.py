"""Update auction staff assignments

Revision ID: update_auction_staff
Revises: 
Create Date: 2025-05-07 15:20:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'update_auction_staff'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create a temp table for the auctions
    auctions = table('auction',
        column('id', sa.Integer),
        column('assigned_staff_name', sa.String),
        column('supervisor_name', sa.String)
    )

    # Update auctions where staff names are NULL or empty
    op.execute(
        auctions.update().where(
            sa.or_(
                auctions.c.assigned_staff_name == None,
                auctions.c.assigned_staff_name == ''
            )
        ).values(
            assigned_staff_name='System User',
            supervisor_name='Not Assigned'
        )
    )

def downgrade():
    pass
