import mysql.connector
import json

def check_table_data(cursor, table_name):
    """Check if a table exists and has data"""
    try:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        result = cursor.fetchone()
        return result['count'] if result else 0
    except mysql.connector.Error:
        return -1  # Table doesn't exist

try:
    # First check loan_system database configuration
    print("\nChecking loan_system database configuration...")
    loan_system_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'loan_system',
        'auth_plugin': 'mysql_native_password'
    }
    
    conn = mysql.connector.connect(**loan_system_config)
    cursor = conn.cursor(dictionary=True)
    
    # Check core banking system configuration
    cursor.execute("SELECT * FROM core_banking_systems WHERE is_active = 1")
    system = cursor.fetchone()
    
    if not system:
        print("Error: No active core banking system found")
    else:
        print("\nCore Banking System Configuration:")
        print(f"Name: {system['name']}")
        print(f"Base URL: {system['base_url']}")
        print(f"Database: {system['database_name']}")
        
        # Check endpoints
        cursor.execute("""
            SELECT name, path, method, is_active 
            FROM core_banking_endpoints 
            WHERE system_id = %s
        """, (system['id'],))
        
        endpoints = cursor.fetchall()
        print("\nConfigured Endpoints:")
        for ep in endpoints:
            print(f"- {ep['name']} ({ep['path']}) - {'Active' if ep['is_active'] else 'Inactive'}")

        # Connect to core banking database using configuration from database
        print(f"\nChecking {system['database_name']} data...")
        try:
            auth_credentials = json.loads(system['auth_credentials'])
        except (json.JSONDecodeError, TypeError):
            # Default to empty credentials if JSON parsing fails
            auth_credentials = {'username': 'root', 'password': ''}
            
        core_banking_config = {
            'host': system['base_url'],
            'port': system['port'] or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': system['database_name'],
            'auth_plugin': 'mysql_native_password'
        }
        
        core_conn = mysql.connector.connect(**core_banking_config)
        core_cursor = core_conn.cursor(dictionary=True)

        # Check tables
        tables = ['LoanApplications', 'LoanDisbursements', 'LoanLedgerEntries', 'LoanSchedule', 'Members']
        print("\nTable Data Status:")
        for table in tables:
            count = check_table_data(core_cursor, table)
            if count >= 0:
                print(f"- {table}: {count} records")
            else:
                print(f"- {table}: Table not found")

        # Get table structures
        print("\nSample Data Preview:\n")
        for table in tables:
            try:
                core_cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = core_cursor.fetchall()
                print(f"\n{table} Fields:")
                for col in columns:
                    print(f"- {col['Field']}")
            except mysql.connector.Error:
                continue
    
    # Update loan grading endpoint
    print("\nConnecting to loan_system database...")
    cursor.execute("""
        UPDATE core_banking_endpoints 
        SET parameters = %s
        WHERE name = 'loan_grading' AND system_id = %s
    """, (json.dumps({
        "tables": ["LoanLedgerEntries"],
        "fields": [
            "LoanLedgerEntries.LoanID",
            "LoanLedgerEntries.MemberID",
            "LoanLedgerEntries.DisbursedAmount",
            "LoanLedgerEntries.OutstandingBalance",
            "LoanLedgerEntries.ArrearsAmount",
            "LoanLedgerEntries.ArrearsDays",
            "LoanLedgerEntries.InterestAccrued",
            "LoanApplications.LoanNo",
            "LoanApplications.LoanAmount",
            "LoanApplications.RepaymentPeriod",
            "LoanApplications.InterestRate",
            "LoanDisbursements.DisbursementDate",
            "LoanDisbursements.RepaymentStartDate",
            "LoanDisbursements.LoanStatus"
        ],
        "joins": [
            {
                "table": "LoanDisbursements",
                "on": "LoanLedgerEntries.LoanID = LoanDisbursements.LoanAppID"
            },
            {
                "table": "LoanApplications",
                "on": "LoanDisbursements.LoanAppID = LoanApplications.LoanAppID"
            }
        ],
        "filters": {
            "loan_status": {
                "field": "LoanDisbursements.LoanStatus",
                "value": "Active"
            }
        }
    }), system['id']))
    conn.commit()
    
    print("\nLoan grading endpoint updated successfully!")
    print("-" * 70)
    print("Name: loan_grading")
    parameters = {
        'tables': ['LoanLedgerEntries'],
        'fields': [
            'LoanLedgerEntries.LoanID',
            'LoanLedgerEntries.MemberID',
            'LoanLedgerEntries.DisbursedAmount',
            'LoanLedgerEntries.OutstandingBalance',
            'LoanLedgerEntries.ArrearsAmount',
            'LoanLedgerEntries.ArrearsDays',
            'LoanLedgerEntries.InterestAccrued',
            'LoanApplications.LoanNo',
            'LoanApplications.LoanAmount',
            'LoanApplications.RepaymentPeriod',
            'LoanApplications.InterestRate',
            'LoanDisbursements.DisbursementDate',
            'LoanDisbursements.RepaymentStartDate',
            'LoanDisbursements.LoanStatus'
        ],
        'joins': [
            {
                'table': 'LoanDisbursements',
                'on': 'LoanLedgerEntries.LoanID = LoanDisbursements.LoanAppID'
            },
            {
                'table': 'LoanApplications',
                'on': 'LoanDisbursements.LoanAppID = LoanApplications.LoanAppID'
            }
        ],
        'filters': {
            'loan_status': {
                'field': 'LoanDisbursements.LoanStatus',
                'value': 'Active'
            }
        }
    }
    print(f"Parameters: {json.dumps(parameters)}")
    print("-" * 70)

    cursor.close()
    conn.close()
    core_cursor.close()
    core_conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
except Exception as e:
    print(f"Unexpected error: {e}")
