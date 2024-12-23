from datetime import datetime, timedelta
import random
import mysql.connector
from mysql.connector import Error

# Mock data
MOCK_CLIENTS = [
    {
        'id': 1,
        'name': 'John Smith',
        'phone': '+254712345678',
        'email': 'john.smith@example.com'
    },
    {
        'id': 2,
        'name': 'Mary Johnson',
        'phone': '+254723456789',
        'email': 'mary.j@example.com'
    },
    {
        'id': 3,
        'name': 'Acme Corporation',
        'phone': '+254734567890',
        'email': 'info@acme.com'
    },
    {
        'id': 4,
        'name': 'Sarah Wilson',
        'phone': '+254745678901',
        'email': 'sarah.w@example.com'
    },
    {
        'id': 5,
        'name': 'Tech Solutions Ltd',
        'phone': '+254756789012',
        'email': 'contact@techsolutions.com'
    }
]

# Sample data for correspondence
correspondence_types = ['SMS', 'Email', 'Call', 'Visit']
statuses = ['Sent', 'Delivered', 'Failed', 'Pending']
call_outcomes = ['Answered', 'No Answer', 'Busy', 'Voicemail']
visit_outcomes = ['Met Client', 'Client Unavailable', 'Rescheduled', 'Successful']
visit_purposes = ['Collection', 'Document Collection', 'Loan Restructuring Discussion', 'General Follow-up']

# Sample messages for each type
sms_messages = [
    "Your loan payment of {amount} is due on {date}. Please ensure timely payment to avoid penalties.",
    "Reminder: Your loan installment of {amount} is overdue. Please make the payment as soon as possible.",
    "Thank you for your recent payment of {amount}. Your next installment is due on {date}.",
]

email_messages = [
    "Dear {client},\n\nThis is a reminder that your loan payment of {amount} is due on {date}. Please ensure timely payment to maintain a good credit record.\n\nBest regards,\nLoan Department",
    "Dear {client},\n\nWe notice that your loan payment of {amount} is overdue. Please contact us immediately to discuss payment arrangements.\n\nBest regards,\nLoan Department",
]

call_messages = [
    "Called to discuss overdue payment of {amount}",
    "Follow-up call regarding loan restructuring",
    "Called to verify payment of {amount}",
]

visit_messages = [
    "Site visit for loan follow-up - discussed payment schedule",
    "Met client to collect overdue payment of {amount}",
    "Visit for document collection and verification",
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
        
        # Get loan IDs from database
        cursor.execute("SELECT id, account_no FROM loans")
        db_loans = cursor.fetchall()
        
        if not db_loans:
            print("Please ensure there are loans in the database first.")
            exit(1)
            
        current_time = datetime.utcnow()
        
        # Create sample correspondence records
        for _ in range(50):
            loan = random.choice(db_loans)
            client = random.choice(MOCK_CLIENTS)
            corr_type = random.choice(correspondence_types)
            
            # Get amount and date for message formatting
            amount = f"${random.randint(100, 10000):,}"
            date = (current_time + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            
            # Select message based on type
            if corr_type == 'SMS':
                message = random.choice(sms_messages)
            elif corr_type == 'Email':
                message = random.choice(email_messages)
            elif corr_type == 'Call':
                message = random.choice(call_messages)
            else:  # Visit
                message = random.choice(visit_messages)
            
            # Format message with placeholders
            message = message.format(
                amount=amount,
                date=date,
                client=client['name']
            )
            
            # Insert correspondence record
            insert_query = """
            INSERT INTO correspondence (
                account_no, client_name, type, message, status, sent_by,
                created_at, recipient, delivery_status, delivery_time,
                call_duration, call_outcome, location, visit_purpose,
                visit_outcome, staff_id, loan_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            values = (
                loan['account_no'],
                client['name'],
                corr_type,
                message,
                random.choice(statuses),
                'admin',  # Using the existing admin user
                current_time - timedelta(days=random.randint(0, 30)),
                client['email'] if corr_type == 'Email' else client['phone'],
                'Delivered' if random.random() > 0.2 else 'Failed',
                current_time - timedelta(minutes=random.randint(1, 60)),
                random.randint(60, 600) if corr_type == 'Call' else None,
                random.choice(call_outcomes) if corr_type == 'Call' else None,
                f"Client Office" if corr_type == 'Visit' else None,
                random.choice(visit_purposes) if corr_type == 'Visit' else None,
                random.choice(visit_outcomes) if corr_type == 'Visit' else None,
                1,  # Using the existing admin user ID
                loan['id']
            )
            
            cursor.execute(insert_query, values)
        
        # Commit the transaction
        connection.commit()
        print(f"Successfully created 50 sample correspondence records")

except Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Database connection closed.")
