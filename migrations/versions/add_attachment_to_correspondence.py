"""add attachment to correspondence

Revision ID: add_attachment_to_correspondence
Revises: create_correspondence_table
Create Date: 2024-12-22 20:49:24.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_attachment_to_correspondence'
down_revision = 'create_correspondence_table'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('correspondence', sa.Column('attachment_path', sa.String(500)))

def downgrade():
    op.drop_column('correspondence', 'attachment_path')
