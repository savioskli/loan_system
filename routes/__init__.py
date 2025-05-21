from .client_types import client_types_bp
from .products import products_bp
from .api import api_bp
from .user import user_bp
from .branch_routes import branch_bp


def init_app(app):
    """Initialize routes."""
    app.register_blueprint(client_types_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(branch_bp, url_prefix='/admin')
