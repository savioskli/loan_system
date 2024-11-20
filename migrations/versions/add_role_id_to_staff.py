"""add role_id to staff

Revision ID: add_role_id_to_staff
Revises: 14f1ffd2f25e
Create Date: 2024-11-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_role_id_to_staff'
down_revision = '14f1ffd2f25e'
branch_labels = None
depends_on = None


def upgrade():
    # Create a temporary role column to store the old role values
    op.add_column('staff', sa.Column('old_role', sa.String(20), nullable=True))
    
    # Copy data from role to old_role
    op.execute('UPDATE staff SET old_role = role')
    
    # Drop the old role column
    op.drop_column('staff', 'role')
    
    # Add the new role_id column
    op.add_column('staff', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_staff_role_id', 'staff', 'roles', ['role_id'], ['id'])
    
    # Create default roles if they don't exist
    op.execute("""
        INSERT IGNORE INTO roles (name, description, is_active, created_at)
        VALUES 
        ('admin', 'Administrator role with full access', 1, NOW()),
        ('staff', 'Default staff role', 1, NOW())
    """)
    
    # Update role_id based on old_role values
    op.execute("""
        UPDATE staff s
        JOIN roles r ON LOWER(s.old_role) = LOWER(r.name)
        SET s.role_id = r.id
    """)
    
    # Set remaining NULL role_ids to the default staff role
    op.execute("""
        UPDATE staff s
        SET s.role_id = (SELECT id FROM roles WHERE name = 'staff')
        WHERE s.role_id IS NULL
    """)
    
    # Make role_id not nullable
    op.alter_column('staff', 'role_id',
               existing_type=sa.Integer(),
               nullable=False)
    
    # Drop the temporary old_role column
    op.drop_column('staff', 'old_role')


def downgrade():
    # Create the old role column
    op.add_column('staff', sa.Column('role', sa.String(20), nullable=True))
    
    # Copy role names from roles table
    op.execute("""
        UPDATE staff s
        JOIN roles r ON s.role_id = r.id
        SET s.role = r.name
    """)
    
    # Make role not nullable and set default
    op.alter_column('staff', 'role',
               existing_type=sa.String(20),
               nullable=False,
               server_default='staff')
    
    # Drop the role_id foreign key and column
    op.drop_constraint('fk_staff_role_id', 'staff', type_='foreignkey')
    op.drop_column('staff', 'role_id')
