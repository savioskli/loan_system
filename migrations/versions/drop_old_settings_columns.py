"""Drop old settings columns

Revision ID: drop_old_settings_columns
Revises: add_updated_fields
Create Date: 2024-11-20 22:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'drop_old_settings_columns'
down_revision = 'add_updated_fields'
branch_labels = None
depends_on = None

def column_exists(table_name, column_name):
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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

    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        if not column_exists('system_settings', 'description'):
            batch_op.add_column(sa.Column('description', mysql.TEXT(), nullable=True))
        if not column_exists('system_settings', 'category'):
            batch_op.add_column(sa.Column('category', mysql.VARCHAR(length=50), nullable=True))
        if not column_exists('system_settings', 'setting_type'):
            batch_op.add_column(sa.Column('setting_type', mysql.VARCHAR(length=20), nullable=True))
        if not column_exists('system_settings', 'setting_value'):
            batch_op.add_column(sa.Column('setting_value', mysql.TEXT(), nullable=True))
        if not column_exists('system_settings', 'setting_key'):
            batch_op.add_column(sa.Column('setting_key', mysql.VARCHAR(length=100), nullable=True))

    # ### end Alembic commands ###