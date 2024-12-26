from flask import Blueprint, render_template, request, jsonify
from models.threshold import Threshold
from extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
thresholds_bp = Blueprint('thresholds', __name__)

@thresholds_bp.route('/admin/thresholds', methods=['GET'])
def list_thresholds():
    logger.info("Fetching thresholds list")
    try:
        thresholds = db.session.query(Threshold).filter(
            Threshold.is_active == True
        ).order_by(Threshold.valid_from.desc()).all()
        
        return render_template(
            'admin/thresholds/list.html',
            thresholds=[t.to_dict() for t in thresholds]
        )
    except Exception as e:
        logger.error(f"Error fetching thresholds: {str(e)}", exc_info=True)
        raise

@thresholds_bp.route('/admin/thresholds/create', methods=['POST'])
def create_threshold():
    logger.info("Creating new threshold")
    try:
        data = request.form
        
        # Parse and validate the data
        try:
            npl_ratio = float(data.get('npl_ratio'))
            coverage_ratio = float(data.get('coverage_ratio'))
            par_ratio = float(data.get('par_ratio'))
            cost_of_risk = float(data.get('cost_of_risk'))
            recovery_rate = float(data.get('recovery_rate'))
            valid_from = datetime.fromisoformat(data.get('valid_from'))
            valid_to = datetime.fromisoformat(data.get('valid_to')) if data.get('valid_to') else None
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid data in threshold creation: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid data format'
            }), 400

        # Validate ranges
        if not (0 <= npl_ratio <= 100 and 
                0 <= coverage_ratio <= 100 and 
                0 <= par_ratio <= 100 and 
                0 <= cost_of_risk <= 100 and 
                0 <= recovery_rate <= 100):
            return jsonify({
                'success': False,
                'message': 'All ratios must be between 0 and 100'
            }), 400

        # Create new threshold
        threshold = Threshold(
            npl_ratio=npl_ratio,
            coverage_ratio=coverage_ratio,
            par_ratio=par_ratio,
            cost_of_risk=cost_of_risk,
            recovery_rate=recovery_rate,
            valid_from=valid_from,
            valid_to=valid_to
        )
        
        db.session.add(threshold)
        db.session.commit()
        logger.info(f"Successfully created threshold valid from {valid_from}")
        
        return jsonify({
            'success': True,
            'message': 'Threshold created successfully',
            'threshold': threshold.to_dict()
        })
    except ValueError as e:
        db.session.rollback()
        logger.error(f"Validation error in threshold creation: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating threshold: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An error occurred while creating the threshold'
        }), 500

@thresholds_bp.route('/admin/thresholds/edit/<int:threshold_id>', methods=['POST'])
def edit_threshold(threshold_id):
    logger.info(f"Attempting to edit threshold with ID: {threshold_id}")
    try:
        threshold = db.session.query(Threshold).filter(
            Threshold.id == threshold_id,
            Threshold.is_active == True
        ).first()
        
        if not threshold:
            logger.warning(f"Threshold not found with ID: {threshold_id}")
            return jsonify({
                'success': False,
                'message': 'Threshold not found'
            }), 404

        data = request.form
        
        # Parse and validate the data
        try:
            npl_ratio = float(data.get('npl_ratio'))
            coverage_ratio = float(data.get('coverage_ratio'))
            par_ratio = float(data.get('par_ratio'))
            cost_of_risk = float(data.get('cost_of_risk'))
            recovery_rate = float(data.get('recovery_rate'))
            valid_from = datetime.fromisoformat(data.get('valid_from'))
            valid_to = datetime.fromisoformat(data.get('valid_to')) if data.get('valid_to') else None
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid data in threshold edit: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid data format'
            }), 400

        # Validate ranges
        if not (0 <= npl_ratio <= 100 and 
                0 <= coverage_ratio <= 100 and 
                0 <= par_ratio <= 100 and 
                0 <= cost_of_risk <= 100 and 
                0 <= recovery_rate <= 100):
            return jsonify({
                'success': False,
                'message': 'All ratios must be between 0 and 100'
            }), 400

        # Update threshold
        threshold.npl_ratio = npl_ratio
        threshold.coverage_ratio = coverage_ratio
        threshold.par_ratio = par_ratio
        threshold.cost_of_risk = cost_of_risk
        threshold.recovery_rate = recovery_rate
        threshold.valid_from = valid_from
        threshold.valid_to = valid_to
        
        db.session.commit()
        logger.info(f"Successfully updated threshold with ID: {threshold_id}")
        
        return jsonify({
            'success': True,
            'message': 'Threshold updated successfully',
            'threshold': threshold.to_dict()
        })
    except ValueError as e:
        db.session.rollback()
        logger.error(f"Validation error in threshold update: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating threshold: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An error occurred while updating the threshold'
        }), 500

@thresholds_bp.route('/admin/thresholds/delete/<int:threshold_id>', methods=['DELETE'])
def delete_threshold(threshold_id):
    logger.info(f"Attempting to delete threshold with ID: {threshold_id}")
    try:
        threshold = db.session.query(Threshold).filter(
            Threshold.id == threshold_id,
            Threshold.is_active == True
        ).first()
        
        if not threshold:
            logger.warning(f"Threshold not found with ID: {threshold_id}")
            return jsonify({
                'success': False,
                'message': 'Threshold not found'
            }), 404

        # Soft delete
        threshold.is_active = False
        db.session.commit()
        logger.info(f"Successfully deleted threshold with ID: {threshold_id}")
        
        return jsonify({
            'success': True,
            'message': 'Threshold deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting threshold: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An error occurred while deleting the threshold'
        }), 500
