from datetime import datetime, timedelta
import random
import mysql.connector
from mysql.connector import Error

# Sample loan data from mock database
SAMPLE_LOANS = [
    {
        'account_no': 'LN00000001',
        'amount': 500000.00,
        'client_name': 'John Kamau',
        'days_in_arrears': 0,
        'classification': 'NORMAL',
        'product_id': 2  # Personal Loan
    },
    {
        'account_no': 'LN00000002',
        'amount': 750000.00,
        'client_name': 'Jane Wanjiku',
        'days_in_arrears': 45,
        'classification': 'WATCH',
        'product_id': 1  # Business Loan
    },
    {
        'account_no': 'LN00000003',
        'amount': 1000000.00,
        'client_name': 'Peter Omondi',
        'days_in_arrears': 120,
        'classification': 'SUBSTANDARD',
        'product_id': 4  # SME Loan
    },
    {
        'account_no': 'LN00000004',
        'amount': 300000.00,
        'client_name': 'Mary Muthoni',
        'days_in_arrears': 250,
        'classification': 'DOUBTFUL',
        'product_id': 5  # Emergency Loan
    },
    {
        'account_no': 'LN00000005',
        'amount': 1500000.00,
        'client_name': 'James Kiprop',
        'days_in_arrears': 400,
        'classification': 'LOSS',
        'product_id': 3  # Agriculture Loan
    }
]

try:
    # Connect to the database
    connection = mysql.connector.connect(
        host='localhost',
        database='loan_system',
        user='root',
        password=''
    )

    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        current_time = datetime.utcnow()
        
        # Get client IDs from database
        cursor.execute("SELECT id FROM clients LIMIT 5")
        clients = cursor.fetchall()
        
        if not clients:
            print("Please ensure there are clients in the database first.")
            exit(1)
        
        # Create sample loans
        for i, loan_data in enumerate(SAMPLE_LOANS):
            client = clients[i % len(clients)]
            disbursement_date = current_time - timedelta(days=loan_data['days_in_arrears'] + random.randint(30, 90))
            maturity_date = disbursement_date + timedelta(days=365)  # 1 year term
            
            # Calculate outstanding balance based on classification
            outstanding_percent = {
                'NORMAL': 0.95,
                'WATCH': 0.85,
                'SUBSTANDARD': 0.70,
                'DOUBTFUL': 0.50,
                'LOSS': 0.30
            }
            outstanding_balance = loan_data['amount'] * outstanding_percent[loan_data['classification']]
            total_in_arrears = loan_data['amount'] * (1 - outstanding_percent[loan_data['classification']])
            
            # Insert loan record
            insert_query = """
            INSERT INTO loans (
                account_no, client_id, product_id, amount, interest_rate, term,
                disbursement_date, maturity_date, status,
                outstanding_balance, total_in_arrears, days_in_arrears,
                classification, created_at, updated_at, created_by, updated_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            values = (
                loan_data['account_no'],
                client['id'],
                loan_data['product_id'],
                loan_data['amount'],
                15.0,  # Standard interest rate
                12,    # 12 months term
                disbursement_date,
                maturity_date,
                'Active',
                outstanding_balance,
                total_in_arrears,
                loan_data['days_in_arrears'],
                loan_data['classification'],
                current_time,
                current_time,
                1,  # Created by admin
                1   # Updated by admin
            )
            
            cursor.execute(insert_query, values)
        
        # Commit the transaction
        connection.commit()
        print(f"Successfully created {len(SAMPLE_LOANS)} sample loan records")

except Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Database connection closed.")
