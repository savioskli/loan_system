from models.staff import Staff
from models.role import Role
from extensions import db
from datetime import datetime
import logging
from sqlalchemy import text

class StaffService:
    @staticmethod
    def get_all_staff():
        """Get all staff members with their roles and branches."""
        try:
            print("\n=== Starting get_all_staff ===")
            print(f"Database URI: {db.engine.url}")
            
            # Test database connection
            with db.engine.connect() as connection:
                print("Connection established")
                result = connection.execute(text('SELECT 1')).scalar()
                print(f"Connection test result: {result}")
                
                # Test roles table
                print("\nTesting roles table...")
                role_count = connection.execute(text('SELECT COUNT(*) FROM roles')).scalar()
                print(f"Found {role_count} roles in database")
                
                # Test staff table
                print("\nTesting staff table...")
                staff_count = connection.execute(text('SELECT COUNT(*) FROM staff')).scalar()
                print(f"Found {staff_count} staff members in database")
                
                # Test role relationships
                print("\nTesting role relationships...")
                role_staff_count = connection.execute(text('''
                    SELECT COUNT(*) 
                    FROM staff 
                    WHERE role_id IS NOT NULL
                ''')).scalar()
                print(f"Staff members with roles: {role_staff_count}")

            # Query staff members
            try:
                print("\nQuerying staff members...")
                query = Staff.query.options(
                    db.joinedload(Staff.role).load_only(Role.name, Role.id),
                    db.joinedload(Staff.branch)
                ).order_by(Staff.created_at.desc())
                print(f"Query: {str(query)}")
                users = query.all()
                print(f"Retrieved {len(users)} users from database")
                
                # Log each user's details
                for user in users:
                    role_name = user.role.name if user.role else "None"
                    branch_name = user.branch.name if user.branch else "None"
                    print(f"\nUser {user.id}:")
                    print(f"Username: {user.username}")
                    print(f"Role: {role_name}")
                    print(f"Branch: {branch_name}")
                    print(f"Status: {user.status}")
                    print(f"is_active: {user.is_active}")
                    print(f"Created at: {user.created_at}")
                    print(f"Updated at: {user.updated_at}")
                    print(f"Role ID: {user.role_id}")
                    print(f"Branch ID: {user.branch_id}")
                
                return users
            except Exception as e:
                print(f"Error querying staff: {str(e)}")
                raise
        except Exception as e:
            print(f"Error in get_all_staff: {str(e)}")
            raise

    @staticmethod
    def get_staff_by_status(status):
        """Get staff members filtered by status."""
        try:
            print("\n=== Starting get_staff_by_status ===")
            print(f"Database URI: {db.engine.url}")
            
            # Test database connection
            with db.engine.connect() as connection:
                print("Connection established")
                result = connection.execute(text('SELECT 1')).scalar()
                print(f"Connection test result: {result}")
                
                # Test roles table
                print("\nTesting roles table...")
                role_count = connection.execute(text('SELECT COUNT(*) FROM roles')).scalar()
                print(f"Found {role_count} roles in database")
                
                # Test staff table
                print("\nTesting staff table...")
                staff_count = connection.execute(text('SELECT COUNT(*) FROM staff')).scalar()
                print(f"Found {staff_count} staff members in database")
                
                # Test role relationships
                print("\nTesting role relationships...")
                role_staff_count = connection.execute(text('''
                    SELECT COUNT(*) 
                    FROM staff 
                    WHERE role_id IS NOT NULL
                ''')).scalar()
                print(f"Staff members with roles: {role_staff_count}")

            # Try to filter by status field first
            try:
                print("\nQuerying staff members by status...")
                query = Staff.query.options(
                    db.joinedload(Staff.role).load_only(Role.name, Role.id),
                    db.joinedload(Staff.branch)
                ).filter_by(status=status)
                print(f"Query: {str(query)}")
                users = query.all()
                print(f"Retrieved {len(users)} users from database")
                
                # Log each user's details
                for user in users:
                    role_name = user.role.name if user.role else "None"
                    branch_name = user.branch.name if user.branch else "None"
                    print(f"\nUser {user.id}:")
                    print(f"Username: {user.username}")
                    print(f"Role: {role_name}")
                    print(f"Branch: {branch_name}")
                    print(f"Status: {user.status}")
                    print(f"is_active: {user.is_active}")
                    print(f"Created at: {user.created_at}")
                    print(f"Updated at: {user.updated_at}")
                    print(f"Role ID: {user.role_id}")
                    print(f"Branch ID: {user.branch_id}")
                
                return users
            except Exception as e:
                print(f"Error filtering by status: {str(e)}")
                
            # If no results, try to filter by is_active field
            if not users:
                try:
                    print("\nQuerying staff members by is_active...")
                    query = Staff.query.options(
                        db.joinedload(Staff.role).load_only(Role.name, Role.id),
                        db.joinedload(Staff.branch)
                    ).filter_by(is_active=status)
                    print(f"Query: {str(query)}")
                    users = query.all()
                    print(f"Retrieved {len(users)} users from database")
                    
                    # Log each user's details
                    for user in users:
                        role_name = user.role.name if user.role else "None"
                        branch_name = user.branch.name if user.branch else "None"
                        print(f"\nUser {user.id}:")
                        print(f"Username: {user.username}")
                        print(f"Role: {role_name}")
                        print(f"Branch: {branch_name}")
                        print(f"Status: {user.status}")
                        print(f"is_active: {user.is_active}")
                        print(f"Created at: {user.created_at}")
                        print(f"Updated at: {user.updated_at}")
                        print(f"Role ID: {user.role_id}")
                        print(f"Branch ID: {user.branch_id}")
                    
                    return users
                except Exception as e:
                    print(f"Error filtering by is_active: {str(e)}")
                    raise
        except Exception as e:
            print(f"Error in get_staff_by_status: {str(e)}")
            raise
    
    @staticmethod
    def get_staff_by_id(staff_id):
        """Get a staff member by ID."""
        try:
            print(f"\n=== Starting get_staff_by_id with ID: {staff_id} ===")
            print(f"Database URI: {db.engine.url}")
            
            # Test database connection
            with db.engine.connect() as connection:
                print("Connection established")
                result = connection.execute(text('SELECT 1')).scalar()
                print(f"Connection test result: {result}")
                
                # Test roles table
                print("\nTesting roles table...")
                role_count = connection.execute(text('SELECT COUNT(*) FROM roles')).scalar()
                print(f"Found {role_count} roles in database")
                
                # Test staff table
                print("\nTesting staff table...")
                staff_count = connection.execute(text('SELECT COUNT(*) FROM staff')).scalar()
                print(f"Found {staff_count} staff members in database")
                
                # Test role relationships
                print("\nTesting role relationships...")
                role_staff_count = connection.execute(text('''
                    SELECT COUNT(*) 
                    FROM staff 
                    WHERE role_id IS NOT NULL
                ''')).scalar()
                print(f"Staff members with roles: {role_staff_count}")

            # Query staff member
            try:
                print("\nQuerying staff member by ID...")
                query = Staff.query.options(
                    db.joinedload(Staff.role).load_only(Role.name, Role.id),
                    db.joinedload(Staff.branch)
                ).get(staff_id)
                print(f"Query: {str(query)}")
                if query:
                    print(f"Found staff member with ID: {staff_id}")
                    role_name = query.role.name if query.role else "None"
                    branch_name = query.branch.name if query.branch else "None"
                    print(f"\nUser {query.id}:")
                    print(f"Username: {query.username}")
                    print(f"Role: {role_name}")
                    print(f"Branch: {branch_name}")
                    print(f"Status: {query.status}")
                    print(f"is_active: {query.is_active}")
                    print(f"Created at: {query.created_at}")
                    print(f"Updated at: {query.updated_at}")
                    print(f"Role ID: {query.role_id}")
                    print(f"Branch ID: {query.branch_id}")
                else:
                    print(f"Staff member with ID {staff_id} not found")
                return query
            except Exception as e:
                print(f"Error querying staff by ID: {str(e)}")
                raise
        except Exception as e:
            print(f"Error in get_staff_by_id: {str(e)}")
            raise
    
    @staticmethod
    def create_staff(staff_data):
        """Create a new staff member with the provided data."""
        try:
            # Validate required fields
            required_fields = ['email', 'first_name', 'last_name', 'password', 'role_id', 'username']
            for field in required_fields:
                if field not in staff_data or not staff_data[field]:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate email format
            email = staff_data['email'].lower().strip()
            if not email or '@' not in email:
                raise ValueError("Invalid email format")
            
            # Validate username format
            username = staff_data['username'].strip()
            if not username or len(username) < 3:
                raise ValueError("Username must be at least 3 characters long")
            
            # Validate password length
            password = staff_data['password']
            if not password or len(password) < 6:
                raise ValueError("Password must be at least 6 characters long")
            
            # Check if email already exists
            if Staff.query.filter_by(email=email).first():
                raise ValueError("Email already exists")
            
            # Check if username already exists
            if Staff.query.filter_by(username=username).first():
                raise ValueError("Username already exists")
            
            # Validate role_id exists
            if not Role.query.get(staff_data['role_id']):
                raise ValueError("Invalid role ID")
            
            # Create new staff member
            new_staff = Staff(
                email=email,
                username=username,
                first_name=staff_data['first_name'].strip(),
                last_name=staff_data['last_name'].strip(),
                role_id=staff_data['role_id'],
                phone=staff_data.get('phone', '').strip() or None,
                branch_id=staff_data.get('branch_id'),
                is_active=staff_data.get('is_active', True)
            )
            
            # Set password
            new_staff.set_password(password)
            
            # Add to session
            db.session.add(new_staff)
            
            # Commit transaction
            db.session.commit()
            
            return new_staff
            
        except ValueError as ve:
            db.session.rollback()
            raise ValueError(str(ve))
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to create staff member: {str(e)}")
    
    @staticmethod
    def update_staff(staff_id, data):
        """Update a staff member's information."""
        try:
            print(f"\n=== Starting update_staff with ID: {staff_id} ===")
            print(f"Database URI: {db.engine.url}")
            
            # Test database connection
            with db.engine.connect() as connection:
                print("Connection established")
                result = connection.execute(text('SELECT 1')).scalar()
                print(f"Connection test result: {result}")
                
                # Test roles table
                print("\nTesting roles table...")
                role_count = connection.execute(text('SELECT COUNT(*) FROM roles')).scalar()
                print(f"Found {role_count} roles in database")
                
                # Test staff table
                print("\nTesting staff table...")
                staff_count = connection.execute(text('SELECT COUNT(*) FROM staff')).scalar()
                print(f"Found {staff_count} staff members in database")
                
                # Test role relationships
                print("\nTesting role relationships...")
                role_staff_count = connection.execute(text('''
                    SELECT COUNT(*) 
                    FROM staff 
                    WHERE role_id IS NOT NULL
                ''')).scalar()
                print(f"Staff members with roles: {role_staff_count}")

            staff = Staff.query.get(staff_id)
            if not staff:
                print(f"Staff member with ID {staff_id} not found")
                return False, "Staff member not found"
            
            # Update staff information
            if 'first_name' in data:
                staff.first_name = data['first_name'].strip()
                print(f"Updated first name for staff member with ID: {staff_id}")
            if 'last_name' in data:
                staff.last_name = data['last_name'].strip()
                print(f"Updated last name for staff member with ID: {staff_id}")
            if 'email' in data:
                staff.email = data['email'].lower().strip()
                print(f"Updated email for staff member with ID: {staff_id}")
            if 'username' in data:
                username = data['username'].strip()
                # Check if username already exists (case-insensitive)
                existing_staff = Staff.query.filter(Staff.username.ilike(username),
                                                 Staff.id != staff_id).first()
                if existing_staff:
                    print(f"Username {username} already taken")
                    return False, "Username already taken"
                staff.username = username
                print(f"Updated username for staff member with ID: {staff_id}")
            if 'phone' in data:
                staff.phone = data['phone'].strip() if data['phone'] else None
                print(f"Updated phone for staff member with ID: {staff_id}")
            if 'branch_id' in data:
                staff.branch_id = data['branch_id']
                print(f"Updated branch ID for staff member with ID: {staff_id}")
            if 'role_id' in data:
                staff.role_id = data['role_id']
                print(f"Updated role ID for staff member with ID: {staff_id}")
            if 'is_active' in data:
                staff.is_active = data['is_active']
                print(f"Updated is_active status for staff member with ID: {staff_id}")
            if 'password' in data and data['password']:
                staff.set_password(data['password'])
                print(f"Updated password for staff member with ID: {staff_id}")
            
            staff.updated_at = datetime.utcnow()
            db.session.commit()
            print(f"Staff member with ID {staff_id} updated successfully")
            role_name = staff.role.name if staff.role else "None"
            branch_name = staff.branch.name if staff.branch else "None"
            print(f"\nUser {staff.id}:")
            print(f"Username: {staff.username}")
            print(f"Role: {role_name}")
            print(f"Branch: {branch_name}")
            print(f"Status: {staff.status}")
            print(f"is_active: {staff.is_active}")
            print(f"Created at: {staff.created_at}")
            print(f"Updated at: {staff.updated_at}")
            print(f"Role ID: {staff.role_id}")
            print(f"Branch ID: {staff.branch_id}")
            return True, "Staff member updated successfully"
        except Exception as e:
            db.session.rollback()
            print(f"Failed to update staff member: {str(e)}")
            return False, f"Failed to update staff member: {str(e)}"
