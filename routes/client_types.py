from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models.client_type import ClientType
from forms.client_type import ClientTypeForm
from extensions import db, csrf

client_types_bp = Blueprint('client_types', __name__, url_prefix='/admin/client-types')

@client_types_bp.route('/')
@login_required
def manage_client_types():
    client_types = ClientType.query.order_by(ClientType.created_at.desc()).all()
    return render_template('admin/client_types/index.html', client_types=client_types)

@client_types_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_client_type():
    form = ClientTypeForm()
    if form.validate_on_submit():
        client_type = ClientType(
            client_code=form.client_code.data,
            client_name=form.client_name.data,
            effective_from=form.effective_from.data,
            effective_to=form.effective_to.data,
            status=form.status.data
        )
        db.session.add(client_type)
        try:
            db.session.commit()
            flash('Client type created successfully!', 'success')
            return redirect(url_for('client_types.manage_client_types'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating client type. Please try again.', 'error')
    return render_template('admin/client_types/form.html', form=form, title='New Client Type')

@client_types_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client_type(id):
    client_type = ClientType.query.get_or_404(id)
    form = ClientTypeForm(obj=client_type)
    if form.validate_on_submit():
        client_type.client_code = form.client_code.data
        client_type.client_name = form.client_name.data
        client_type.effective_from = form.effective_from.data
        client_type.effective_to = form.effective_to.data
        client_type.status = form.status.data
        try:
            db.session.commit()
            flash('Client type updated successfully!', 'success')
            return redirect(url_for('client_types.manage_client_types'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating client type. Please try again.', 'error')
    return render_template('admin/client_types/form.html', form=form, title='Edit Client Type')

@client_types_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_client_type(id):
    client_type = ClientType.query.get_or_404(id)
    try:
        db.session.delete(client_type)
        db.session.commit()
        flash('Client type deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('Error deleting client type. Please try again.', 'error')
        return jsonify({'success': False}), 500
