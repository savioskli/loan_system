from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from utils.decorators import admin_required
from models.impact import ImpactCategory
from extensions import db
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define the blueprint
impact_bp = Blueprint('impact', __name__)

@impact_bp.route('/admin/impact/categories', methods=['GET'])
@login_required
@admin_required
def list_categories():
    """List all impact categories"""
    try:
        categories = ImpactCategory.query.order_by(ImpactCategory.name).all()
        return render_template('admin/impact/categories.html', categories=categories)
    except Exception as e:
        logger.error(f"Error fetching impact categories: {str(e)}", exc_info=True)
        flash('An error occurred while fetching impact categories.', 'error')
        return redirect(url_for('admin.dashboard'))

@impact_bp.route('/admin/impact/categories/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_category():
    """Create a new impact category"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        active = True if request.form.get('active') else False
        
        try:
            category = ImpactCategory(
                name=name,
                description=description,
                active=active
            )
            db.session.add(category)
            db.session.commit()
            flash('Impact category created successfully!', 'success')
            return redirect(url_for('impact.list_categories'))
        except Exception as e:
            logger.error(f"Error creating impact category: {str(e)}", exc_info=True)
            db.session.rollback()
            flash('An error occurred while creating the impact category.', 'error')
    
    return render_template('admin/impact/create_category.html')

@impact_bp.route('/admin/impact/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """Edit an existing impact category"""
    category = ImpactCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        category.active = True if request.form.get('active') else False
        
        try:
            db.session.commit()
            flash('Impact category updated successfully!', 'success')
            return redirect(url_for('impact.list_categories'))
        except Exception as e:
            logger.error(f"Error updating impact category: {str(e)}", exc_info=True)
            db.session.rollback()
            flash('An error occurred while updating the impact category.', 'error')
    
    return render_template('admin/impact/edit_category.html', category=category)

@impact_bp.route('/admin/impact/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """Delete an impact category"""
    category = ImpactCategory.query.get_or_404(category_id)
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Impact category deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting impact category: {str(e)}", exc_info=True)
        db.session.rollback()
        flash('An error occurred while deleting the impact category.', 'error')
    
    return redirect(url_for('impact.list_categories'))

@impact_bp.route('/admin/impact/categories/<int:category_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_active(category_id):
    """Toggle active status for an impact category"""
    category = ImpactCategory.query.get_or_404(category_id)
    category.active = not category.active
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'active': category.active})
    except Exception as e:
        logger.error(f"Error toggling active status: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False}), 500
