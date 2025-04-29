import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from models.crb_report import CRBReport
from services.crb_service import CRBService

crb_bp = Blueprint('crb', __name__)

@crb_bp.route('/crb-reports')
@login_required
def crb_reports():
    """Render the CRB reports page"""
    return render_template('user/crb_reports.html')

@crb_bp.route('/crb-reports/generate', methods=['POST'])
@login_required
def generate_crb_report():
    """Generate a new CRB report"""
    try:
        data = request.get_json()
        national_id = data.get('national_id')
        
        if not national_id:
            return jsonify({'error': 'National ID is required'}), 400
            
        crb_service = CRBService()
        report = crb_service.generate_report(national_id)
        
        return jsonify({
            'id': report.id,
            'status': report.status,
            'message': 'Report generation initiated'
        })
    except Exception as e:
        current_app.logger.error(f"Error generating CRB report: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500

@crb_bp.route('/crb-reports/<int:report_id>')
@login_required
def get_crb_report(report_id):
    """Get a specific CRB report"""
    try:
        crb_service = CRBService()
        report = crb_service.get_report(report_id)
        
        return jsonify({
            'id': report.id,
            'national_id': report.national_id,
            'status': report.status,
            'credit_score': report.credit_score,
            'report_reference': report.report_reference,
            'created_at': report.created_at.isoformat(),
            'report_data': report.report_data
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving CRB report: {str(e)}")
        return jsonify({'error': 'Failed to retrieve report'}), 500

@crb_bp.route('/crb-reports/list')
@login_required
def list_crb_reports():
    """Get paginated list of CRB reports with stats"""
    try:
        # Get active credit bureau for Metropol
        from models.credit_bureau import CreditBureau
        bureau = CreditBureau.query.filter_by(provider='metropol', is_active=True).first()
        
        # Log the bureau information
        if bureau:
            current_app.logger.info(f"Using active credit bureau: {bureau.name}")
            current_app.logger.info(f"Bureau credentials: base_url={bureau.base_url}, api_key={bureau.api_key[:5]}...")
        else:
            current_app.logger.warning("No active Metropol credit bureau found. Using default configuration.")
            
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            current_app.logger.info(f"Created logs directory: {log_dir}")
        
        # Write debug information to a specific debug log file
        debug_log_file = os.path.join(log_dir, 'crb_debug.log')
        with open(debug_log_file, 'a') as f:
            f.write(f"=== {datetime.now()} - CRB Reports Listing ===\n")
            f.write(f"Bureau: {bureau.name if bureau else 'None'}\n")
        
        page = request.args.get('page', 1, type=int)
        crb_service = CRBService(bureau=bureau)
        pagination = crb_service.get_reports(page=page)
        
        reports = [{
            'id': report.id,
            'national_id': report.national_id,
            'status': report.status,
            'credit_score': report.credit_score,
            'created_at': report.created_at.isoformat()
        } for report in pagination.items]
        
        # Get statistics
        stats = {
            'negative_count': CRBReport.query.filter_by(status='completed').filter(CRBReport.credit_score < 600).count(),
            'positive_count': CRBReport.query.filter_by(status='completed').filter(CRBReport.credit_score >= 600).count(),
            'pending_count': CRBReport.query.filter_by(status='pending').count()
        }
        
        return jsonify({
            'reports': reports,
            'stats': stats,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        current_app.logger.error(f"Error listing CRB reports: {str(e)}")
        return jsonify({'error': 'Failed to list reports'}), 500
