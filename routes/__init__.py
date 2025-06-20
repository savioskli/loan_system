from .client_types import client_types_bp
from .products import products_bp
from .api import api_bp
from .branch_routes import branch_bp
from .system_references import bp as system_references_bp


def init_app(app):
    """Initialize routes."""
    app.register_blueprint(client_types_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(branch_bp, url_prefix='/admin')
    app.register_blueprint(system_references_bp)
