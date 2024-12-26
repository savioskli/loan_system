from flask import Blueprint, render_template, request, jsonify
from models.email_template import EmailTemplateType, EmailTemplate
from extensions import db
import logging

logger = logging.getLogger(__name__)
email_templates_bp = Blueprint('email_templates', __name__)

@email_templates_bp.route('/admin/email-templates', methods=['GET'])
def list_templates():
    logger.info("Fetching email templates list")
    try:
        templates = db.session.query(EmailTemplate).filter(
            EmailTemplate.is_active == True
        ).all()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template.id,
                'type': template.type,
                'subject': template.subject,
                'days': template.days_trigger,
                'content': template.content
            })
        
        logger.info(f"Successfully retrieved {len(template_list)} email templates")
        return render_template(
            'admin/email_templates/list.html',
            templates=template_list,
            template_types=[t.value for t in EmailTemplateType]
        )
    except Exception as e:
        logger.error(f"Error fetching email templates: {str(e)}", exc_info=True)
        raise

@email_templates_bp.route('/admin/email-templates/get/<int:template_id>', methods=['GET'])
def get_template(template_id):
    logger.info(f"Fetching template with ID: {template_id}")
    try:
        template = db.session.query(EmailTemplate).filter(
            EmailTemplate.id == template_id,
            EmailTemplate.is_active == True
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
                'subject': template.subject,
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

@email_templates_bp.route('/admin/email-templates/edit/<int:template_id>', methods=['POST'])
def edit_template(template_id):
    logger.info(f"Attempting to edit template with ID: {template_id}")
    try:
        template = db.session.query(EmailTemplate).filter(
            EmailTemplate.id == template_id,
            EmailTemplate.is_active == True
        ).first()
        
        if not template:
            logger.warning(f"Template not found with ID: {template_id}")
            return jsonify({
                'success': False,
                'message': 'Template not found'
            }), 404

        data = request.form
        template_type = data.get('template_type')
        template_subject = data.get('template_subject')
        template_content = data.get('template_content')
        days_trigger = data.get('days_trigger')

        # Validate required fields
        if not all([template_type, template_subject, template_content]):
            logger.error("Missing required fields in template edit request")
            return jsonify({
                'success': False,
                'message': 'Template type, subject, and content are required'
            }), 400

        # Validate template type
        if template_type not in [t.value for t in EmailTemplateType]:
            logger.error(f"Invalid template type received: {template_type}")
            return jsonify({
                'success': False,
                'message': 'Invalid template type'
            }), 400

        # Update template
        template.type = template_type
        template.subject = template_subject
        template.content = template_content
        if days_trigger:
            template.days_trigger = int(days_trigger)
        
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

@email_templates_bp.route('/admin/email-templates/preview', methods=['POST'])
def preview_template():
    logger.info("Previewing email template")
    try:
        data = request.form
        template_type = data.get('template_type')
        template_subject = data.get('template_subject', '')
        template_content = data.get('template_content', '')
        days = data.get('days_trigger')

        if not template_type:
            return jsonify({
                'success': False,
                'message': 'Template type is required'
            }), 400

        # Here you would typically add your placeholder data for preview
        preview_data = {
            'loan_amount': '5000',
            'due_date': '2024-01-15',
            'customer_name': 'John Doe',
            'payment_amount': '500',
            # Add more placeholder data as needed
        }

        # Process the template with placeholder data
        processed_subject = template_subject
        processed_content = template_content
        for key, value in preview_data.items():
            placeholder = f'{{{{{key}}}}}'
            processed_subject = processed_subject.replace(placeholder, str(value))
            processed_content = processed_content.replace(placeholder, str(value))

        return jsonify({
            'success': True,
            'preview': {
                'subject': processed_subject,
                'content': processed_content
            }
        })
    except Exception as e:
        logger.error(f"Error previewing template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@email_templates_bp.route('/admin/email-templates/create', methods=['POST'])
def create_template():
    logger.info("Creating new email template")
    try:
        data = request.form
        template_type = data.get('template_type')
        template_subject = data.get('template_subject')
        template_content = data.get('template_content')
        days_trigger = data.get('days_trigger')

        # Validate required fields
        if not all([template_type, template_subject, template_content]):
            logger.error("Missing required fields in template creation request")
            return jsonify({
                'success': False,
                'message': 'Template type, subject, and content are required'
            }), 400

        # Validate template type
        if template_type not in [t.value for t in EmailTemplateType]:
            logger.error(f"Invalid template type received: {template_type}")
            return jsonify({
                'success': False,
                'message': 'Invalid template type'
            }), 400

        # Create new template
        new_template = EmailTemplate(
            type=template_type,
            subject=template_subject,
            content=template_content,
            days_trigger=int(days_trigger) if days_trigger else None
        )
        
        db.session.add(new_template)
        db.session.commit()
        
        logger.info(f"Successfully created new template with ID: {new_template.id}")
        return jsonify({
            'success': True,
            'message': 'Template created successfully',
            'template': {
                'id': new_template.id,
                'type': new_template.type,
                'subject': new_template.subject,
                'content': new_template.content,
                'days': new_template.days_trigger
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@email_templates_bp.route('/admin/email-templates/delete/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    logger.info(f"Attempting to delete template with ID: {template_id}")
    try:
        template = db.session.query(EmailTemplate).filter(
            EmailTemplate.id == template_id,
            EmailTemplate.is_active == True
        ).first()
        
        if not template:
            logger.warning(f"Template not found with ID: {template_id}")
            return jsonify({
                'success': False,
                'message': 'Template not found'
            }), 404

        # Soft delete by setting is_active to False
        template.is_active = False
        db.session.commit()
        logger.info(f"Successfully deleted template with ID: {template_id}")
        
        return jsonify({
            'success': True,
            'message': 'Template deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
