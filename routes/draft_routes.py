from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from datetime import datetime

draft_bp = Blueprint('draft', __name__)

@draft_bp.route('/user/save_section_draft/<int:module_id>', methods=['POST'])
@login_required
def save_section_draft(module_id):
    try:
        # Get the form data
        form_data = request.form.to_dict()
        section_number = form_data.pop('section_number', None)
        is_draft = form_data.pop('is_draft', None)

        if not section_number:
            return jsonify({'error': 'Section number is required'}), 400

        # Get the module to determine the table name
        module = db.session.execute(
            "SELECT table_name FROM modules WHERE id = :module_id",
            {'module_id': module_id}
        ).fetchone()

        if not module or not module.table_name:
            return jsonify({'error': 'Module not found or invalid'}), 404

        table_name = module.table_name

        # Check if a draft record exists for this user
        existing_record = db.session.execute(
            f"SELECT id FROM {table_name} WHERE created_by = :user_id AND draft_status = 'draft'",
            {'user_id': current_user.id}
        ).fetchone()

        # Prepare column names and values for the query
        columns = []
        values = []
        params = {}

        for key, value in form_data.items():
            if key != 'csrf_token':  # Skip CSRF token
                columns.append(key)
                values.append(f":{key}")
                params[key] = value

        # Add metadata fields
        current_time = datetime.utcnow()
        
        if existing_record:
            # Update existing draft
            set_clauses = [f"{col} = :{col}" for col in columns]
            set_clauses.append("updated_at = :updated_at")
            set_clauses.append("updated_by = :updated_by")
            
            query = f"""
                UPDATE {table_name}
                SET {', '.join(set_clauses)}
                WHERE id = :record_id AND created_by = :user_id AND draft_status = 'draft'
            """
            
            params.update({
                'updated_at': current_time,
                'updated_by': current_user.id,
                'record_id': existing_record.id,
                'user_id': current_user.id
            })
            
        else:
            # Create new draft
            columns.extend(['created_at', 'created_by', 'updated_at', 'updated_by', 'is_active', 'draft_status'])
            values.extend([':created_at', ':created_by', ':updated_at', ':updated_by', ':is_active', ':draft_status'])
            
            query = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(values)})
            """
            
            params.update({
                'created_at': current_time,
                'created_by': current_user.id,
                'updated_at': current_time,
                'updated_by': current_user.id,
                'is_active': 1,
                'draft_status': 'draft'
            })

        db.session.execute(query, params)
        db.session.commit()

        return jsonify({'message': 'Draft saved successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
