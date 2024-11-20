from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.branch import Branch
from forms.branch_forms import NewBranchForm, EditBranchForm
from extensions import db
import logging

branch_bp = Blueprint('branch', __name__)
logger = logging.getLogger(__name__)

@branch_bp.route('/admin/branches')
@login_required
def manage_branches():
    """List all branches."""
    branches = Branch.query.all()
    return render_template('admin/branches/index.html', branches=branches)

@branch_bp.route('/admin/branches/new', methods=['GET', 'POST'])
@login_required
def new_branch():
    """Create a new branch."""
    form = NewBranchForm()
    if form.validate_on_submit():
        try:
            branch = Branch(
                branch_code=form.branch_code.data,
                branch_name=form.branch_name.data,
                lower_limit=form.lower_limit.data,
                upper_limit=form.upper_limit.data,
                is_active=form.is_active.data,
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(branch)
            db.session.commit()
            logger.info(f"Branch {branch.branch_name} created by {current_user.username}")
            flash('Branch created successfully.', 'success')
            return redirect(url_for('branch.manage_branches'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating branch: {str(e)}")
            flash('An error occurred while creating the branch.', 'error')
    
    return render_template('admin/branches/new.html', form=form)

@branch_bp.route('/admin/branches/<int:branch_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_branch(branch_id):
    """Edit an existing branch."""
    branch = Branch.query.get_or_404(branch_id)
    form = EditBranchForm(branch_id=branch_id, obj=branch)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(branch)
            branch.updated_by = current_user.id
            db.session.commit()
            logger.info(f"Branch {branch.branch_name} updated by {current_user.username}")
            flash('Branch updated successfully.', 'success')
            return redirect(url_for('branch.manage_branches'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating branch: {str(e)}")
            flash('An error occurred while updating the branch.', 'error')
    
    return render_template('admin/branches/edit.html', form=form, branch=branch)

@branch_bp.route('/admin/branches/<int:branch_id>/delete', methods=['POST'])
@login_required
def delete_branch(branch_id):
    """Delete a branch."""
    branch = Branch.query.get_or_404(branch_id)
    try:
        db.session.delete(branch)
        db.session.commit()
        logger.info(f"Branch {branch.branch_name} deleted by {current_user.username}")
        flash('Branch deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting branch: {str(e)}")
        flash('An error occurred while deleting the branch.', 'error')
    
    return redirect(url_for('branch.manage_branches'))
