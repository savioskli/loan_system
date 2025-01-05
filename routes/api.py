from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
import mysql.connector
from config import db_config

api_bp = Blueprint('api', __name__, url_prefix='/api')

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
