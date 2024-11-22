"""Create products table

Revision ID: create_products_table_001
Revises: merge_activity_logs_001
Create Date: 2024-11-21 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'create_products_table_001'
down_revision = 'merge_activity_logs_001'
branch_labels = None
depends_on = None

def upgrade():
    # Create products table
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Active'),
        sa.Column('interest_rate', sa.String(length=10), nullable=True),
        sa.Column('rate_method', sa.String(length=20), nullable=True),
        sa.Column('processing_fee', sa.String(length=50), nullable=True),
        sa.Column('maintenance_fee', sa.String(length=50), nullable=True),
        sa.Column('insurance_fee', sa.String(length=20), nullable=True),
        sa.Column('frequency', sa.String(length=10), nullable=True),
        sa.Column('min_amount', sa.Numeric(precision=20, scale=2), nullable=False, server_default='1.00'),
        sa.Column('max_amount', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('min_term', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('max_term', sa.Integer(), nullable=False),
        sa.Column('collateral', sa.String(length=200), nullable=True),
        sa.Column('bs_income_statement', sa.String(length=20), nullable=False, server_default='Mandatory'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Insert initial product data (sample of key products)
    op.bulk_insert(sa.table('products',
        sa.Column('name', sa.String(100)),
        sa.Column('code', sa.String(10)),
        sa.Column('status', sa.String(20)),
        sa.Column('interest_rate', sa.String(10)),
        sa.Column('rate_method', sa.String(20)),
        sa.Column('processing_fee', sa.String(50)),
        sa.Column('maintenance_fee', sa.String(50)),
        sa.Column('insurance_fee', sa.String(20)),
        sa.Column('frequency', sa.String(10)),
        sa.Column('min_amount', sa.Numeric(20, 2)),
        sa.Column('max_amount', sa.Numeric(20, 2)),
        sa.Column('min_term', sa.Integer),
        sa.Column('max_term', sa.Integer),
        sa.Column('collateral', sa.String(200)),
        sa.Column('bs_income_statement', sa.String(20))
    ), [
        # Sample key products
        {'name': 'BUSINESS LOAN 2', 'code': 'BSL2', 'status': 'Active', 'interest_rate': 'Investa Based', 'rate_method': 'Reducing', 'processing_fee': '2.9%', 'maintenance_fee': 'ksh. 100pm', 'insurance_fee': '0.5%pa', 'frequency': 'M', 'min_amount': 1.00, 'max_amount': 9999999999.00, 'min_term': 1, 'max_term': 36, 'collateral': 'Above ksh. 200,000.00', 'bs_income_statement': 'Mandatory'},
        {'name': 'SALARY LOANS 2', 'code': 'SAL2', 'status': 'Active', 'interest_rate': 'Investa Based', 'rate_method': 'Reducing', 'processing_fee': '2.9%', 'maintenance_fee': 'ksh. 100pm', 'insurance_fee': '0.5%pa', 'frequency': 'M', 'min_amount': 1.00, 'max_amount': 99999999999.00, 'min_term': 1, 'max_term': 36, 'collateral': 'Above ksh. 200,000.00', 'bs_income_statement': 'Exempted'},
        {'name': 'STAFF LOAN', 'code': 'STL', 'status': 'Active', 'interest_rate': '10%pa', 'rate_method': 'Reducing', 'processing_fee': '0.5% min ksh. 1,000', 'maintenance_fee': 'ksh. 50 pm', 'insurance_fee': '0.5%pa', 'frequency': 'M', 'min_amount': 1.00, 'max_amount': 999999999999.00, 'min_term': 1, 'max_term': 60, 'collateral': 'Above ksh. 500,000.00', 'bs_income_statement': 'Exempted'},
        {'name': 'AMICASH LOAN', 'code': 'AMKL', 'status': 'Active', 'interest_rate': '6%pm', 'rate_method': 'FLAT', 'processing_fee': '2.9%', 'maintenance_fee': 'n/a', 'insurance_fee': 'n/a', 'frequency': 'M', 'min_amount': 500.00, 'max_amount': 40000.00, 'min_term': 1, 'max_term': 1, 'collateral': 'full amount', 'bs_income_statement': 'Exempted'},
        {'name': 'SCHOOL FEES LOAN', 'code': 'SFL', 'status': 'Active', 'interest_rate': '24%pa', 'rate_method': 'FLAT', 'processing_fee': '2.9%', 'maintenance_fee': 'ksh. 100pm', 'insurance_fee': '0.5%pa', 'frequency': 'M', 'min_amount': 100.00, 'max_amount': 999999999.00, 'min_term': 1, 'max_term': 12, 'collateral': 'Above ksh. 200,000.00', 'bs_income_statement': 'Mandatory'}
    ])

def downgrade():
    op.drop_table('products')
