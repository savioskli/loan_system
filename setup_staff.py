import mysql.connector
from config import db_config
from datetime import datetime
import bcrypt

def insert_staff_members():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Get default role_id for collection officers
        cursor.execute("SELECT id FROM roles WHERE name = 'Collection Officer' LIMIT 1")
        result = cursor.fetchone()
        if result:
            collection_officer_role_id = result[0]
        else:
            print("Collection Officer role not found. Please ensure roles are set up first.")
            return

        # Get default role_id for supervisors
        cursor.execute("SELECT id FROM roles WHERE name = 'Collection Supervisor' LIMIT 1")
        result = cursor.fetchone()
        if result:
            supervisor_role_id = result[0]
        else:
            print("Collection Supervisor role not found. Please ensure roles are set up first.")
            return

        # Get branch IDs
        cursor.execute("SELECT id, name FROM branches")
        branches = {row[1]: row[0] for row in cursor.fetchall()}
        if not branches:
            print("No branches found. Please ensure branches are set up first.")
            return

        # Sample staff data
        staff_members = [
            {
                'username': 'john.smith',
                'email': 'john.smith@loansystem.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '+254700123456',
                'role_id': collection_officer_role_id,
                'branch_id': branches.get('Main Branch'),
                'status': 'active',
                'password': 'password123'  # This will be hashed
            },
            {
                'username': 'sarah.johnson',
                'email': 'sarah.johnson@loansystem.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'phone': '+254700123457',
                'role_id': supervisor_role_id,
                'branch_id': branches.get('Main Branch'),
                'status': 'active',
                'password': 'password123'
            },
            {
                'username': 'michael.chen',
                'email': 'michael.chen@loansystem.com',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'phone': '+254700123458',
                'role_id': collection_officer_role_id,
                'branch_id': branches.get('Downtown Branch'),
                'status': 'active',
                'password': 'password123'
            },
            {
                'username': 'emily.brown',
                'email': 'emily.brown@loansystem.com',
                'first_name': 'Emily',
                'last_name': 'Brown',
                'phone': '+254700123459',
                'role_id': collection_officer_role_id,
                'branch_id': branches.get('East Branch'),
                'status': 'active',
                'password': 'password123'
            },
            {
                'username': 'david.wilson',
                'email': 'david.wilson@loansystem.com',
                'first_name': 'David',
                'last_name': 'Wilson',
                'phone': '+254700123460',
                'role_id': supervisor_role_id,
                'branch_id': branches.get('Downtown Branch'),
                'status': 'active',
                'password': 'password123'
            }
        ]

        # Insert staff members
        insert_sql = """
        INSERT INTO staff (
            username, email, first_name, last_name, phone, password_hash,
            role_id, branch_id, status, is_active
        ) VALUES (
            %(username)s, %(email)s, %(first_name)s, %(last_name)s, %(phone)s, %(password_hash)s,
            %(role_id)s, %(branch_id)s, %(status)s, 1
        )
        """

        for staff in staff_members:
            try:
                # Hash the password
                password_hash = bcrypt.hashpw(staff['password'].encode('utf-8'), bcrypt.gensalt())
                
                insert_data = {
                    'username': staff['username'],
                    'email': staff['email'],
                    'first_name': staff['first_name'],
                    'last_name': staff['last_name'],
                    'phone': staff['phone'],
                    'password_hash': password_hash,
                    'role_id': staff['role_id'],
                    'branch_id': staff['branch_id'],
                    'status': staff['status']
                }
                
                cursor.execute(insert_sql, insert_data)
                print(f"Added staff member: {staff['first_name']} {staff['last_name']}")
            except mysql.connector.Error as err:
                if err.errno == 1062:  # Duplicate entry error
                    print(f"Staff member already exists: {staff['first_name']} {staff['last_name']}")
                else:
                    print(f"Error adding staff member {staff['first_name']} {staff['last_name']}: {err}")

        # Commit the changes
        conn.commit()
        print("\nStaff members added successfully!")

        # Display current staff count
        cursor.execute("SELECT COUNT(*) FROM staff")
        count = cursor.fetchone()[0]
        print(f"\nTotal staff members in database: {count}")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    insert_staff_members()
