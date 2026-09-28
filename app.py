"""
Legal Metrology Packaged Commodity Compliance Checker
Backend Server (Flask)

Author: Advanced Agentic AI Assistant
Purpose: Analyze packaged food product labels and verify mandatory declarations
         under the Legal Metrology (Packaged Commodities) Rules, 2011 (India).
"""

import os
import logging
from PIL import Image
from flask import Flask
from config.settings import Config
from utils.file_utils import ALLOWED_IMAGE_EXTENSIONS
from repositories.product_repository import (
    load_dataset,
    save_record_to_dataset,
)
from services.ocr_service import check_tesseract_available
from routes import (
    web_bp,
    scan_bp,
    product_bp,
    analytics_bp,
    rules_bp,
)


# ---------------------------------------------------------------------------
# Setup & Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Keep these module-level names during the refactor because the existing
# application still references them in dataset, sample, and upload operations.
DATASET_PATH = Config.DATASET_PATH
UPLOAD_FOLDER = Config.UPLOAD_FOLDER
SAMPLES_FOLDER = Config.SAMPLES_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAMPLES_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config.from_object(Config)

ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS

# ---------------------------------------------------------------------------
# Tesseract OCR Detection & Initialization
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# OCR & Entity Extraction Engine
# ---------------------------------------------------------------------------


from services.sample_service import ensure_sample_labels


# Call generator at startup
try:
    ensure_sample_labels()
except Exception as e:
    logger.warning(f"Could not pre-render sample images: {e}")


from routes import (
    web_bp,
    scan_bp,
    product_bp,
    analytics_bp,
    rules_bp,
)

app.register_blueprint(web_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(product_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(rules_bp)



# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting Legal Metrology Packaged Commodity Compliance Checker on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
