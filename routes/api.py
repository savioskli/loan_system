from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
import mysql.connector
from config import db_config
from models.correspondence import Correspondence
from models.staff import Staff
from models.loan import Loan
from datetime import datetime
from extensions import db, csrf

api_bp = Blueprint('api', __name__, url_prefix='/api')
csrf.exempt(api_bp)  # Remove CSRF protection from API routes since we handle it manually

@api_bp.route('/customers/search')
@login_required
def search_customers():
    """Search customers/clients from core banking database."""
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        if not query:
            return jsonify({
                'items': [],
                'has_more': False
            })

        # Connect to core banking database
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database='sacco_db',  # Use core banking database
            auth_plugin=db_config['auth_plugin']
        )
        cursor = conn.cursor(dictionary=True)

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Search query with LIKE for multiple fields
        search_term = f"%{query}%"
        sql = """
            SELECT 
                MemberID,
                MemberNo,
                FirstName,
                MiddleName,
                LastName,
                FullName,
                PhoneNumber,
                Email,
                Status
            FROM Members 
            WHERE 
                MemberNo LIKE %s OR
                FirstName LIKE %s OR
                MiddleName LIKE %s OR
                LastName LIKE %s OR
                PhoneNumber LIKE %s OR
                Email LIKE %s OR
                FullName LIKE %s
            AND Status = 'Active'
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (
            search_term, search_term, search_term, search_term, 
            search_term, search_term, search_term, per_page, offset
        ))
        members = cursor.fetchall()

        # Get total count for pagination
        count_sql = """
            SELECT COUNT(*) as count
            FROM Members 
            WHERE 
                (MemberNo LIKE %s OR
                FirstName LIKE %s OR
                MiddleName LIKE %s OR
                LastName LIKE %s OR
                PhoneNumber LIKE %s OR
                Email LIKE %s OR
                FullName LIKE %s)
            AND Status = 'Active'
        """
        cursor.execute(count_sql, (
            search_term, search_term, search_term, search_term, 
            search_term, search_term, search_term
        ))
        total_count = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        # Transform the results to match Select2 format
        return jsonify({
            'items': [{
                'id': str(member['MemberID']),
                'text': f"{member['FullName']} ({member['MemberNo']})",
                'member_no': member['MemberNo'],
                'phone': member.get('PhoneNumber', ''),
                'email': member.get('Email', '')
            } for member in members],
            'has_more': total_count > (page * per_page)
        })

    except Exception as e:
        current_app.logger.error(f'Error in customer search: {str(e)}')
        return jsonify({
            'items': [],
            'has_more': False,
            'error': 'An error occurred while searching'
        }), 500

@api_bp.route('/communications', methods=['POST'])
@login_required
def create_communication():
    """Create a new communication record"""
    try:
        data = request.json
        current_app.logger.info(f"Received data: {data}")
        
        # Get current staff member
        staff = Staff.query.filter_by(username=current_user.username).first()
        if not staff:
            return jsonify({
                'status': 'error',
                'message': 'Staff record not found'
            }), 404
            
        # Create new communication
        try:
            new_comm = Correspondence(
                account_no=data['account_no'],
                client_name=data['client_name'],
                type=data['type'],
                message=data['message'],
                status=data.get('status', 'pending'),
                sent_by=current_user.username,
                staff_id=staff.id,
                recipient=data.get('recipient') or None,
                delivery_status=data.get('delivery_status') or None,
                delivery_time=datetime.strptime(data['delivery_time'], '%Y-%m-%dT%H:%M') if data.get('delivery_time') else None,
                call_duration=int(data['call_duration']) if data.get('call_duration') else None,
                call_outcome=data.get('call_outcome') or None,
                location=data.get('location') or None,
                visit_purpose=data.get('visit_purpose') or None,
                visit_outcome=data.get('visit_outcome') or None
            )
        except KeyError as e:
            current_app.logger.error(f"Missing required field: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Missing required field: {str(e)}'
            }), 400
        
        db.session.add(new_comm)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Communication created successfully',
            'data': new_comm.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating communication: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to create communication'
        }), 500
