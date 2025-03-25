from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models.staff import Staff
from models.branch import Branch
from models.role import Role
from forms.user_management import UserCreateForm, UserApprovalForm
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash
import logging
from services.staff_service import StaffService
from sqlalchemy import text

bp = Blueprint('user_management', __name__, url_prefix='/users')

# User Management
@bp.route('/test', methods=['GET'])
@login_required
def test():
    """Test database connection and user retrieval."""
    try:
        # Test database connection
        with db.engine.connect() as connection:
            print("Testing database connection...")
            print(f"Engine URL: {db.engine.url}")
            print(f"Engine dialect: {db.engine.dialect.name}")
            print(f"Engine driver: {db.engine.driver}")
            
            # Test connection
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

        # Test user retrieval
        users = Staff.query.all()
        print(f"\nRetrieved {len(users)} users from database")
        for user in users:
            print(f"\nUser {user.id}:")
            print(f"Username: {user.username}")
            print(f"Role: {user.role.name if user.role else 'None'}")
            print(f"Status: {user.status}")
            print(f"is_active: {user.is_active}")
            print(f"Created at: {user.created_at}")
            print(f"Updated at: {user.updated_at}")
            print(f"Role ID: {user.role_id}")
            print(f"Branch ID: {user.branch_id}")
        
        return jsonify({
            'database_connection': 'success',
            'role_count': role_count,
            'user_count': len(users),
            'users': [{'id': user.id, 'username': user.username} for user in users]
        })
    except Exception as e:
        print(f"Error in test: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@bp.route('/test_tables', methods=['GET'])
@login_required
def test_tables():
    """Test database tables and relationships."""
    try:
        # Test roles table
        roles = Role.query.all()
        print(f"\n=== Testing Roles Table ===")
        print(f"Found {len(roles)} roles")
        for role in roles:
            print(f"\nRole {role.id}:")
            print(f"Name: {role.name}")
            print(f"Code: {role.code}")
            print(f"Is Active: {role.is_active}")
            print(f"Created At: {role.created_at}")
            print(f"Updated At: {role.updated_at}")
            print(f"Created By: {role.creator.username if role.creator else 'None'}")
            print(f"Updated By: {role.updater.username if role.updater else 'None'}")

        # Test staff table
        staff = Staff.query.all()
        print(f"\n=== Testing Staff Table ===")
        print(f"Found {len(staff)} staff members")
        for member in staff:
            print(f"\nStaff {member.id}:")
            print(f"Username: {member.username}")
            print(f"Email: {member.email}")
            print(f"Full Name: {member.full_name}")
            print(f"Role: {member.role.name if member.role else 'None'}")
            print(f"Branch: {member.branch.name if member.branch else 'None'}")
            print(f"Status: {member.status}")
            print(f"Is Active: {member.is_active}")
            print(f"Created At: {member.created_at}")
            print(f"Updated At: {member.updated_at}")
            print(f"Approved By: {member.approved_by.username if member.approved_by else 'None'}")
            print(f"Approved At: {member.approved_at}")
            print(f"Last Login: {member.last_login}")

        # Test role relationships
        print("\n=== Testing Role Relationships ===")
        for role in roles:
            staff_members = Staff.query.filter_by(role_id=role.id).all()
            print(f"\nRole {role.id} ({role.name}) has {len(staff_members)} staff members:")
            for member in staff_members:
                print(f"- {member.username}")

        return jsonify({
            'roles': [{'id': r.id, 'name': r.name, 'code': r.code} for r in roles],
            'staff': [{'id': s.id, 'username': s.username, 'role': s.role.name if s.role else None} for s in staff]
        })
    except Exception as e:
        print(f"Error in test_tables: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@bp.route('/search', methods=['GET'])
@login_required
def search_users():
    """Search users with AJAX."""
    try:
        current_app.logger.info("Starting search_users")
        
        # Get search query from request
        search = request.args.get('query', '').strip()
        current_app.logger.info(f"Received search query: {search}")
        
        # Get page number from query parameters
        page = request.args.get('page', 1, type=int)
        current_app.logger.info(f"Received page number: {page}")
        
        # Get users from database with pagination
        try:
            current_app.logger.info("Querying users from database")
            query = Staff.query
            
            # Apply search filter if provided
            if search:
                try:
                    search_query = search.lower()
                    query = query.filter(
                        (Staff.username.ilike(f'%{search_query}%')) |
                        (Staff.first_name.ilike(f'%{search_query}%')) |
                        (Staff.last_name.ilike(f'%{search_query}%')) |
                        (Staff.email.ilike(f'%{search_query}%')) |
                        (Staff.phone.ilike(f'%{search_query}%'))
                    )
                    current_app.logger.info(f"Applied search filter: {search}")
                except Exception as e:
                    current_app.logger.error(f"Error applying search filter: {str(e)}", exc_info=True)
                    raise
            
            # Apply pagination
            try:
                per_page = 10
                pagination = query.paginate(page=page, per_page=per_page, error_out=False)
                users = pagination.items
                current_app.logger.info(f"Retrieved {len(users)} users for page {page}")
            except Exception as e:
                current_app.logger.error(f"Error applying pagination: {str(e)}", exc_info=True)
                raise
        except Exception as e:
            current_app.logger.error(f"Error querying users: {str(e)}", exc_info=True)
            raise
        
        # Get roles from database
        try:
            current_app.logger.info("Querying roles from database")
            roles = Role.query.all()
            current_app.logger.info(f"Retrieved {len(roles)} roles")
        except Exception as e:
            current_app.logger.error(f"Error querying roles: {str(e)}", exc_info=True)
            raise
        
        # Get branches from database
        try:
            current_app.logger.info("Querying branches from database")
            branches = Branch.query.all()
            current_app.logger.info(f"Retrieved {len(branches)} branches")
        except Exception as e:
            current_app.logger.error(f"Error querying branches: {str(e)}", exc_info=True)
            raise
        
        # Prepare data for template
        try:
            current_app.logger.info("Preparing data for template")
            data = {
                'users': users,
                'roles': roles,
                'branches': branches,
                'pagination': pagination,
                'search': search
            }
            current_app.logger.info(f"Data prepared: {data.keys()}")
        except Exception as e:
            current_app.logger.error(f"Error preparing data: {str(e)}", exc_info=True)
            raise
        
        # Render only the table body and pagination
        return render_template('admin/users/_user_table.html', **data)
        
    except Exception as e:
        current_app.logger.error(f"Error in search_users: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['GET'])
@login_required
def list_users():
    """List all users."""
    try:
        current_app.logger.info("Starting list_users")
        
        # Get search query from request
        search = request.args.get('search', '').strip()
        current_app.logger.info(f"Received search query: {search}")
        
        # Get page number from query parameters
        page = request.args.get('page', 1, type=int)
        current_app.logger.info(f"Received page number: {page}")
        
        # Get users from database with pagination
        try:
            current_app.logger.info("Querying users from database")
            query = Staff.query
            
            # Apply search filter if provided
            if search:
                try:
                    search_query = search.lower()
                    query = query.filter(
                        (Staff.username.ilike(f'%{search_query}%')) |
                        (Staff.first_name.ilike(f'%{search_query}%')) |
                        (Staff.last_name.ilike(f'%{search_query}%')) |
                        (Staff.email.ilike(f'%{search_query}%')) |
                        (Staff.phone.ilike(f'%{search_query}%'))
                    )
                    current_app.logger.info(f"Applied search filter: {search}")
                except Exception as e:
                    current_app.logger.error(f"Error applying search filter: {str(e)}", exc_info=True)
                    raise
            
            # Apply pagination
            try:
                per_page = 10
                pagination = query.paginate(page=page, per_page=per_page, error_out=False)
                users = pagination.items
                current_app.logger.info(f"Retrieved {len(users)} users for page {page}")
            except Exception as e:
                current_app.logger.error(f"Error applying pagination: {str(e)}", exc_info=True)
                raise
        except Exception as e:
            current_app.logger.error(f"Error querying users: {str(e)}", exc_info=True)
            raise
        
        # Get roles from database
        try:
            current_app.logger.info("Querying roles from database")
            roles = Role.query.all()
            current_app.logger.info(f"Retrieved {len(roles)} roles")
        except Exception as e:
            current_app.logger.error(f"Error querying roles: {str(e)}", exc_info=True)
            raise
        
        # Get branches from database
        try:
            current_app.logger.info("Querying branches from database")
            branches = Branch.query.all()
            current_app.logger.info(f"Retrieved {len(branches)} branches")
        except Exception as e:
            current_app.logger.error(f"Error querying branches: {str(e)}", exc_info=True)
            raise
        
        # Prepare data for template
        try:
            current_app.logger.info("Preparing data for template")
            data = {
                'users': users,
                'roles': roles,
                'branches': branches,
                'pagination': pagination,
                'search': search
            }
            current_app.logger.info(f"Data prepared: {data.keys()}")
        except Exception as e:
            current_app.logger.error(f"Error preparing data: {str(e)}", exc_info=True)
            raise
        
        return render_template('admin/users/list.html', **data)
        
    except Exception as e:
        current_app.logger.error(f"Error in list_users: {str(e)}", exc_info=True)
        raise

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create a new user."""
    form = UserCreateForm()
    
    try:
        # Get all roles and branches from the database
        roles = Role.query.all()
        if not roles:
            flash('No roles found in the system. Please create at least one role first.', 'error')
            return redirect(url_for('user_management.list_users'))
            
        branches = Branch.query.all()
        
        # Populate form choices with data from the database
        form.role_id.choices = [(role.id, role.name) for role in roles]
        form.branch_id.choices = [(branch.id, branch.name) for branch in branches]
        
        if form.validate_on_submit():
            try:
                # Prepare staff data with form input
                staff_data = {
                    'email': form.email.data.strip(),
                    'username': form.username.data.strip(),
                    'first_name': form.first_name.data.strip(),
                    'last_name': form.last_name.data.strip(),
                    'phone': form.phone.data.strip() if form.phone.data else None,
                    'password': form.password.data,
                    'role_id': form.role_id.data,
                    'branch_id': form.branch_id.data if form.branch_id.data else None,
                    'is_active': form.is_active.data
                }
                
                # Create new staff member using the StaffService
                new_staff = StaffService.create_staff(staff_data)
                
                flash('User created successfully!', 'success')
                return redirect(url_for('user_management.list_users'))
                
            except ValueError as e:
                flash(str(e), 'error')
                return render_template('admin/users/create.html', form=form)
            except Exception as e:
                flash('An unexpected error occurred while creating the user.', 'error')
                return render_template('admin/users/create.html', form=form)
        
        return render_template('admin/users/create.html', form=form)
        
    except Exception as e:
        flash('An error occurred while setting up the form.', 'error')
        return render_template('admin/users/create.html', form=form)

@bp.route('/view/<int:user_id>', methods=['GET'])
@login_required
def view_user(user_id):
    """View a user's details."""
    try:
        user = Staff.query.get_or_404(user_id)
        return render_template('admin/users/view.html', user=user)
        
    except Exception as e:
        current_app.logger.error(f"Error in view_user: {str(e)}", exc_info=True)
        flash('An error occurred while viewing the user.', 'error')
        return redirect(url_for('user_management.list_users'))

@bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit an existing user."""
    try:
        user = Staff.query.get_or_404(user_id)
        
        form = UserCreateForm(obj=user)
        if form.validate_on_submit():
            user.username = form.username.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.role_id = form.role_id.data
            user.branch_id = form.branch_id.data
            user.status = form.status.data
            user.is_active = form.is_active.data
            
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for('user_management.list_users'))
        
        return render_template('admin/users/edit.html', form=form, user=user)
        
    except Exception as e:
        current_app.logger.error(f"Error in edit_user: {str(e)}", exc_info=True)
        flash('An error occurred while updating the user.', 'error')
        return redirect(url_for('user_management.list_users'))

@bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user."""
    try:
        user = Staff.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
        return redirect(url_for('user_management.list_users'))
        
    except Exception as e:
        current_app.logger.error(f"Error in delete_user: {str(e)}", exc_info=True)
        flash('An error occurred while deleting the user.', 'error')
        return redirect(url_for('user_management.list_users'))

@bp.route('/change-status/<int:user_id>', methods=['POST'])
@login_required
def change_status(user_id):
    """Change a user's status."""
    try:
        user = Staff.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        flash(f'User status changed to {"Active" if user.is_active else "Inactive"}.', 'success')
        return redirect(url_for('user_management.list_users'))
        
    except Exception as e:
        current_app.logger.error(f"Error in change_status: {str(e)}", exc_info=True)
        flash('An error occurred while changing the user status.', 'error')
        return redirect(url_for('user_management.list_users'))

@bp.route('/<int:user_id>/approve', methods=['GET', 'POST'])
@login_required
def approve_user(user_id):
    """Approve a user."""
    try:
        user = Staff.query.get_or_404(user_id)
        
        if request.method == 'POST':
            form = UserApprovalForm(request.form)
            if form.validate():
                user.is_approved = True
                user.approved_by = current_user.id
                user.approved_at = datetime.utcnow()
                db.session.commit()
                flash('User approved successfully.', 'success')
                return redirect(url_for('user_management.list_users'))
        
        form = UserApprovalForm()
        return render_template('admin/users/approve.html', form=form, user=user)
        
    except Exception as e:
        current_app.logger.error(f"Error in approve_user: {str(e)}", exc_info=True)
        flash('An error occurred while approving the user.', 'error')
        return redirect(url_for('user_management.list_users'))
