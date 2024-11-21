"""add cascade delete

Revision ID: add_cascade_delete
Revises: 553c90805d53
Create Date: 2024-01-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_cascade_delete'
down_revision = '553c90805d53'
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing foreign key constraints
    op.drop_constraint('modules_parent_id_fkey', 'modules', type_='foreignkey')
    op.drop_constraint('form_fields_module_id_fkey', 'form_fields', type_='foreignkey')
    
    # Re-create foreign key constraints with ON DELETE CASCADE
    op.create_foreign_key(
        'modules_parent_id_fkey', 'modules', 'modules',
        ['parent_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'form_fields_module_id_fkey', 'form_fields', 'modules',
        ['module_id'], ['id'], ondelete='CASCADE'
    )


def downgrade():
    # Drop CASCADE foreign key constraints
    op.drop_constraint('modules_parent_id_fkey', 'modules', type_='foreignkey')
    op.drop_constraint('form_fields_module_id_fkey', 'form_fields', type_='foreignkey')
    
    # Re-create foreign key constraints without ON DELETE CASCADE
    op.create_foreign_key(
        'modules_parent_id_fkey', 'modules', 'modules',
        ['parent_id'], ['id']
    )
    op.create_foreign_key(
        'form_fields_module_id_fkey', 'form_fields', 'modules',
        ['module_id'], ['id']
    )
