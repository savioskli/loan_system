from app import create_app
from extensions import db
from models.product import Product

# Sample loan products
products = [
    {
        'name': 'Personal Loan',
        'code': 'PL001',
        'status': 'Active',
        'interest_rate': '15.5',
        'rate_method': 'Flat Rate',
        'processing_fee': '2%',
        'maintenance_fee': '1%',
        'insurance_fee': '0.5%',
        'frequency': 'Monthly',
        'min_amount': 10000.00,
        'max_amount': 500000.00,
        'min_term': 6,
        'max_term': 36,
        'collateral': 'No collateral required',
        'income_statement': 'Last 3 months payslip required'
    },
    {
        'name': 'Business Loan',
        'code': 'BL001',
        'status': 'Active',
        'interest_rate': '18.0',
        'rate_method': 'Reducing Balance',
        'processing_fee': '2.5%',
        'maintenance_fee': '1.5%',
        'insurance_fee': '1%',
        'frequency': 'Monthly',
        'min_amount': 100000.00,
        'max_amount': 5000000.00,
        'min_term': 12,
        'max_term': 60,
        'collateral': 'Business assets or property',
        'income_statement': 'Business financial statements for last 2 years'
    },
    {
        'name': 'Home Loan',
        'code': 'HL001',
        'status': 'Active',
        'interest_rate': '12.5',
        'rate_method': 'Reducing Balance',
        'processing_fee': '1.5%',
        'maintenance_fee': '0.5%',
        'insurance_fee': '1%',
        'frequency': 'Monthly',
        'min_amount': 500000.00,
        'max_amount': 10000000.00,
        'min_term': 60,
        'max_term': 240,
        'collateral': 'Property being purchased',
        'income_statement': 'Income proof and property valuation required'
    },
    {
        'name': 'Education Loan',
        'code': 'EL001',
        'status': 'Active',
        'interest_rate': '10.0',
        'rate_method': 'Flat Rate',
        'processing_fee': '1%',
        'maintenance_fee': '0.5%',
        'insurance_fee': '0.5%',
        'frequency': 'Monthly',
        'min_amount': 50000.00,
        'max_amount': 1000000.00,
        'min_term': 12,
        'max_term': 72,
        'collateral': 'Parent/Guardian guarantee',
        'income_statement': 'Parent/Guardian income proof and admission letter'
    },
    {
        'name': 'Agriculture Loan',
        'code': 'AL001',
        'status': 'Active',
        'interest_rate': '14.0',
        'rate_method': 'Reducing Balance',
        'processing_fee': '1.5%',
        'maintenance_fee': '1%',
        'insurance_fee': '1.5%',
        'frequency': 'Quarterly',
        'min_amount': 100000.00,
        'max_amount': 2000000.00,
        'min_term': 4,
        'max_term': 20,
        'collateral': 'Farm land or equipment',
        'income_statement': 'Farm income records and business plan'
    }
]

app = create_app()
with app.app_context():
    # First, check if products already exist
    existing_products = Product.query.count()
    if existing_products > 0:
        print(f"Found {existing_products} existing products. Skipping insertion.")
    else:
        # Insert products
        for product_data in products:
            product = Product(**product_data)
            db.session.add(product)
        
        # Commit the changes
        try:
            db.session.commit()
            print(f"Successfully inserted {len(products)} products.")
        except Exception as e:
            db.session.rollback()
            print(f"Error inserting products: {str(e)}")
