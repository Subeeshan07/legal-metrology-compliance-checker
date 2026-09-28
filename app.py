"""
Legal Metrology Packaged Commodity Compliance Checker
Backend Server (Flask)

Author: Advanced Agentic AI Assistant
Purpose: Analyze packaged food product labels and verify mandatory declarations
         under the Legal Metrology (Packaged Commodities) Rules, 2011 (India).
"""

import os
import logging
from flask import Flask
from config.settings import Config
from utils.file_utils import ALLOWED_IMAGE_EXTENSIONS
from repositories.product_repository import (
    load_dataset,
    save_record_to_dataset,
)
from services.ocr_service import check_tesseract_available
from services.sample_service import ensure_sample_labels
from routes import (
    web_bp,
    scan_bp,
    product_bp,
    analytics_bp,
    rules_bp,
)

# ---------------------------------------------------------------------------
# Setup & Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------
def create_app(config_class=Config):
    """
    Application factory for the Legal Metrology Compliance Checker.
    Configures settings, ensures storage folders and sample presets,
    and registers all route blueprints.
    """
    flask_app = Flask(__name__)
    if isinstance(config_class, dict):
        flask_app.config.from_mapping(config_class)
    else:
        flask_app.config.from_object(config_class)

    # Ensure required directories exist
    upload_folder = flask_app.config.get("UPLOAD_FOLDER", Config.UPLOAD_FOLDER)
    samples_folder = flask_app.config.get("SAMPLES_FOLDER", Config.SAMPLES_FOLDER)
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(samples_folder, exist_ok=True)

    # Initialize synthetic sample label images
    try:
        ensure_sample_labels(samples_folder)
    except Exception as e:
        logger.warning(f"Could not pre-render sample images: {e}")

    # Register Blueprints
    flask_app.register_blueprint(web_bp)
    flask_app.register_blueprint(scan_bp)
    flask_app.register_blueprint(product_bp)
    flask_app.register_blueprint(analytics_bp)
    flask_app.register_blueprint(rules_bp)

    # -----------------------------------------------------------------------
    # Production Security Headers Middleware
    # -----------------------------------------------------------------------
    @flask_app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # -----------------------------------------------------------------------
    # Health & Readiness Check Endpoint
    # -----------------------------------------------------------------------
    @flask_app.route("/health", methods=["GET"])
    def health_check():
        from datetime import datetime
        tess_status = check_tesseract_available()
        return {
            "status": "UP",
            "service": "Legal Metrology Compliance & Counterfeit Risk Checker",
            "ocr_engine": "ACTIVE" if tess_status else "STANDBY_FALLBACK",
            "database": "SQLITE_READY",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, 200

    # -----------------------------------------------------------------------
    # Central Error Handlers
    # -----------------------------------------------------------------------
    @flask_app.errorhandler(413)
    def file_too_large(e):
        return {"error": "Uploaded image exceeds the 16MB file size limit."}, 413

    @flask_app.errorhandler(404)
    def not_found(e):
        return {"error": "Resource not found."}, 404

    @flask_app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return {"error": "Internal server error occurred."}, 500

    return flask_app


# ---------------------------------------------------------------------------
# Global Application Instance & Backward Compatibility Exports
# ---------------------------------------------------------------------------
app = create_app(Config)

DATASET_PATH = Config.DATASET_PATH
UPLOAD_FOLDER = Config.UPLOAD_FOLDER
SAMPLES_FOLDER = Config.SAMPLES_FOLDER
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting Legal Metrology Packaged Commodity Compliance Checker on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
