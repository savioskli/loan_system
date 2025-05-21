from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.branch_limit import BranchLimit
from forms.branch_limit_forms import NewBranchLimitForm, EditBranchLimitForm
from extensions import db
import logging

branch_limit_bp = Blueprint('branch_limit', __name__)
logger = logging.getLogger(__name__)

@branch_limit_bp.route('/admin/branch-limits')
@login_required
def manage_branch_limits():
    """List all branch limits."""
    branch_limits = BranchLimit.query.all()
    return render_template('admin/branch_limits/index.html', branch_limits=branch_limits)

@branch_limit_bp.route('/admin/branch-limits/new', methods=['GET', 'POST'])
@login_required
def new_branch_limit():
    """Create a new branch limit."""
    form = NewBranchLimitForm()
    if form.validate_on_submit():
        try:
            branch_limit = BranchLimit(
                branch_id=form.branch_id.data,
                min_amount=form.min_amount.data,
                max_amount=form.max_amount.data,
                created_by=current_user.id
            )
            db.session.add(branch_limit)
            db.session.commit()
            logger.info(f"Branch limit created for branch ID {branch_limit.branch_id} by {current_user.username}")
            flash(f'Branch limit created successfully.', 'success')
            return redirect(url_for('branch_limit.manage_branch_limits'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating branch limit: {str(e)}")
            flash('An error occurred while creating the branch limit.', 'error')
    
    return render_template('admin/branch_limits/new.html', form=form)

@branch_limit_bp.route('/admin/branch-limits/<int:limit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_branch_limit(limit_id):
    """Edit an existing branch limit."""
    branch_limit = BranchLimit.query.get_or_404(limit_id)
    form = EditBranchLimitForm(limit_id=limit_id, obj=branch_limit)
    
    if form.validate_on_submit():
        try:
            branch_limit.branch_id = form.branch_id.data
            branch_limit.min_amount = form.min_amount.data
            branch_limit.max_amount = form.max_amount.data
            branch_limit.is_active = form.is_active.data
            branch_limit.updated_by = current_user.id
            
            db.session.commit()
            logger.info(f"Branch limit {limit_id} updated by {current_user.username}")
            flash('Branch limit updated successfully.', 'success')
            return redirect(url_for('branch_limit.manage_branch_limits'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating branch limit: {str(e)}")
            flash('An error occurred while updating the branch limit.', 'error')
    
    return render_template('admin/branch_limits/edit.html', form=form, branch_limit=branch_limit)

@branch_limit_bp.route('/admin/branch-limits/<int:limit_id>/delete', methods=['POST'])
@login_required
def delete_branch_limit(limit_id):
    """Delete a branch limit."""
    branch_limit = BranchLimit.query.get_or_404(limit_id)
    
    try:
        branch_limit.is_active = False
        branch_limit.updated_by = current_user.id
        db.session.commit()
        logger.info(f"Branch limit {limit_id} deleted by {current_user.username}")
        flash('Branch limit deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting branch limit: {str(e)}")
        flash('An error occurred while deleting the branch limit.', 'error')
    
    return redirect(url_for('branch_limit.manage_branch_limits'))
