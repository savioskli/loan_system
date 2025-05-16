from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from models.impact import ImpactCategory, ImpactMetric
from models.loan_impact import LoanImpact, ImpactValue, ImpactEvidence
from models.staff import Staff
from models.core_banking import CoreBankingSystem
from models.post_disbursement_modules import ExpectedStructure, ActualStructure, PostDisbursementModule
from models.post_disbursement_workflows import WorkflowDefinition, WorkflowStep, WorkflowInstance, WorkflowHistory, WorkflowTransition
from utils.decorators import admin_required
from extensions import db
import mysql.connector
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from sqlalchemy import desc

impact_assessment_bp = Blueprint('impact_assessment', __name__)

@impact_assessment_bp.route('/user/impact_assessment', methods=['GET'])
@login_required
def impact_assessment():
    """Render the impact assessment dashboard"""
    # Get visible modules for sidebar
    visible_modules = PostDisbursementModule.query.filter_by(hidden=False).order_by(PostDisbursementModule.order).all()
    return render_template('user/impact/assessment.html', visible_modules=visible_modules)

@impact_assessment_bp.route('/user/get_loans_for_impact', methods=['GET'])
@login_required
def get_loans_for_impact():
    """Get loans for impact assessment"""
    try:
        # Get the active core banking system
        core_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_system:
            return jsonify({'error': 'No active core banking system configured'}), 400

        # Connect to core banking database
        try:
            auth_credentials = core_system.auth_credentials_dict
        except (json.JSONDecodeError, TypeError) as e:
            current_app.logger.error(f"Error decoding auth credentials: {str(e)}")
            auth_credentials = {'username': 'root', 'password': ''}

        core_banking_config = {
            'host': core_system.base_url,
            'port': core_system.port or 3306,
            'user': auth_credentials.get('username', 'root'),
            'password': auth_credentials.get('password', ''),
            'database': core_system.database_name,
            'auth_plugin': 'mysql_native_password'
        }

        conn = mysql.connector.connect(**core_banking_config)
        cursor = conn.cursor(dictionary=True)

        # Use module ID 1 for loan details
        module_id = 1

        # Retrieve the mapping data
        def get_mapping_for_module(module_id):
            try:
                expected_mappings = ExpectedStructure.query.filter_by(module_id=module_id).all()
                mapping = {}
                for expected in expected_mappings:
                    actual = ActualStructure.query.filter_by(expected_structure_id=expected.id).first()
                    if not actual:
                        raise Exception(f"No mapping found for expected table {expected.table_name}")
                    
                    # Retrieve expected and actual columns as lists
                    expected_columns = expected.columns
                    actual_columns = actual.columns
                    
                    # Create a dictionary mapping expected to actual columns
                    columns_dict = dict(zip(expected_columns, actual_columns))
                    
                    mapping[expected.table_name] = {
                        "actual_table_name": actual.table_name,
                        "columns": columns_dict
                    }
                return mapping
            except Exception as e:
                current_app.logger.error(f"Error retrieving mapping data: {str(e)}")
                raise

        try:
            mapping = get_mapping_for_module(module_id)
        except Exception as e:
            return jsonify({'error': f'Error retrieving mapping data: {str(e)}'}), 500

        # Build dynamic query
        def build_dynamic_query(mapping):
            try:
                ll = mapping.get("LoanLedgerEntries", {})
                ld = mapping.get("LoanDisbursements", {})
                la = mapping.get("LoanApplications", {})
                m = mapping.get("Members", {})
        
                # Ensure that the necessary columns are present in the mapping
                required_ll_columns = ["LoanID", "LedgerID", "OutstandingBalance"]
                required_ld_columns = ["LoanAppID", "LoanStatus"]
                required_la_columns = ["LoanAppID", "LoanNo", "LoanAmount", "MemberID"]
                required_m_columns = ["MemberID", "FirstName", "LastName"]
        
                if not all(column in ll.get("columns", {}) for column in required_ll_columns):
                    raise KeyError(f"Missing columns in LoanLedgerEntries mapping")
        
                if not all(column in ld.get("columns", {}) for column in required_ld_columns):
                    raise KeyError(f"Missing columns in LoanDisbursements mapping")
        
                if not all(column in la.get("columns", {}) for column in required_la_columns):
                    raise KeyError(f"Missing columns in LoanApplications mapping")
        
                if not all(column in m.get("columns", {}) for column in required_m_columns):
                    raise KeyError(f"Missing columns in Members mapping")
        
                query = f"""
                SELECT
                    l.{ll["columns"]["LoanID"]} AS LoanID,
                    l.{ll["columns"]["OutstandingBalance"]} AS OutstandingBalance,
                    la.{la["columns"]["LoanNo"]} AS LoanNo,
                    la.{la["columns"]["LoanAmount"]} AS LoanAmount,
                    CONCAT(m.{m["columns"]["FirstName"]}, ' ', m.{m["columns"]["LastName"]}) AS CustomerName,
                    m.{m["columns"]["MemberID"]} AS MemberID,
                    ld.{ld["columns"]["LoanStatus"]} AS LoanStatus
                FROM
                    {ll["actual_table_name"]} l
                JOIN
                    {ld["actual_table_name"]} ld ON l.{ll["columns"]["LoanID"]} = ld.{ld["columns"]["LoanAppID"]}
                JOIN
                    {la["actual_table_name"]} la ON ld.{ld["columns"]["LoanAppID"]} = la.{la["columns"]["LoanAppID"]}
                JOIN
                    {m["actual_table_name"]} m ON la.{la["columns"]["MemberID"]} = m.{m["columns"]["MemberID"]}
                WHERE
                    ld.{ld["columns"]["LoanStatus"]} = 'Active'
                    AND l.{ll["columns"]["OutstandingBalance"]} > 0
                ORDER BY
                    l.{ll["columns"]["LoanID"]} DESC
                """
                return query
            except Exception as e:
                current_app.logger.error(f"Error building dynamic query: {str(e)}")
                raise

        try:
            query = build_dynamic_query(mapping)
            current_app.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            loans = cursor.fetchall()
            
            # Add impact assessment status and workflow information to each loan
            for loan in loans:
                loan_impact = LoanImpact.query.filter_by(loan_id=loan['LoanID']).first()
                if loan_impact:
                    loan['has_impact'] = True
                    loan['impact_status'] = loan_impact.verification_status
                    
                    # Add workflow information if available
                    if loan_impact.workflow_instance_id:
                        workflow_instance = WorkflowInstance.query.get(loan_impact.workflow_instance_id)
                        if workflow_instance:
                            current_step = WorkflowStep.query.get(workflow_instance.current_step_id)
                            loan['workflow_instance_id'] = workflow_instance.id
                            loan['workflow_status'] = current_step.name if current_step else 'Unknown'
                            
                            # Get all available transitions for this step
                            transitions = WorkflowTransition.query.filter_by(
                                workflow_id=workflow_instance.workflow_id,
                                from_step_id=workflow_instance.current_step_id
                            ).all()
                            
                            if transitions:
                                # Add all available transitions to the loan data
                                loan['transitions'] = []
                                for transition in transitions:
                                    # Get the target step name
                                    to_step = WorkflowStep.query.get(transition.to_step_id)
                                    
                                    # Check if user has permission to perform this transition
                                    can_perform = False
                                    
                                    # Admin can perform any transition
                                    if current_user.role_id == 1:
                                        can_perform = True
                                    # Non-admin can only perform transitions if their role matches the current step's role
                                    elif current_step.role_id == current_user.role_id:
                                        can_perform = True
                                    
                                    # Only add transitions the user can perform
                                    if can_perform:
                                        loan['transitions'].append({
                                            'id': transition.id,
                                            'name': transition.transition_name,
                                            'to_step_name': to_step.name if to_step else 'Unknown'
                                        })
                else:
                    loan['has_impact'] = False
                    loan['impact_status'] = 'Not Submitted'
                    loan['workflow_status'] = None
            
            return jsonify({'data': loans})
        except Exception as e:
            current_app.logger.error(f"Error executing query: {str(e)}")
            return jsonify({'error': f'Error executing query: {str(e)}'}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@impact_assessment_bp.route('/user/impact_assessment/<int:loan_id>', methods=['GET'])
@login_required
def impact_assessment_form(loan_id):
    """Render the impact assessment form for a specific loan"""
    # Get all active impact categories
    categories = ImpactCategory.query.filter_by(active=True).all()
    
    # Check if loan already has impact assessment
    loan_impact = LoanImpact.query.filter_by(loan_id=loan_id).first()
    
    # If assessment exists and has a workflow, check if user has permission to edit
    if loan_impact and loan_impact.workflow_instance_id:
        workflow_instance = WorkflowInstance.query.get(loan_impact.workflow_instance_id)
        if workflow_instance:
            current_step = WorkflowStep.query.get(workflow_instance.current_step_id)
            
            # Only allow editing if user has the role for the current step or is an admin
            if current_step and current_step.role_id != current_user.role_id and current_user.role_id != 1:
                current_app.logger.info(f'User {current_user.id} with role {current_user.role_id} attempted to edit assessment in step {current_step.name} (role {current_step.role_id})')
                flash('You do not have permission to edit this assessment at its current workflow step', 'error')
                return redirect(url_for('impact_assessment_bp.view_impact_assessment', loan_id=loan_id))
    
    # Get existing impact values if this is an update
    existing_values = {}
    if loan_impact:
        # Get the metrics for this category
        metrics = ImpactMetric.query.filter_by(impact_category_id=loan_impact.impact_category_id).all()
        
        # Get the impact values for this loan impact
        impact_values = ImpactValue.query.filter_by(loan_impact_id=loan_impact.id).all()
        
        # Create a dictionary of metric values for easy access
        for value in impact_values:
            existing_values[value.impact_metric_id] = value.value
        
        # Get the evidence files
        evidence_files = ImpactEvidence.query.filter_by(loan_impact_id=loan_impact.id).all()
    else:
        metrics = []
        evidence_files = []
    
    # Get visible modules for sidebar
    visible_modules = PostDisbursementModule.query.filter_by(hidden=False).order_by(PostDisbursementModule.order).all()
    
    return render_template('user/impact/assessment_form.html', 
                           loan_id=loan_id, 
                           categories=categories,
                           loan_impact=loan_impact,
                           existing_values=existing_values,
                           evidence_files=evidence_files,
                           visible_modules=visible_modules)

@impact_assessment_bp.route('/user/get_metrics/<int:category_id>', methods=['GET'])
@login_required
def get_metrics(category_id):
    """Get metrics for a specific impact category"""
    metrics = ImpactMetric.query.filter_by(impact_category_id=category_id, active=True).all()
    metrics_list = [{
        'id': metric.id,
        'name': metric.name,
        'data_type': metric.data_type,
        'unit': metric.unit,
        'required': metric.required
    } for metric in metrics]
    
    return jsonify({'metrics': metrics_list})

@impact_assessment_bp.route('/user/submit_impact_assessment', methods=['POST'])
@login_required
def submit_impact_assessment():
    """Submit impact assessment for a loan"""
    try:
        data = request.form
        loan_id = data.get('loan_id')
        category_id = data.get('category_id')
        
        if not loan_id or not category_id:
            return jsonify({'error': 'Loan ID and Category ID are required'}), 400
        
        # Create or update loan impact record
        loan_impact = LoanImpact.query.filter_by(loan_id=loan_id).first()
        
        # If assessment exists and has a workflow, check if user has permission to update
        if loan_impact and loan_impact.workflow_instance_id:
            workflow_instance = WorkflowInstance.query.get(loan_impact.workflow_instance_id)
            if workflow_instance:
                current_step = WorkflowStep.query.get(workflow_instance.current_step_id)
                
                # Only allow updating if user has the role for the current step or is an admin
                if current_step and current_step.role_id != current_user.role_id and current_user.role_id != 1:
                    current_app.logger.warning(f'User {current_user.id} with role {current_user.role_id} attempted to update assessment in step {current_step.name} (role {current_step.role_id})')
                    return jsonify({
                        'error': 'You do not have permission to update this assessment at its current workflow step',
                        'redirect': url_for('impact_assessment_bp.view_impact_assessment', loan_id=loan_id)
                    }), 403
        if not loan_impact:
            loan_impact = LoanImpact(
                loan_id=loan_id,
                impact_category_id=category_id,
                submitted_by=current_user.id,
                submission_date=datetime.now(),
                verification_status='Pending'
            )
            db.session.add(loan_impact)
        else:
            loan_impact.impact_category_id = category_id
            loan_impact.submitted_by = current_user.id
            loan_impact.submission_date = datetime.now()
            loan_impact.verification_status = 'Pending'
        
        db.session.commit()
        
        # Save metric values
        metrics = ImpactMetric.query.filter_by(impact_category_id=category_id).all()
        for metric in metrics:
            value = data.get(f'metric_{metric.id}')
            if value is not None:
                # Convert value based on data type
                if metric.data_type == 'number':
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0
                elif metric.data_type == 'boolean':
                    value = value.lower() in ['true', 'yes', '1', 'on']
                
                # Create or update impact value
                impact_value = ImpactValue.query.filter_by(
                    loan_impact_id=loan_impact.id,
                    impact_metric_id=metric.id
                ).first()
                
                if not impact_value:
                    impact_value = ImpactValue(
                        loan_impact_id=loan_impact.id,
                        impact_metric_id=metric.id,
                        value=str(value)
                    )
                    db.session.add(impact_value)
                else:
                    impact_value.value = str(value)
        
        # Handle evidence files
        if 'evidence_files' in request.files:
            files = request.files.getlist('evidence_files')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'impact_evidence', filename)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    file.save(file_path)
                    
                    # Create evidence record
                    evidence = ImpactEvidence(
                        loan_impact_id=loan_impact.id,
                        file_path=file_path,
                        file_name=filename,
                        uploaded_by=current_user.id,
                        upload_date=datetime.now()
                    )
                    db.session.add(evidence)
        
        # Create or update workflow instance for this impact assessment
        workflow_def = WorkflowDefinition.query.filter_by(name='Impact Assessment Verification').first()
        
        if workflow_def:
            # Check if there's an existing workflow instance
            if loan_impact.workflow_instance_id:
                # Existing workflow - we could reset it here if needed
                current_app.logger.info(f"Existing workflow instance found for loan impact {loan_impact.id}")
            else:
                # Create new workflow instance
                start_step = WorkflowStep.query.filter_by(workflow_id=workflow_def.id, is_start_step=True).first()
                
                if start_step:
                    # Create workflow instance
                    workflow_instance = WorkflowInstance(
                        workflow_id=workflow_def.id,
                        current_step_id=start_step.id,
                        entity_type='loan_impact',
                        entity_id=loan_impact.id,
                        status='active',
                        created_by=current_user.id
                    )
                    db.session.add(workflow_instance)
                    db.session.commit()
                    
                    # Update loan impact with workflow instance ID
                    loan_impact.workflow_instance_id = workflow_instance.id
                    
                    # Create initial history entry
                    history_entry = WorkflowHistory(
                        instance_id=workflow_instance.id,
                        step_id=start_step.id,
                        action='created',
                        comments='Impact assessment submitted for verification',
                        performed_by=current_user.id
                    )
                    db.session.add(history_entry)
                    db.session.commit()
                    
                    current_app.logger.info(f"Created workflow instance {workflow_instance.id} for loan impact {loan_impact.id}")
        
        return jsonify({'success': True, 'message': 'Impact assessment submitted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting impact assessment: {str(e)}")
        return jsonify({'error': f'Error submitting impact assessment: {str(e)}'}), 500

@impact_assessment_bp.route('/uploads/impact_evidence/<filename>')
@login_required
def get_impact_evidence(filename):
    """Serve impact evidence files"""
    # Construct the path to the file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'impact_evidence', filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        current_app.logger.error(f"Evidence file not found: {file_path}")
        return "File not found", 404
    
    # Determine the file's MIME type
    import mimetypes
    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    # Serve the file
    from flask import send_file
    return send_file(file_path, mimetype=mimetype)

@impact_assessment_bp.route('/user/impact_assessment/history/<int:workflow_instance_id>', methods=['GET'])
@login_required
def get_workflow_history(workflow_instance_id):
    """Get the workflow history for a specific workflow instance"""
    try:
        # Check if the workflow instance exists
        workflow_instance = WorkflowInstance.query.get(workflow_instance_id)
        if not workflow_instance:
            return jsonify({'error': 'Workflow instance not found'}), 404
        
        # Get the workflow history entries for this instance
        history_entries = WorkflowHistory.query.filter_by(instance_id=workflow_instance_id).order_by(WorkflowHistory.performed_at.desc()).all()
        
        history_data = []
        for entry in history_entries:
            # Get step name
            step = WorkflowStep.query.get(entry.step_id)
            
            # Get performer name
            performer = Staff.query.get(entry.performed_by)
            performer_name = f"{performer.first_name} {performer.last_name}" if performer else "Unknown"
            
            # Get action from the entry
            action = entry.action
            
            history_data.append({
                'id': entry.id,
                'step_id': entry.step_id,
                'step_name': step.name if step else 'Unknown',
                'performed_by': entry.performed_by,
                'performer_name': performer_name,
                'performed_at': entry.performed_at.isoformat(),
                'comments': entry.comments,
                'action': action
            })
        
        return jsonify({'history': history_data})
    except Exception as e:
        current_app.logger.error(f"Error retrieving workflow history: {str(e)}")
        return jsonify({'error': f'Error retrieving workflow history: {str(e)}'}), 500

@impact_assessment_bp.route('/user/impact_assessment/transition', methods=['POST'])
@login_required
def transition_workflow():
    # Get form data
    transition_id = request.form.get('transition_id')
    workflow_instance_id = request.form.get('workflow_instance_id')
    loan_id = request.form.get('loan_id')
    comments = request.form.get('comments', '')
    
    if not transition_id or not workflow_instance_id or not loan_id:
        flash('Missing required parameters for workflow transition', 'error')
        return redirect(url_for('impact_assessment.view_impact_assessment', loan_id=loan_id))
    
    try:
        # Get the workflow instance
        workflow_instance = WorkflowInstance.query.get_or_404(workflow_instance_id)
        
        # Get the current step
        current_step = WorkflowStep.query.get(workflow_instance.current_step_id)
        if not current_step:
            flash('Current workflow step not found', 'error')
            return redirect(url_for('impact_assessment_bp.view_impact_assessment', loan_id=loan_id))
        
        # Check if the user has permission to perform this transition
        can_transition = False
        
        # Admin can perform any transition
        if current_user.role_id == 1:
            can_transition = True
            current_app.logger.info(f'Admin user {current_user.id} performing transition {transition_id}')
        # Non-admin can only perform transitions if their role matches the current step's role
        elif current_step.role_id == current_user.role_id:
            can_transition = True
            current_app.logger.info(f'User {current_user.id} with matching role {current_user.role_id} performing transition {transition_id}')
        else:
            current_app.logger.warning(f'User {current_user.id} with role {current_user.role_id} attempted unauthorized transition from step with role {current_step.role_id}')
            flash('You do not have permission to perform this transition at the current workflow step', 'error')
            return redirect(url_for('impact_assessment_bp.view_impact_assessment', loan_id=loan_id))
        
        # Get the transition
        transition = WorkflowTransition.query.get_or_404(transition_id)
        
        # Verify the transition is valid for the current step
        if transition.from_step_id != current_step.id:
            current_app.logger.warning(f'Invalid transition: from_step_id {transition.from_step_id} does not match current_step_id {current_step.id}')
            flash('Invalid transition for the current workflow step', 'error')
            return redirect(url_for('impact_assessment_bp.view_impact_assessment', loan_id=loan_id))
        
        # Get the target step
        target_step = WorkflowStep.query.get_or_404(transition.to_step_id)
        
        # Update the workflow instance
        workflow_instance.current_step_id = target_step.id
        
        # Create a workflow history entry
        history_entry = WorkflowHistory(
            instance_id=workflow_instance.id,
            step_id=target_step.id,
            transition_id=transition.id,
            action=transition.transition_name,
            performed_by=current_user.id,
            comments=comments
        )
        
        # Save changes to database
        db.session.add(history_entry)
        db.session.commit()
        
        flash(f'Successfully moved to {target_step.name} step', 'success')
        # Return to the impact assessment view after successful transition
        return redirect(url_for('impact_assessment_bp.view_impact_assessment', loan_id=loan_id))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error in workflow transition: {str(e)}')
        flash(f'Error processing workflow transition: {str(e)}', 'error')
        # Return to the impact assessment view in case of error
        return redirect(url_for('impact_assessment_bp.view_impact_assessment', loan_id=loan_id))
    except Exception as e:
        current_app.logger.error(f"Error viewing impact assessment: {str(e)}")
        return render_template('error.html', error_message="An error occurred while viewing the impact assessment. Please try again later."), 500

@impact_assessment_bp.route('/admin/impact/verify/<int:loan_impact_id>', methods=['POST'])
@login_required
@admin_required
def verify_impact_assessment(loan_impact_id):
    """Verify an impact assessment"""
    try:
        status = request.form.get('verification_status')
        notes = request.form.get('verification_notes')
        
        if not status:
            return jsonify({'error': 'Verification status is required'}), 400
        
        loan_impact = LoanImpact.query.get(loan_impact_id)
        if not loan_impact:
            return jsonify({'error': 'Impact assessment not found'}), 404
        
        loan_impact.verification_status = status
        loan_impact.verification_notes = notes
        loan_impact.verified_by = current_user.id
        loan_impact.verification_date = datetime.now()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Impact assessment verified successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error verifying impact assessment: {str(e)}")
        return jsonify({'error': f'Error verifying impact assessment: {str(e)}'}), 500
