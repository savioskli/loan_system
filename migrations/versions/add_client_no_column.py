"""add client_no column

Revision ID: add_client_no_column
Revises: create_correspondence_table
Create Date: 2024-12-22 20:33:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_client_no_column'
down_revision = 'create_correspondence_table'
branch_labels = None
depends_on = None

def upgrade():
    # Add client_no column
    op.add_column('clients', sa.Column('client_no', sa.String(50), nullable=True))
    
    # Generate client numbers for existing clients
    connection = op.get_bind()
    connection.execute("""
        UPDATE clients 
        SET client_no = CONCAT('CL', LPAD(id, 6, '0'))
        WHERE client_no IS NULL
    """)
    
    # Make the column non-nullable and unique after populating it
    op.alter_column('clients', 'client_no',
                    existing_type=sa.String(50),
                    nullable=False)
    op.create_unique_constraint('uq_clients_client_no', 'clients', ['client_no'])

def downgrade():
    op.drop_constraint('uq_clients_client_no', 'clients', type_='unique')
    op.drop_column('clients', 'client_no')
