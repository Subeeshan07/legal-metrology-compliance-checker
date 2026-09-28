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


# ---------------------------------------------------------------------------
# Pre-generate Synthetic Sample Label Images
# ---------------------------------------------------------------------------
def ensure_sample_labels():
    """
    Generates realistic sample product label images with Pillow so judges and users
    can immediately test the compliance scanner with 1-click presets.
    """
    from PIL import ImageDraw, ImageFont
    
    sample_definitions = [
        {
            "filename": "sample_compliant_atta.png",
            "lines": [
                "HIMALAYAN CHAKKI FRESH ATTA",
                "100% Pure Whole Wheat Flour",
                "Net Quantity: 5 kg",
                "MRP Rs. 245.00 (Incl. of all taxes)",
                "Mfg Date: 05/2026",
                "Batch No: HCF-2026-B8",
                "Manufactured by: Pristine Foods & Agro Ltd,",
                "Phase 2, Peenya Industrial Area, Bengaluru - 560058",
                "Consumer Care: care@pristine.com | Ph: 1800-220-4400",
                "Country of Origin: India"
            ],
            "title": "Compliant Label (Whole Wheat Atta)"
        },
        {
            "filename": "sample_non_compliant_chips.png",
            "lines": [
                "CRUNCHY POTATO MASALA CHIPS",
                "Net Qty: 80 g",
                "MRP Rs. 40.00",  # VIOLATION: Missing 'incl of all taxes'
                "Mfg Date: 04/2026",
                "Manufactured by: Surya Snacks LLP, Industrial Zone",
                # VIOLATION: Missing Consumer Care email/phone
                # VIOLATION: Missing Country of Origin
            ],
            "title": "Non-Compliant Label (Missing Tax Clause & Care & Origin)"
        },
        {
            "filename": "sample_needs_review_spice.png",
            "lines": [
                "KASHMIRI DEGI RED CHILLI POWDER",
                "Net Quantity: 200 gms",  # VIOLATION: 'gms' instead of standard 'g'
                "MRP Rs. 145.00 (Incl. of all taxes)",
                "PKD: 06/2026",
                "Mfd by: Kaveri Spices & Naturals, Idukki",  # VIOLATION: Incomplete street address
                "Consumer Care Helpline: 1800-435-8475",    # VIOLATION: Missing email
                "Country of Origin: India"
            ],
            "title": "Needs Review Label (Non-standard Unit & Incomplete Address)"
        }
    ]

    for item in sample_definitions:
        target_path = os.path.join(SAMPLES_FOLDER, item["filename"])
        if not os.path.exists(target_path):
            img = Image.new("RGB", (700, 480), color="#ffffff")
            draw = ImageDraw.Draw(img)
            
            # Header banner
            draw.rectangle([(0, 0), (700, 50)], fill="#0f172a")
            draw.text((20, 16), "LEGAL METROLOGY PACKAGING LABEL SAMPLE", fill="#38bdf8")
            
            # Draw lines
            y = 70
            for i, line in enumerate(item["lines"]):
                if i == 0:
                    draw.text((30, y), line, fill="#0f172a")
                    y += 35
                elif "MRP" in line or "Net" in line:
                    draw.text((30, y), line, fill="#1e293b")
                    y += 32
                else:
                    draw.text((30, y), line, fill="#334155")
                    y += 30
                    
            # Footer border
            draw.rectangle([(10, 10), (690, 470)], outline="#cbd5e1", width=2)
            img.save(target_path, format="PNG")


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
