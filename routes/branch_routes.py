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
                code=form.code.data,
                name=form.name.data,
                address=form.address.data if hasattr(form, 'address') else None,
                created_by=current_user.id
            )
            db.session.add(branch)
            db.session.commit()
            logger.info(f"Branch {branch.name} created by {current_user.username}")
            flash(f'Branch {branch.name} created successfully.', 'success')
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
            branch.code = form.code.data
            branch.name = form.name.data
            branch.address = form.address.data
            branch.is_active = form.is_active.data
            branch.updated_by = current_user.id
            
            db.session.commit()
            logger.info(f"Branch {branch.name} updated by {current_user.username}")
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
    branch_name = branch.name
    try:
        # Check if there are any staff members assigned to this branch
        if branch.staff_members:
            flash('Cannot delete branch with assigned staff members. Please reassign or remove staff members first.', 'error')
            return redirect(url_for('branch.manage_branches'))
            
        db.session.delete(branch)
        db.session.commit()
        logger.info(f"Branch {branch_name} deleted by {current_user.username}")
        flash('Branch deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting branch: {str(e)}")
        flash('An error occurred while deleting the branch. Please try again.', 'error')
    
    return redirect(url_for('branch.manage_branches'))
