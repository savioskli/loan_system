"""add organization id columns

Revision ID: add_organization_id_columns
Revises: merge_all_heads
Create Date: 2025-05-22 12:01:29.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_organization_id_columns'
down_revision = 'merge_all_heads'
branch_labels = None
depends_on = None


def upgrade():
    # Add organization_id column to modules table
    op.add_column('modules',
        sa.Column('organization_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_modules_organization_id',
        'modules', 'organizations',
        ['organization_id'], ['id'],
        ondelete='CASCADE'
    )
    # Make organization_id non-nullable after adding the column
    op.execute('UPDATE modules SET organization_id = (SELECT id FROM organizations LIMIT 1)')
    op.alter_column('modules', 'organization_id',
        existing_type=sa.Integer(),
        nullable=False
    )

    # Add organization_id column to staff table
    op.add_column('staff',
        sa.Column('organization_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_staff_organization_id',
        'staff', 'organizations',
        ['organization_id'], ['id'],
        ondelete='CASCADE'
    )
    # Make organization_id non-nullable after adding the column
    op.execute('UPDATE staff SET organization_id = (SELECT id FROM organizations LIMIT 1)')
    op.alter_column('staff', 'organization_id',
        existing_type=sa.Integer(),
        nullable=False
    )


def downgrade():
    # Remove foreign key constraints first
    op.drop_constraint('fk_modules_organization_id', 'modules', type_='foreignkey')
    op.drop_constraint('fk_staff_organization_id', 'staff', type_='foreignkey')
    
    # Then remove the columns
    op.drop_column('modules', 'organization_id')
    op.drop_column('staff', 'organization_id')
