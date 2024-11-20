"""Fix settings columns

Revision ID: fix_settings_columns
Revises: 75259a57969d
Create Date: 2024-11-20 22:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'fix_settings_columns'
down_revision = '75259a57969d'
branch_labels = None
depends_on = None

def column_exists(table_name, column_name):
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    # Only copy data if both old and new columns exist
    if column_exists('system_settings', 'setting_key') and column_exists('system_settings', 'key'):
        op.execute("""
            UPDATE system_settings 
            SET `key` = setting_key, 
                `value` = setting_value 
            WHERE `key` IS NULL
        """)
    
    # Drop old columns if they exist
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        if column_exists('system_settings', 'setting_key'):
            batch_op.drop_column('setting_key')
        if column_exists('system_settings', 'setting_value'):
            batch_op.drop_column('setting_value')
        if column_exists('system_settings', 'setting_type'):
            batch_op.drop_column('setting_type')
        if column_exists('system_settings', 'category'):
            batch_op.drop_column('category')
        if column_exists('system_settings', 'description'):
            batch_op.drop_column('description')

def downgrade():
    # Add back old columns
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        if not column_exists('system_settings', 'setting_key'):
            batch_op.add_column(sa.Column('setting_key', mysql.VARCHAR(length=100), nullable=True))
        if not column_exists('system_settings', 'setting_value'):
            batch_op.add_column(sa.Column('setting_value', mysql.TEXT(), nullable=True))
        if not column_exists('system_settings', 'setting_type'):
            batch_op.add_column(sa.Column('setting_type', mysql.VARCHAR(length=20), nullable=True))
        if not column_exists('system_settings', 'category'):
            batch_op.add_column(sa.Column('category', mysql.VARCHAR(length=50), nullable=True))
        if not column_exists('system_settings', 'description'):
            batch_op.add_column(sa.Column('description', mysql.VARCHAR(length=200), nullable=True))
    
    # Copy data back to old columns if both exist
    if column_exists('system_settings', 'setting_key') and column_exists('system_settings', 'key'):
        op.execute("""
            UPDATE system_settings 
            SET setting_key = `key`, 
                setting_value = `value`
        """)
