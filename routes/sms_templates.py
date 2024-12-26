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
                'id': template.id,
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

@sms_templates_bp.route('/admin/sms-templates/get/<int:template_id>', methods=['GET'])
def get_template(template_id):
    logger.info(f"Fetching template with ID: {template_id}")
    try:
        template = db.session.query(SMSTemplate).filter(
            SMSTemplate.id == template_id,
            SMSTemplate.is_active == True
        ).first()
        
        if not template:
            logger.warning(f"Template not found with ID: {template_id}")
            return jsonify({
                'success': False,
                'message': 'Template not found'
            }), 404
        
        return jsonify({
            'success': True,
            'template': {
                'type': template.type,
                'days': template.days_trigger,
                'content': template.content
            }
        })
    except Exception as e:
        logger.error(f"Error fetching template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sms_templates_bp.route('/admin/sms-templates/edit/<int:template_id>', methods=['POST'])
def edit_template(template_id):
    logger.info(f"Attempting to edit template with ID: {template_id}")
    try:
        template = db.session.query(SMSTemplate).filter(
            SMSTemplate.id == template_id,
            SMSTemplate.is_active == True
        ).first()
        
        if not template:
            logger.warning(f"Template not found with ID: {template_id}")
            return jsonify({
                'success': False,
                'message': 'Template not found'
            }), 404

        data = request.form
        template_type = data.get('template_type')
        template_content = data.get('template_content')

        # Validate required fields
        if not all([template_type, template_content]):
            logger.error("Missing required fields in template edit request")
            return jsonify({
                'success': False,
                'message': 'Template type and content are required'
            }), 400

        # Validate template type
        if template_type not in [t.value for t in TemplateType]:
            logger.error(f"Invalid template type received: {template_type}")
            return jsonify({
                'success': False,
                'message': 'Invalid template type'
            }), 400

        # Update template
        template.type = template_type
        template.content = template_content

        # Update days_trigger if applicable
        days = data.get('days')
        if days:
            try:
                template.days_trigger = int(days)
            except ValueError:
                logger.error(f"Invalid days value received: {days}")
                return jsonify({
                    'success': False,
                    'message': 'Invalid days value'
                }), 400
        else:
            template.days_trigger = None

        db.session.commit()
        logger.info(f"Successfully updated template with ID: {template_id}")
        return jsonify({
            'success': True,
            'message': 'Template updated successfully'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sms_templates_bp.route('/admin/sms-templates/preview', methods=['POST'])
def preview_template():
    template_type = request.form.get('template_type')
    days_trigger = request.form.get('days_trigger')
    
    logger.info(f"Previewing SMS template - Type: {template_type}, Days: {days_trigger}")
    
    if days_trigger:
        try:
            days_trigger = int(days_trigger)
        except ValueError:
            logger.error(f"Invalid days value received: {days_trigger}")
            return jsonify({'preview': 'Invalid days value'}), 400
    
    try:
        template = db.session.query(SMSTemplate).filter(
            SMSTemplate.type == template_type,
            SMSTemplate.days_trigger == days_trigger,
            SMSTemplate.is_active == True
        ).first()
        
        if not template:
            logger.warning(f"Template not found - Type: {template_type}, Days: {days_trigger}")
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
        
        preview = template.content.format(**sample_data)
        logger.info("Successfully generated template preview")
        return jsonify({'preview': preview})
        
    except KeyError as e:
        logger.error(f"Missing variable in template: {str(e)}")
        return jsonify({'preview': f'Error: Missing variable {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error generating template preview: {str(e)}", exc_info=True)
        return jsonify({'preview': f'Error: {str(e)}'}), 400

@sms_templates_bp.route('/admin/sms-templates/create', methods=['POST'])
def create_template():
    logger.info("Attempting to create new SMS template")
    try:
        data = request.form
        template_type = data.get('template_type')
        template_content = data.get('template_content')

        # Validate required fields
        if not all([template_type, template_content]):
            logger.error("Missing required fields in template creation request")
            return jsonify({
                'success': False,
                'message': 'Template type and content are required'
            }), 400

        # Validate template type
        if template_type not in [t.value for t in TemplateType]:
            logger.error(f"Invalid template type received: {template_type}")
            return jsonify({
                'success': False,
                'message': 'Invalid template type'
            }), 400

        # Check if template already exists
        existing_template = db.session.query(SMSTemplate).filter(
            SMSTemplate.type == template_type,
            SMSTemplate.is_active == True
        ).first()

        if existing_template:
            logger.warning(f"Template already exists for type: {template_type}")
            return jsonify({
                'success': False,
                'message': 'Template already exists for this type'
            }), 400

        # Create new template
        new_template = SMSTemplate(
            type=template_type,
            content=template_content,
            is_active=True
        )

        # Add days_trigger if applicable
        days = data.get('days')
        if days:
            try:
                new_template.days_trigger = int(days)
            except ValueError:
                logger.error(f"Invalid days value received: {days}")
                return jsonify({
                    'success': False,
                    'message': 'Invalid days value'
                }), 400

        db.session.add(new_template)
        db.session.commit()

        logger.info(f"Successfully created new template of type: {template_type}")
        return jsonify({
            'success': True,
            'message': 'Template created successfully'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating SMS template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500