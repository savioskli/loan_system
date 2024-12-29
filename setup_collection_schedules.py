import mysql.connector
from datetime import datetime
from config import db_config  # Import database configuration

# SQL for creating the collection_schedules table
create_table_sql = """
CREATE TABLE IF NOT EXISTS collection_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    loan_id INT NOT NULL,
    supervisor_id INT,
    
    -- Collection Staff Assignment
    assigned_branch VARCHAR(100) NOT NULL,
    assignment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    follow_up_deadline DATETIME NOT NULL,
    collection_priority VARCHAR(20) NOT NULL COMMENT 'High, Medium, Low',
    
    -- Follow-up Plan
    follow_up_frequency VARCHAR(20) NOT NULL COMMENT 'Daily, Weekly, Bi-Weekly',
    next_follow_up_date DATETIME NOT NULL,
    preferred_collection_method VARCHAR(50) NOT NULL COMMENT 'Phone Call, Physical Visit, Legal Action',
    promised_payment_date DATETIME,
    attempts_allowed INT NOT NULL DEFAULT 3,
    attempts_made INT NOT NULL DEFAULT 0,
    
    -- Task & Progress Tracking
    task_description TEXT,
    progress_status VARCHAR(20) NOT NULL DEFAULT 'Not Started' COMMENT 'Not Started, In Progress, Completed, Escalated',
    escalation_level INT,
    resolution_date DATETIME,
    
    -- Supervisor/Manager Review
    reviewed_by INT,
    approval_date DATETIME,
    special_instructions TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (staff_id) REFERENCES staff(id),
    FOREIGN KEY (loan_id) REFERENCES loans(id),
    FOREIGN KEY (supervisor_id) REFERENCES staff(id),
    FOREIGN KEY (reviewed_by) REFERENCES staff(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

def setup_database():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Drop existing table if it exists
        print("Dropping existing collection_schedules table if it exists...")
        cursor.execute("DROP TABLE IF EXISTS collection_schedules")

        # Create the table
        print("Creating collection_schedules table...")
        cursor.execute(create_table_sql)

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

def insert_sample_data():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # First, get some staff IDs from the staff table
        cursor.execute("SELECT id FROM staff LIMIT 5")
        staff_ids = [row[0] for row in cursor.fetchall()]

        if not staff_ids:
            print("No staff members found in the database!")
            return

        # Get some loan IDs
        cursor.execute("SELECT id FROM loans LIMIT 10")
        loan_ids = [row[0] for row in cursor.fetchall()]

        if not loan_ids:
            print("No loans found in the database!")
            return

        print(f"Found {len(staff_ids)} staff members and {len(loan_ids)} loans")

        # Sample data with varied scenarios
        sample_schedules = [
            {
                'staff_id': staff_ids[0],
                'loan_id': loan_ids[0],
                'supervisor_id': staff_ids[1],
                'assigned_branch': 'Main Branch',
                'follow_up_deadline': '2024-01-15 14:00:00',
                'collection_priority': 'High',
                'follow_up_frequency': 'Daily',
                'next_follow_up_date': '2024-01-02 10:00:00',
                'preferred_collection_method': 'Phone Call',
                'promised_payment_date': '2024-01-20 00:00:00',
                'attempts_allowed': 5,
                'attempts_made': 2,
                'task_description': 'Follow up on overdue loan payment - Customer promised to pay',
                'progress_status': 'In Progress',
                'special_instructions': 'Customer prefers morning calls before 10 AM'
            },
            {
                'staff_id': staff_ids[1],
                'loan_id': loan_ids[1],
                'supervisor_id': staff_ids[1],
                'assigned_branch': 'Downtown Branch',
                'follow_up_deadline': '2024-01-20 16:00:00',
                'collection_priority': 'Medium',
                'follow_up_frequency': 'Weekly',
                'next_follow_up_date': '2024-01-05 11:00:00',
                'preferred_collection_method': 'Physical Visit',
                'attempts_allowed': 3,
                'attempts_made': 1,
                'task_description': 'Discuss payment plan options - Business experiencing cash flow issues',
                'progress_status': 'Not Started',
                'special_instructions': 'Business owner - visit during off-peak hours (2-4 PM)'
            },
            {
                'staff_id': staff_ids[2],
                'loan_id': loan_ids[2],
                'supervisor_id': staff_ids[1],
                'assigned_branch': 'East Branch',
                'follow_up_deadline': '2024-01-25 15:00:00',
                'collection_priority': 'Low',
                'follow_up_frequency': 'Bi-Weekly',
                'next_follow_up_date': '2024-01-10 14:00:00',
                'preferred_collection_method': 'Phone Call',
                'promised_payment_date': '2024-01-30 00:00:00',
                'attempts_allowed': 4,
                'attempts_made': 0,
                'task_description': 'Regular follow-up on payment schedule - Minor delay',
                'progress_status': 'Not Started',
                'special_instructions': None
            },
            {
                'staff_id': staff_ids[0],
                'loan_id': loan_ids[3],
                'supervisor_id': staff_ids[1],
                'assigned_branch': 'Main Branch',
                'follow_up_deadline': '2024-01-10 09:00:00',
                'collection_priority': 'High',
                'follow_up_frequency': 'Daily',
                'next_follow_up_date': '2024-01-03 09:00:00',
                'preferred_collection_method': 'Legal Action',
                'attempts_allowed': 5,
                'attempts_made': 5,
                'task_description': 'Multiple failed payment promises - Escalate to legal',
                'progress_status': 'Escalated',
                'escalation_level': 2,
                'special_instructions': 'All communication must go through legal department'
            },
            {
                'staff_id': staff_ids[3],
                'loan_id': loan_ids[4],
                'supervisor_id': staff_ids[1],
                'assigned_branch': 'West Branch',
                'follow_up_deadline': '2024-02-01 16:00:00',
                'collection_priority': 'Medium',
                'follow_up_frequency': 'Weekly',
                'next_follow_up_date': '2024-01-08 14:00:00',
                'preferred_collection_method': 'Physical Visit',
                'promised_payment_date': '2024-01-25 00:00:00',
                'attempts_allowed': 4,
                'attempts_made': 1,
                'task_description': 'First reminder for upcoming payment',
                'progress_status': 'In Progress',
                'special_instructions': 'Customer requested evening visits after 4 PM'
            }
        ]

        # Add more varied scenarios if we have enough loans
        if len(loan_ids) > 5:
            sample_schedules.extend([
                {
                    'staff_id': staff_ids[4],
                    'loan_id': loan_ids[5],
                    'supervisor_id': staff_ids[1],
                    'assigned_branch': 'South Branch',
                    'follow_up_deadline': '2024-01-18 11:00:00',
                    'collection_priority': 'High',
                    'follow_up_frequency': 'Daily',
                    'next_follow_up_date': '2024-01-04 11:00:00',
                    'preferred_collection_method': 'Phone Call',
                    'attempts_allowed': 5,
                    'attempts_made': 4,
                    'task_description': 'Critical payment overdue - Final warning before legal action',
                    'progress_status': 'In Progress',
                    'escalation_level': 1,
                    'special_instructions': 'Document all communication carefully'
                },
                {
                    'staff_id': staff_ids[2],
                    'loan_id': loan_ids[6],
                    'supervisor_id': staff_ids[1],
                    'assigned_branch': 'North Branch',
                    'follow_up_deadline': '2024-02-15 10:00:00',
                    'collection_priority': 'Low',
                    'follow_up_frequency': 'Monthly',
                    'next_follow_up_date': '2024-01-15 10:00:00',
                    'preferred_collection_method': 'Email',
                    'attempts_allowed': 3,
                    'attempts_made': 0,
                    'task_description': 'Courtesy reminder for good-standing customer',
                    'progress_status': 'Not Started',
                    'special_instructions': 'Valued customer - maintain professional relationship'
                }
            ])

        # Insert sample schedules
        insert_sql = """
        INSERT INTO collection_schedules (
            staff_id, loan_id, supervisor_id, assigned_branch, follow_up_deadline,
            collection_priority, follow_up_frequency, next_follow_up_date,
            preferred_collection_method, promised_payment_date, attempts_allowed,
            attempts_made, task_description, progress_status, escalation_level,
            special_instructions
        ) VALUES (
            %(staff_id)s, %(loan_id)s, %(supervisor_id)s, %(assigned_branch)s, %(follow_up_deadline)s,
            %(collection_priority)s, %(follow_up_frequency)s, %(next_follow_up_date)s,
            %(preferred_collection_method)s, %(promised_payment_date)s, %(attempts_allowed)s,
            %(attempts_made)s, %(task_description)s, %(progress_status)s, %(escalation_level)s,
            %(special_instructions)s
        )
        """

        for schedule in sample_schedules:
            if schedule['loan_id'] is None:
                print("Skipping schedule due to missing loan_id")
                continue
                
            cursor.execute(insert_sql, {
                'staff_id': schedule['staff_id'],
                'loan_id': schedule['loan_id'],
                'supervisor_id': schedule['supervisor_id'],
                'assigned_branch': schedule['assigned_branch'],
                'follow_up_deadline': schedule['follow_up_deadline'],
                'collection_priority': schedule['collection_priority'],
                'follow_up_frequency': schedule['follow_up_frequency'],
                'next_follow_up_date': schedule['next_follow_up_date'],
                'preferred_collection_method': schedule['preferred_collection_method'],
                'promised_payment_date': schedule.get('promised_payment_date'),
                'attempts_allowed': schedule['attempts_allowed'],
                'attempts_made': schedule.get('attempts_made', 0),
                'task_description': schedule['task_description'],
                'progress_status': schedule['progress_status'],
                'escalation_level': schedule.get('escalation_level'),
                'special_instructions': schedule.get('special_instructions')
            })

        # Commit the changes
        conn.commit()
        print("Sample data inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database()
    insert_sample_data()