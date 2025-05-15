from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from models.impact import ImpactCategory, ImpactMetric
from models.loan_impact import LoanImpact, ImpactValue, ImpactEvidence
from models.staff import Staff
from models.core_banking import CoreBankingSystem
from models.post_disbursement_modules import ExpectedStructure, ActualStructure, PostDisbursementModule
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
            
            # Add impact assessment status to each loan
            for loan in loans:
                loan_impact = LoanImpact.query.filter_by(loan_id=loan['LoanID']).first()
                if loan_impact:
                    loan['has_impact'] = True
                    loan['impact_status'] = loan_impact.verification_status
                else:
                    loan['has_impact'] = False
                    loan['impact_status'] = 'Not Submitted'
            
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
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Impact assessment submitted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting impact assessment: {str(e)}")
        return jsonify({'error': f'Error submitting impact assessment: {str(e)}'}), 500

@impact_assessment_bp.route('/user/impact_assessment/view/<int:loan_id>', methods=['GET'])
@login_required
def view_impact_assessment(loan_id):
    """View impact assessment for a specific loan"""
    # Get the loan impact record
    loan_impact = LoanImpact.query.filter_by(loan_id=loan_id).first_or_404()
    
    # Get the impact category
    category = ImpactCategory.query.get(loan_impact.impact_category_id)
    
    # Get the metrics for this category
    metrics = ImpactMetric.query.filter_by(impact_category_id=category.id).all()
    
    # Get the impact values for this loan impact
    impact_values = ImpactValue.query.filter_by(loan_impact_id=loan_impact.id).all()
    
    # Create a dictionary of metric values for easy access
    metric_values = {}
    for value in impact_values:
        metric_values[value.impact_metric_id] = value.value
    
    # Get the evidence files
    evidence_files = ImpactEvidence.query.filter_by(loan_impact_id=loan_impact.id).all()
    
    # Get the staff who submitted and verified
    submitted_by = Staff.query.get(loan_impact.submitted_by)
    verified_by = None
    if loan_impact.verified_by:
        verified_by = Staff.query.get(loan_impact.verified_by)
    
    # Get visible modules for sidebar
    visible_modules = PostDisbursementModule.query.filter_by(hidden=False).order_by(PostDisbursementModule.order).all()
    
    return render_template('user/impact/view_assessment.html',
                           loan_id=loan_id,
                           loan_impact=loan_impact,
                           category=category,
                           metrics=metrics,
                           metric_values=metric_values,
                           evidence_files=evidence_files,
                           submitted_by=submitted_by,
                           verified_by=verified_by,
                           visible_modules=visible_modules)

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
