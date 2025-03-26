from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.post_disbursement_workflows import WorkflowDefinition, WorkflowStep, WorkflowTransition
from models.role import Role
from extensions import db
from datetime import datetime
import json

post_disbursement_workflows_bp = Blueprint('post_disbursement_workflows', __name__)

@post_disbursement_workflows_bp.route('/admin/workflows', methods=['GET'])
@login_required
def list_workflows():
    """List all workflow definitions"""
    workflows = WorkflowDefinition.query.all()
    return render_template('admin/post_disbursement_workflows/workflows.html', workflows=workflows)

@post_disbursement_workflows_bp.route('/admin/workflows/create', methods=['GET', 'POST'])
@login_required
def create_workflow():
    """Create a new workflow definition"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Workflow name is required', 'error')
            return redirect(url_for('post_disbursement_workflows.create_workflow'))
        
        workflow = WorkflowDefinition(
            name=name,
            description=description,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.session.add(workflow)
        db.session.commit()
        
        flash('Workflow created successfully', 'success')
        return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow.id))
    
    return render_template('admin/post_disbursement_workflows/create_workflow.html')

@post_disbursement_workflows_bp.route('/admin/workflows/<int:workflow_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workflow(workflow_id):
    """Edit a workflow definition and manage its steps"""
    workflow = WorkflowDefinition.query.get_or_404(workflow_id)
    roles = Role.query.filter_by(is_active=True).all()
    steps = WorkflowStep.query.filter_by(workflow_id=workflow_id).order_by(WorkflowStep.step_order).all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        is_active = request.form.get('is_active') == 'on'
        
        if not name:
            flash('Workflow name is required', 'error')
            return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))
        
        workflow.name = name
        workflow.description = description
        workflow.is_active = is_active
        workflow.updated_by = current_user.id
        workflow.updated_at = datetime.now()
        
        db.session.commit()
        flash('Workflow updated successfully', 'success')
    
    return render_template('admin/post_disbursement_workflows/edit_workflow.html', 
                          workflow=workflow, roles=roles, steps=steps)

@post_disbursement_workflows_bp.route('/admin/workflows/<int:workflow_id>/steps/create', methods=['POST'])
@login_required
def create_step(workflow_id):
    """Create a new workflow step"""
    # workflow_id is already passed as a parameter from the route
    workflow = WorkflowDefinition.query.get_or_404(workflow_id)
    
    name = request.form.get('name')
    description = request.form.get('description')
    role_id = request.form.get('role_id', type=int)
    is_start_step = request.form.get('is_start_step') == 'on'
    
    if not name or not role_id:
        flash('Step name and role are required', 'error')
        return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))
    
    # Get the highest current step order
    max_order = db.session.query(db.func.max(WorkflowStep.step_order)).filter_by(workflow_id=workflow_id).scalar() or 0
    
    # If this is a start step, update any existing start steps
    if is_start_step:
        existing_start_steps = WorkflowStep.query.filter_by(workflow_id=workflow_id, is_start_step=True).all()
        for step in existing_start_steps:
            step.is_start_step = False
    
    step = WorkflowStep(
        workflow_id=workflow_id,
        name=name,
        description=description,
        role_id=role_id,
        is_start_step=is_start_step,
        step_order=max_order + 1
    )
    
    db.session.add(step)
    db.session.commit()
    
    flash('Workflow step created successfully', 'success')
    return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))

@post_disbursement_workflows_bp.route('/admin/workflows/steps/<int:step_id>/edit', methods=['POST'])
@login_required
def edit_step(step_id):
    """Edit a workflow step"""
    step = WorkflowStep.query.get_or_404(step_id)
    workflow_id = step.workflow_id
    
    name = request.form.get('name')
    description = request.form.get('description')
    role_id = request.form.get('role_id', type=int)
    is_start_step = request.form.get('is_start_step') == 'on'
    
    if not name or not role_id:
        flash('Step name and role are required', 'error')
        return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))
    
    # If this is a start step, update any existing start steps
    if is_start_step and not step.is_start_step:
        existing_start_steps = WorkflowStep.query.filter_by(workflow_id=workflow_id, is_start_step=True).all()
        for existing_step in existing_start_steps:
            existing_step.is_start_step = False
    
    step.name = name
    step.description = description
    step.role_id = role_id
    step.is_start_step = is_start_step
    step.updated_at = datetime.now()
    
    db.session.commit()
    
    flash('Workflow step updated successfully', 'success')
    return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))

@post_disbursement_workflows_bp.route('/admin/workflows/steps/<int:step_id>/update', methods=['POST'])
@login_required
def update_step(step_id):
    """Update a workflow step"""
    step = WorkflowStep.query.get_or_404(step_id)
    workflow_id = step.workflow_id
    
    name = request.form.get('name')
    description = request.form.get('description')
    role_id = request.form.get('role_id', type=int)
    is_start_step = request.form.get('is_start_step') == 'on'
    
    if not name or not role_id:
        flash('Step name and role are required', 'error')
        return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))
    
    # If this is a start step, update any existing start steps
    if is_start_step and not step.is_start_step:
        existing_start_steps = WorkflowStep.query.filter_by(workflow_id=workflow_id, is_start_step=True).all()
        for existing_step in existing_start_steps:
            existing_step.is_start_step = False
    
    # Update the step
    step.name = name
    step.description = description
    step.role_id = role_id
    step.is_start_step = is_start_step
    
    db.session.commit()
    
    flash('Workflow step updated successfully', 'success')
    return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))

@post_disbursement_workflows_bp.route('/admin/workflows/steps/<int:step_id>/delete', methods=['POST'])
@login_required
def delete_step(step_id):
    """Delete a workflow step"""
    step = WorkflowStep.query.get_or_404(step_id)
    workflow_id = step.workflow_id
    
    # Check if there are any transitions using this step
    from_transitions = WorkflowTransition.query.filter_by(from_step_id=step_id).all()
    to_transitions = WorkflowTransition.query.filter_by(to_step_id=step_id).all()
    
    if from_transitions or to_transitions:
        flash('Cannot delete step: it is used in workflow transitions', 'error')
        return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))
    
    db.session.delete(step)
    
    # Reorder remaining steps
    remaining_steps = WorkflowStep.query.filter_by(workflow_id=workflow_id).order_by(WorkflowStep.step_order).all()
    for i, remaining_step in enumerate(remaining_steps):
        remaining_step.step_order = i + 1
    
    db.session.commit()
    
    flash('Workflow step deleted successfully', 'success')
    return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))

@post_disbursement_workflows_bp.route('/admin/workflows/steps/reorder', methods=['POST'])
@login_required
def reorder_steps():
    """Reorder workflow steps"""
    step_order = request.json.get('stepOrder', [])
    
    for order_data in step_order:
        step_id = order_data.get('id')
        new_order = order_data.get('order')
        
        step = WorkflowStep.query.get(step_id)
        if step:
            step.step_order = new_order
    
    db.session.commit()
    
    return jsonify({'success': True})

@post_disbursement_workflows_bp.route('/admin/workflows/transitions/create', methods=['POST'])
@login_required
def create_transition():
    """Create a new workflow transition between steps"""
    workflow_id = request.form.get('workflow_id', type=int)
    from_step_id = request.form.get('from_step_id', type=int)
    to_step_id = request.form.get('to_step_id', type=int)
    transition_name = request.form.get('transition_name')
    
    if not from_step_id or not to_step_id or not transition_name:
        flash('From step, to step, and transition name are required', 'error')
        return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))
    
    # Check if the transition already exists
    existing = WorkflowTransition.query.filter_by(
        workflow_id=workflow_id,
        from_step_id=from_step_id,
        to_step_id=to_step_id
    ).first()
    
    if existing:
        flash('A transition between these steps already exists', 'error')
        return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))
    
    transition = WorkflowTransition(
        workflow_id=workflow_id,
        from_step_id=from_step_id,
        to_step_id=to_step_id,
        transition_name=transition_name
    )
    
    db.session.add(transition)
    db.session.commit()
    
    flash('Workflow transition created successfully', 'success')
    return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))

@post_disbursement_workflows_bp.route('/admin/workflows/transitions/<int:transition_id>/delete', methods=['POST'])
@login_required
def delete_transition(transition_id):
    """Delete a workflow transition"""
    transition = WorkflowTransition.query.get_or_404(transition_id)
    workflow_id = transition.workflow_id
    
    db.session.delete(transition)
    db.session.commit()
    
    flash('Workflow transition deleted successfully', 'success')
    return redirect(url_for('post_disbursement_workflows.edit_workflow', workflow_id=workflow_id))

@post_disbursement_workflows_bp.route('/admin/workflows/<int:workflow_id>/delete', methods=['POST'])
@login_required
def delete_workflow(workflow_id):
    """Delete a workflow definition and all its steps and transitions"""
    workflow = WorkflowDefinition.query.get_or_404(workflow_id)
    
    # Check if the workflow is being used by any instances
    # This would require checking the WorkflowInstance model if implemented
    
    db.session.delete(workflow)  # This will cascade delete steps and transitions
    db.session.commit()
    
    flash('Workflow deleted successfully', 'success')
    return redirect(url_for('post_disbursement_workflows.list_workflows'))

@post_disbursement_workflows_bp.route('/admin/workflows/<int:workflow_id>/steps', methods=['GET'])
@login_required
def get_workflow_steps(workflow_id):
    """Get all steps for a workflow as JSON for the frontend"""
    steps = WorkflowStep.query.filter_by(workflow_id=workflow_id).order_by(WorkflowStep.step_order).all()
    
    steps_data = [{
        'id': step.id,
        'name': step.name,
        'order': step.step_order,
        'role_id': step.role_id,
        'role_name': step.role.name if step.role else 'Unknown',
        'is_start_step': step.is_start_step
    } for step in steps]
    
    return jsonify(steps_data)

@post_disbursement_workflows_bp.route('/admin/workflows/<int:workflow_id>/transitions', methods=['GET'])
@login_required
def get_workflow_transitions(workflow_id):
    """Get all transitions for a workflow as JSON for the frontend"""
    transitions = WorkflowTransition.query.filter_by(workflow_id=workflow_id).all()
    
    transitions_data = [{
        'id': transition.id,
        'from_step_id': transition.from_step_id,
        'from_step_name': transition.from_step.name if transition.from_step else 'Unknown',
        'to_step_id': transition.to_step_id,
        'to_step_name': transition.to_step.name if transition.to_step else 'Unknown',
        'transition_name': transition.transition_name
    } for transition in transitions]
    
    return jsonify(transitions_data)
