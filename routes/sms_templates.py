from flask import Blueprint, render_template, request, jsonify
from models.sms_template import TemplateType, SMSTemplate
from extensions import db
import logging

logger = logging.getLogger(__name__)
sms_templates_bp = Blueprint('sms_templates', __name__)

@sms_templates_bp.route('/admin/sms-templates', methods=['GET'])
def list_templates():
    logger.info("Fetching SMS templates list")
    try:
        templates = db.session.query(SMSTemplate).filter(
            SMSTemplate.is_active == True
        ).all()
        
        template_list = []
        for template in templates:
            template_list.append({
                'type': template.type,
                'days': template.days_trigger,
                'content': template.content
            })
        
        logger.info(f"Successfully retrieved {len(template_list)} SMS templates")
        return render_template(
            'admin/sms_templates/list.html',
            templates=template_list,
            template_types=[t.value for t in TemplateType]
        )
    except Exception as e:
        logger.error(f"Error fetching SMS templates: {str(e)}", exc_info=True)
        raise

@sms_templates_bp.route('/admin/sms-templates/preview', methods=['POST'])
def preview_template():
    template_type = request.form.get('template_type')
    days = request.form.get('days')
    
    logger.info(f"Previewing SMS template - Type: {template_type}, Days: {days}")
    
    if days:
        try:
            days = int(days)
        except ValueError:
            logger.error(f"Invalid days value received: {days}")
            return jsonify({'preview': 'Invalid days value'}), 400
    
    try:
        template = db.session.query(SMSTemplate).filter(
            SMSTemplate.type == template_type,
            SMSTemplate.days_trigger == days,
            SMSTemplate.is_active == True
        ).first()
        
        if not template:
            logger.warning(f"Template not found - Type: {template_type}, Days: {days}")
            return jsonify({'preview': 'Template not found'}), 404
        
        # Sample data for preview
        sample_data = {
            'client_name': 'John Doe',
            'amount': '10,000',
            'account_number': '1234567890',
            'support_number': '0700123456',
            'next_amount': '12,000',
            'next_date': '2024-01-24',
            'remaining_balance': '50,000'
        }
        
        logger.debug(f"Attempting to format template with sample data: {sample_data}")
        preview = template.content.format(**sample_data)
        logger.info("Successfully generated template preview")
        return jsonify({'preview': preview})
        
    except KeyError as e:
        logger.error(f"Missing variable in template: {str(e)}")
        return jsonify({'preview': f'Error: Missing variable {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error generating template preview: {str(e)}", exc_info=True)
        return jsonify({'preview': f'Error: {str(e)}'}), 400