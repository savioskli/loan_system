"""fix role columns

Revision ID: fix_role_columns
Revises: a5ec725474b9
Create Date: 2024-11-20 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fix_role_columns'
down_revision = 'a5ec725474b9'
branch_labels = None
depends_on = None


def upgrade():
    # Make sure all necessary columns exist in roles table
    with op.batch_alter_table('roles') as batch_op:
        # Add columns if they don't exist
        columns = [
            sa.Column('created_at', sa.DateTime, nullable=True),
            sa.Column('updated_at', sa.DateTime, nullable=True),
            sa.Column('created_by', sa.Integer, nullable=True),
            sa.Column('updated_by', sa.Integer, nullable=True),
            sa.Column('is_active', sa.Boolean, nullable=False, server_default='1'),
            sa.Column('description', sa.String(200), nullable=True)
        ]
        
        for column in columns:
            try:
                batch_op.add_column(column)
            except Exception:
                pass  # Column might already exist

    # Add foreign key constraints if they don't exist
    try:
        op.create_foreign_key(
            'fk_roles_created_by_staff',
            'roles', 'staff',
            ['created_by'], ['id']
        )
    except Exception:
        pass

    try:
        op.create_foreign_key(
            'fk_roles_updated_by_staff',
            'roles', 'staff',
            ['updated_by'], ['id']
        )
    except Exception:
        pass

    # Update timestamps for any null values
    op.execute("""
        UPDATE roles 
        SET created_at = NOW() 
        WHERE created_at IS NULL
    """)
    
    op.execute("""
        UPDATE roles 
        SET updated_at = NOW() 
        WHERE updated_at IS NULL
    """)


def downgrade():
    # Remove foreign key constraints
    with op.batch_alter_table('roles') as batch_op:
        try:
            batch_op.drop_constraint('fk_roles_created_by_staff', type_='foreignkey')
        except Exception:
            pass
        try:
            batch_op.drop_constraint('fk_roles_updated_by_staff', type_='foreignkey')
        except Exception:
            pass
