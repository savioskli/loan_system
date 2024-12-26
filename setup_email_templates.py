import mysql.connector
from datetime import datetime
from config import db_config  # Import database configuration

# SQL for creating the email_templates table
create_table_sql = """
CREATE TABLE IF NOT EXISTS email_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_value INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# Sample templates
sample_templates = [
    {
        'name': 'Payment Due Reminder',
        'category': 'payment',
        'subject': 'Payment Reminder: Loan Payment Due Soon',
        'message': '''Dear {customer_name},

Your loan payment of {amount_due} for loan {loan_id} is due on {due_date}.

Please ensure timely payment to maintain a good credit record. You can make your payment through any of our approved payment channels.

Payment Details:
- Amount Due: {amount_due}
- Due Date: {due_date}
- Loan ID: {loan_id}

If you have already made the payment, please disregard this reminder.

Best regards,
The Loan Team''',
        'trigger_type': 'days_before',
        'trigger_value': 3
    },
    {
        'name': 'Payment Overdue Notice',
        'category': 'overdue',
        'subject': 'URGENT: Loan Payment Overdue Notice',
        'message': '''Dear {customer_name},

This is to inform you that your loan payment of {amount_due} for loan {loan_id} is now overdue by {days_overdue} days.

Please make the payment immediately to avoid:
- Additional late payment charges
- Negative impact on your credit score
- Potential legal action

Payment Details:
- Overdue Amount: {amount_due}
- Days Overdue: {days_overdue}
- Loan ID: {loan_id}

If you are experiencing financial difficulties, please contact our customer service team to discuss payment arrangements.

Best regards,
The Loan Team''',
        'trigger_type': 'days_after',
        'trigger_value': 1
    },
    {
        'name': 'Loan Approval Notification',
        'category': 'approval',
        'subject': 'Congratulations! Your Loan Has Been Approved',
        'message': '''Dear {customer_name},

We are pleased to inform you that your loan application has been approved!

Loan Details:
- Loan Amount: {loan_amount}
- Interest Rate: {interest_rate}%
- Loan Term: {loan_term} months
- Monthly Payment: {monthly_payment}

Next Steps:
1. Review and sign the loan agreement
2. Provide any remaining documentation
3. Confirm your disbursement details

The funds will be disbursed to your account within 24-48 hours after completing these steps.

Best regards,
The Loan Team''',
        'trigger_type': 'event',
        'trigger_value': 0
    },
    {
        'name': 'High NPL Alert',
        'category': 'alert',
        'subject': 'ALERT: High NPL Ratio Detected',
        'message': '''ATTENTION: Risk Management Team

This is an automated alert to inform you that the Non-Performing Loan (NPL) ratio has exceeded the defined threshold.

Current Status:
- NPL Ratio: {npl_ratio}%
- Threshold: {threshold}%
- Date: {current_date}

Required Actions:
1. Review the loan portfolio immediately
2. Identify high-risk accounts
3. Implement necessary risk mitigation measures
4. Prepare a detailed report for management

Please address this situation urgently to maintain portfolio quality.

System Generated Alert''',
        'trigger_type': 'threshold',
        'trigger_value': 5
    },
    {
        'name': 'Welcome Email',
        'category': 'onboarding',
        'subject': 'Welcome to Our Loan Service',
        'message': '''Dear {customer_name},

Welcome to our loan service! We're excited to have you as a new customer.

Your account has been successfully created with the following details:
- Account Number: {account_number}
- Registration Date: {registration_date}

Here's what you can do with your account:
1. Apply for loans
2. Track your loan applications
3. Make payments
4. View your loan history
5. Update your profile

If you have any questions, our customer service team is available 24/7 to assist you.

Best regards,
The Loan Team''',
        'trigger_type': 'event',
        'trigger_value': 0
    }
]

def setup_database():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create the table
        print("Creating email_templates table...")
        cursor.execute(create_table_sql)

        # Insert sample templates
        insert_sql = """
        INSERT INTO email_templates (name, category, subject, message, trigger_type, trigger_value)
        VALUES (%(name)s, %(category)s, %(subject)s, %(message)s, %(trigger_type)s, %(trigger_value)s)
        """
        
        print("Inserting sample templates...")
        for template in sample_templates:
            cursor.execute(insert_sql, template)

        # Commit the changes
        conn.commit()
        print("Database setup completed successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database()
