from flask import Blueprint

branches_bp = Blueprint('branches', __name__)

@branches_bp.route('/admin/branches')
def manage_branches():
    return "Branches management page"
