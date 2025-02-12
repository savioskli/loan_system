from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.post_disbursement_modules import PostDisbursementModule
from models.post_disbursement_modules import ExpectedStructure
from flask_login import login_required
from utils.decorators import admin_required
from models.core_banking import CoreBankingSystem 
from extensions import db
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define the blueprint
post_disbursement_modules_bp = Blueprint('post_disbursement_modules', __name__)

@post_disbursement_modules_bp.route('/admin/modules', methods=['GET'])
@login_required
@admin_required
def list_modules():
    """Render the module management page with expected structures"""
    logger.info("Fetching modules list with expected structures")
    try:
        # Fetch all modules and sort them by order
        all_modules = PostDisbursementModule.query.order_by(PostDisbursementModule.order).all()

        # Create a dictionary to store modules by their parent_id
        modules_by_parent = {}
        for module in all_modules:
            if module.parent_id not in modules_by_parent:
                modules_by_parent[module.parent_id] = []
            modules_by_parent[module.parent_id].append(module)

        # Recursive function to build the hierarchical structure
        def build_hierarchy(parent_id):
            if parent_id not in modules_by_parent:
                return []
            hierarchy = []
            for module in modules_by_parent[parent_id]:
                # Fetch expected structures for the module
                expected_structures = ExpectedStructure.query.filter_by(module_id=module.id).all()
                hierarchy.append({
                    'module': module,
                    'expected_structures': expected_structures,
                    'children': build_hierarchy(module.id)
                })
            return hierarchy

        # Build the hierarchical structure starting from the root (parent_id is None)
        hierarchical_modules = build_hierarchy(None)

        # Fetch parent modules for the dropdown
        parent_modules = PostDisbursementModule.query.filter_by(parent_id=None).order_by(PostDisbursementModule.order).all()

        logger.info(f"Successfully retrieved {len(all_modules)} modules with expected structures")
        return render_template('admin/post_disbursement_modules/modules.html', hierarchical_modules=hierarchical_modules, parent_modules=parent_modules)
    except Exception as e:
        logger.error(f"Error fetching modules: {str(e)}", exc_info=True)
        raise


