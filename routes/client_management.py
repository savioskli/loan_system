from flask import Blueprint, render_template
from flask_login import login_required

client_management_bp = Blueprint('client_management', __name__)

@client_management_bp.route('/admin/client-management')
@login_required
def index():
    return render_template('admin/clients/index.html')
