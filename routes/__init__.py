"""
Application routes package.
"""

from routes.web_routes import web_bp
from routes.scan_routes import scan_bp
from routes.product_routes import product_bp
from routes.analytics_routes import analytics_bp
from routes.rules_routes import rules_bp

__all__ = [
    "web_bp",
    "scan_bp",
    "product_bp",
    "analytics_bp",
    "rules_bp",
]
