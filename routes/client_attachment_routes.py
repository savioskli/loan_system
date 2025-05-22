from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.client_attachment import ClientAttachment
from models.client_type import ClientType
from extensions import db
from datetime import datetime

client_attachment_bp = Blueprint('client_attachments', __name__)

@client_attachment_bp.route('/admin/client-attachments')
@login_required
def index():
    attachments = ClientAttachment.query.all()
    client_types = ClientType.query.all()
    return render_template('admin/client_attachments/index.html', 
                         attachments=attachments,
                         client_types=client_types)

@client_attachment_bp.route('/admin/client-attachments/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            # Get form data
            client_type_id = request.form.get('client_type_id')
            name = request.form.get('name')
            attachment_type = request.form.get('attachment_type')
            size_limit = request.form.get('size_limit')
            is_mandatory = request.form.get('is_mandatory', 'false') == 'true'
            status = request.form.get('status', 'active')

            # Validate required fields
            if not all([client_type_id, name, attachment_type]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('client_attachments.create'))

            # Create attachment
            attachment = ClientAttachment(
                client_type_id=int(client_type_id),
                name=name,
                attachment_type=attachment_type,
                size_limit=int(size_limit) if size_limit else None,
                is_mandatory=is_mandatory,
                status=status,
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(attachment)
            db.session.commit()
            flash('Client attachment created successfully', 'success')
            return redirect(url_for('client_attachments.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating client attachment: {str(e)}', 'error')
    
    client_types = ClientType.query.all()
    return render_template('admin/client_attachments/create.html', client_types=client_types)

@client_attachment_bp.route('/admin/client-attachments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    attachment = ClientAttachment.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            attachment.client_type_id = request.form['client_type_id']
            attachment.name = request.form['name']
            attachment.attachment_type = request.form['attachment_type']
            attachment.size_limit = int(request.form['size_limit']) if request.form['size_limit'] else None
            attachment.is_mandatory = request.form.get('is_mandatory') == 'true'
            attachment.status = request.form['status']
            attachment.updated_by = current_user.id
            attachment.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Client attachment updated successfully', 'success')
            return redirect(url_for('client_attachments.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating client attachment: {str(e)}', 'error')
    
    client_types = ClientType.query.all()
    return render_template('admin/client_attachments/edit.html', 
                         attachment=attachment,
                         client_types=client_types)

@client_attachment_bp.route('/admin/client-attachments/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    attachment = ClientAttachment.query.get_or_404(id)
    try:
        db.session.delete(attachment)
        db.session.commit()
        return jsonify({'message': 'Client attachment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting client attachment: {str(e)}'}), 500