@post_disbursement_modules_bp.route('/admin/modules/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_module():
    """Create a new module"""
    logger.info("Creating a new module")
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        url = request.form.get('url')  # New URL field
        parent_id = request.form.get('parent_id', None)

        # Convert empty string to None
        if parent_id == '':
            parent_id = None
        elif parent_id is not None:
            try:
                parent_id = int(parent_id)  # Ensure parent_id is an integer
            except (ValueError, TypeError):
                # If conversion fails, log the error and set parent_id to None
                logger.error(f"Invalid parent_id value: {parent_id}. Setting to None.")
                parent_id = None

        try:
            new_module = PostDisbursementModule(
                name=name,
                description=description,
                url=url,
                parent_id=parent_id
            )
            db.session.add(new_module)
            db.session.commit()

            flash('Module created successfully!', 'success')
            logger.info(f"Successfully created module with ID: {new_module.id}")
            return redirect(url_for('post_disbursement_modules.list_modules'))

        except Exception as e:
            logger.error(f"Error creating module: {str(e)}", exc_info=True)
            db.session.rollback()
            flash('Failed to create module. Please try again.', 'error')

    return render_template('admin/post_disbursement_modules/create_module.html')

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_module(module_id):
    """Edit an existing module"""
    logger.info(f"Editing module with ID: {module_id}")
    module = PostDisbursementModule.query.get_or_404(module_id)

    if request.method == 'POST':
        module.name = request.form.get('name')
        module.description = request.form.get('description')
        module.url = request.form.get('url')
        parent_id = request.form.get('parent_id', None)

        if parent_id == '':
            module.parent_id = None
        else:
            try:
                module.parent_id = int(parent_id)
            except (ValueError, TypeError):
                logger.error(f"Invalid parent_id value: {parent_id}. Setting to None.")
                module.parent_id = None

        try:
            db.session.commit()
            flash('Module updated successfully!', 'success')
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error updating module: {str(e)}", exc_info=True)
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Failed to update module. Please try again.'}), 500

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return module data as JSON for AJAX requests
        return jsonify({
            'id': module.id,
            'name': module.name,
            'description': module.description,
            'url': module.url,
            'parent_id': module.parent_id
        })

    parent_modules = PostDisbursementModule.query.filter_by(parent_id=None).all()
    return render_template('admin/post_disbursement_modules/edit_module.html', module=module, parent_modules=parent_modules)

@post_disbursement_modules_bp.route('/admin/modules/reorder', methods=['POST'])
@login_required
@admin_required
def reorder_modules():
    """Reorder modules based on the provided order"""
    try:
        data = request.get_json()
        if not data or 'order' not in data:
            return jsonify({'success': False, 'message': 'Invalid data'}), 400

        order = data['order']
        
        # Update each module's order
        for index, item in enumerate(order):
            module_id = int(item['id'])  # Extract ID from the object
            module = PostDisbursementModule.query.get(module_id)
            
            if not module:
                return jsonify({
                    'success': False, 
                    'message': f'Module {module_id} not found'
                }), 404
                
            module.order = index
            
            # Update parent if needed
            if 'parent_id' in item:
                parent_id = item['parent_id']
                module.parent_id = int(parent_id) if parent_id else None

        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error reordering modules: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 500

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/toggle_hide', methods=['POST'])
@login_required
@admin_required
def toggle_hide_module(module_id):
    """Toggle hide/unhide for a module"""
    logger.info(f"Toggling hide status for module with ID: {module_id}")
    module = PostDisbursementModule.query.get_or_404(module_id)
    module.hidden = not module.hidden

    try:
        db.session.commit()
        return jsonify({'success': True, 'hidden': module.hidden})
    except Exception as e:
        logger.error(f"Error toggling hide status: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False}), 500


@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/manage', methods=['GET'])
@login_required
@admin_required
def manage_fields(module_id):
    """Manage fields for a specific module"""
    logger.info(f"Managing fields for module with ID: {module_id}")
    try:
        module = PostDisbursementModule.query.get_or_404(module_id)
        return render_template('admin/post_disbursement_modules/manage_fields.html', module=module)
    except Exception as e:
        logger.error(f"Error managing fields for module: {str(e)}", exc_info=True)
        raise

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_module(module_id):
    """Delete a module"""
    logger.info(f"Attempting to delete module with ID: {module_id}")
    try:
        module = PostDisbursementModule.query.get_or_404(module_id)
        db.session.delete(module)
        db.session.commit()

        logger.info(f"Successfully deleted module with ID: {module_id}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error deleting module: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False}), 500

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/tables', methods=['POST'])
@login_required
@admin_required
def manage_tables(module_id):
    """Manage tables for a specific module"""
    logger.info(f"Managing tables for module with ID: {module_id}")
    try:
        # Ensure the request contains JSON data
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Request must be JSON'}), 415

        data = request.get_json()
        selected_tables = data.get('tables', [])

        # Remove duplicates from selected_tables
        selected_tables = list(set(selected_tables))

        # Fetch the module
        module = PostDisbursementModule.query.get_or_404(module_id)

        # Update the selected_tables field
        module.selected_tables = selected_tables
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error managing tables: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while managing tables.'}), 500

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/available-tables', methods=['GET'])
@login_required
@admin_required
def fetch_available_tables(module_id):
    """Fetch available tables from the core banking system"""
    logger.info(f"Fetching available tables for module with ID: {module_id}")
    try:
        # Fetch the active core banking system
        core_banking_system = CoreBankingSystem.query.filter_by(is_active=True).first()
        if not core_banking_system:
            return jsonify({'success': False, 'message': 'No active core banking system found.'}), 404

        # Fetch the list of tables
        tables = core_banking_system.list_tables()
        return jsonify({'tables': tables})

    except Exception as e:
        logger.error(f"Error fetching available tables: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'An error occurred while fetching available tables.'}), 500

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/tables/remove', methods=['POST'])
@login_required
@admin_required
def remove_selected_table(module_id):
    """Remove a selected table from a module"""
    logger.info(f"Removing selected table from module with ID: {module_id}")
    try:
        module = PostDisbursementModule.query.get_or_404(module_id)
        data = request.get_json()
        table_name = data.get('table')

        # Ensure selected_tables is a list
        if isinstance(module.selected_tables, list):
            if table_name in module.selected_tables:
                module.selected_tables.remove(table_name)
                db.session.commit()
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': 'Table not found in selected tables.'}), 404
        else:
            return jsonify({'success': False, 'message': 'Selected tables are not in the correct format.'}), 500

    except Exception as e:
        logger.error(f"Error removing selected table: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while removing the selected table.'}), 500

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/expected-structure', methods=['POST'])
@login_required
@admin_required
def save_expected_structure(module_id):
    """Save the expected structure for a specific module"""
    logger.info(f"Saving expected structure for module with ID: {module_id}")
    try:
        # Ensure the request contains form data
        if not request.form:
            return jsonify({'success': False, 'message': 'Request must contain form data'}), 400

        table_name = request.form.get('table_name')
        columns = request.form.get('columns')

        if not table_name or not columns:
            return jsonify({'success': False, 'message': 'Table name and columns are required'}), 400

        # Convert columns from a string to a list
        columns_list = [col.strip() for col in columns.split(',')]

        # Create a new ExpectedStructure entry
        expected_structure = ExpectedStructure(
            module_id=module_id,
            table_name=table_name,
            columns=columns_list
        )

        db.session.add(expected_structure)
        db.session.commit()

        flash('Expected structure saved successfully!', 'success')
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error saving expected structure: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while saving the expected structure.'}), 500

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/expected-structure/<int:structure_id>', methods=['POST'])
@login_required
@admin_required
def edit_expected_structure(module_id, structure_id):
    """Edit the expected structure for a specific module"""
    logger.info(f"Editing expected structure with ID: {structure_id} for module with ID: {module_id}")
    try:
        # Ensure the request contains form data
        if not request.form:
            return jsonify({'success': False, 'message': 'Request must contain form data'}), 400

        table_name = request.form.get('table_name')
        columns = request.form.get('columns')

        if not table_name or not columns:
            return jsonify({'success': False, 'message': 'Table name and columns are required'}), 400

        # Convert columns from a string to a list
        columns_list = [col.strip() for col in columns.split(',')]

        # Fetch the expected structure
        expected_structure = ExpectedStructure.query.get_or_404(structure_id)

        # Update the expected structure
        expected_structure.table_name = table_name
        expected_structure.columns = columns_list

        db.session.commit()
        flash('Expected structure updated successfully!', 'success')
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error editing expected structure: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while editing the expected structure.'}), 500

@post_disbursement_modules_bp.route('/admin/modules/<int:module_id>/expected-structure/<int:structure_id>/fetch', methods=['GET'])
@login_required
@admin_required
def fetch_expected_structure(module_id, structure_id):
    """Fetch the expected structure for a specific module"""
    logger.info(f"Fetching expected structure with ID: {structure_id} for module with ID: {module_id}")
    try:
        # Fetch the expected structure
        expected_structure = ExpectedStructure.query.get_or_404(structure_id)

        # Return the expected structure data as JSON
        return jsonify({
            'success': True,
            'table_name': expected_structure.table_name,
            'columns': expected_structure.columns
        })

    except Exception as e:
        logger.error(f"Error fetching expected structure: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'An error occurred while fetching the expected structure.'}), 500



    




        
