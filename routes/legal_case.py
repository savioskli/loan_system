from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from datetime import datetime
from models.legal_case import LegalCase, LegalCaseAttachment
from extensions import db

legal_bp = Blueprint('legal', __name__)

@legal_bp.route('/create_legal_case', methods=['POST'])
@login_required
def create_legal_case():
    """Create a new legal case"""
    try:
        # Get JSON data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['loan_id', 'case_number', 'court_name', 'case_type', 
                          'filing_date', 'status', 'plaintiff', 'defendant', 
                          'amount_claimed']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Convert dates to datetime objects
        filing_date = datetime.strptime(data['filing_date'], '%Y-%m-%d')
        next_hearing_date = datetime.strptime(data['next_hearing_date'], '%Y-%m-%d') if data.get('next_hearing_date') else None
        
        # Create new legal case
        new_case = LegalCase(
            loan_id=data['loan_id'],
            case_number=data['case_number'],
            court_name=data['court_name'],
            case_type=data['case_type'],
            filing_date=filing_date,
            status=data['status'],
            plaintiff=data['plaintiff'],
            defendant=data['defendant'],
            amount_claimed=float(data['amount_claimed']),
            lawyer_name=data.get('lawyer_name', ''),
            lawyer_contact=data.get('lawyer_contact', ''),
            description=data.get('description', ''),
            next_hearing_date=next_hearing_date
        )
        
        # Add and commit legal case
        db.session.add(new_case)
        db.session.commit()
        
        # Handle file upload if present
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                # Save file to uploads directory
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Create attachment record
                attachment = LegalCaseAttachment(
                    legal_case_id=new_case.id,
                    file_name=filename,
                    file_path=file_path,
                    file_type=file.content_type
                )
                db.session.add(attachment)
                db.session.commit()
        
        return jsonify({
            'message': 'Legal case created successfully', 
            'case_id': new_case.id
        }), 201
    
    except ValueError as ve:
        current_app.logger.error(f"Value error creating legal case: {str(ve)}")
        return jsonify({'error': 'Invalid date format'}), 400
    
    except Exception as e:
        current_app.logger.error(f"Error creating legal case: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating the legal case'}), 500
