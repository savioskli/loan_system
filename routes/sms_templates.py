from flask import Blueprint, render_template, jsonify, request, current_app
from models.sms_template import SMSTemplate
from database import db
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required, current_user
import logging
import traceback

sms_templates = Blueprint('sms_templates', __name__)

@sms_templates.route('/')
@login_required
def manage_templates():
    try:
        logging.info("Starting manage_templates route")
        logging.info(f"Current user: {current_user}")
        
        # Log database connection info
        logging.info(f"Database URI: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Fetch templates grouped by category
        logging.info("Fetching payment templates")
        payment_templates = SMSTemplate.query.filter_by(category='payment').all()
        logging.info(f"Found {len(payment_templates)} payment templates")
        
        logging.info("Fetching overdue templates")
        overdue_templates = SMSTemplate.query.filter_by(category='overdue').all()
        logging.info(f"Found {len(overdue_templates)} overdue templates")
        
        logging.info("Fetching alert templates")
        alert_templates = SMSTemplate.query.filter_by(category='alert').all()
        logging.info(f"Found {len(alert_templates)} alert templates")
        
        # Log template details
        for template in payment_templates + overdue_templates + alert_templates:
            logging.info(f"Template: {template.to_dict()}")
        
        return render_template('admin/sms_templates.html',
                             payment_templates=payment_templates or [],
                             overdue_templates=overdue_templates or [],
                             alert_templates=alert_templates or [])
    except SQLAlchemyError as e:
        error_msg = f"Database error in manage_templates: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return "Database error occurred", 500
    except Exception as e:
        error_msg = f"Unexpected error in manage_templates: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return "An unexpected error occurred", 500

@sms_templates.route('/api', methods=['POST'])
@login_required
def create_template():
    try:
        logging.info(f"Current user: {current_user}")
        data = request.json
        logging.info(f"Received data: {data}")
        template = SMSTemplate(
            name=data['name'],
            category=data['category'],
            message=data['message'],
            trigger_type=data['trigger'],
            trigger_value=data['triggerValue']
        )
        logging.info(f"Created template: {template.to_dict()}")
        db.session.add(template)
        db.session.commit()
        return jsonify({'success': True, 'template': template.to_dict()})
    except SQLAlchemyError as e:
        db.session.rollback()
        error_msg = f"Database error in create_template: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        error_msg = f"Unexpected error in create_template: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': 'An unexpected error occurred'}), 500

@sms_templates.route('/api/<int:template_id>', methods=['PUT'])
@login_required
def update_template(template_id):
    try:
        logging.info(f"Current user: {current_user}")
        template = SMSTemplate.query.get_or_404(template_id)
        logging.info(f"Found template: {template.to_dict()}")
        data = request.json
        logging.info(f"Received data: {data}")
        template.name = data['name']
        template.category = data['category']
        template.message = data['message']
        template.trigger_type = data['trigger']
        template.trigger_value = data['triggerValue']
        logging.info(f"Updated template: {template.to_dict()}")
        db.session.commit()
        return jsonify({'success': True, 'template': template.to_dict()})
    except SQLAlchemyError as e:
        db.session.rollback()
        error_msg = f"Database error in update_template: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        error_msg = f"Unexpected error in update_template: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': 'An unexpected error occurred'}), 500

@sms_templates.route('/api/<int:template_id>', methods=['DELETE'])
@login_required
def delete_template(template_id):
    try:
        logging.info(f"Current user: {current_user}")
        template = SMSTemplate.query.get_or_404(template_id)
        logging.info(f"Found template: {template.to_dict()}")
        db.session.delete(template)
        db.session.commit()
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        error_msg = f"Database error in delete_template: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        error_msg = f"Unexpected error in delete_template: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': 'An unexpected error occurred'}), 500

@sms_templates.route('/api/<int:template_id>', methods=['GET'])
@login_required
def get_template(template_id):
    try:
        logging.info(f"Current user: {current_user}")
        template = SMSTemplate.query.get_or_404(template_id)
        logging.info(f"Found template: {template.to_dict()}")
        return jsonify(template.to_dict())
    except SQLAlchemyError as e:
        error_msg = f"Database error in get_template: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        error_msg = f"Unexpected error in get_template: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': 'An unexpected error occurred'}), 500
