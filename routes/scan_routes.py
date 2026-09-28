"""
Scan and evaluation API routes for label OCR, compliance checking, and saving records.
"""

import os
import uuid
from datetime import datetime
from flask import Blueprint, current_app, jsonify, request
from services.ocr_service import check_tesseract_available, perform_ocr_on_image
from services.extraction_service import extract_entities_from_text
from services.compliance_service import LegalMetrologyComplianceEngine
from repositories.product_repository import save_record_to_dataset
from utils.file_utils import allowed_file

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/api/scan", methods=["POST"])
def scan_product():
    """
    Scans a product label image or sample text:
    1. Preprocesses image
    2. Runs Tesseract OCR (with intelligent fallback if host lacks binary)
    3. Extracts packaged commodity entities
    4. Evaluates against Legal Metrology Rules, 2011
    """
    sample_id = request.form.get("sample_id")
    raw_manual_text = request.form.get("manual_text", "").strip()
    image_url = None
    extracted_text = ""
    ocr_source = ""

    # Check if a preset sample was requested
    if sample_id:
        sample_map = {
            "compliant": {
                "file": "sample_compliant_atta.png",
                "text": (
                    "HIMALAYAN CHAKKI FRESH ATTA\n"
                    "100% Pure Whole Wheat Flour\n"
                    "Net Quantity: 5 kg\n"
                    "MRP Rs. 245.00 (Incl. of all taxes)\n"
                    "Mfg Date: 05/2026\n"
                    "Batch No: HCF-2026-B8\n"
                    "Manufactured by: Pristine Foods & Agro Ltd,\n"
                    "Phase 2, Peenya Industrial Area, Bengaluru - 560058\n"
                    "Consumer Care: care@pristine.com | Ph: 1800-220-4400\n"
                    "Country of Origin: India"
                )
            },
            "non_compliant": {
                "file": "sample_non_compliant_chips.png",
                "text": (
                    "CRUNCHY POTATO MASALA CHIPS\n"
                    "Net Qty: 80 g\n"
                    "MRP Rs. 40.00\n"
                    "Mfg Date: 04/2026\n"
                    "Manufactured by: Surya Snacks LLP, Industrial Zone"
                )
            },
            "needs_review": {
                "file": "sample_needs_review_spice.png",
                "text": (
                    "KASHMIRI DEGI RED CHILLI POWDER\n"
                    "Net Quantity: 200 gms\n"
                    "MRP Rs. 145.00 (Incl. of all taxes)\n"
                    "PKD: 06/2026\n"
                    "Mfd by: Kaveri Spices & Naturals, Idukki\n"
                    "Consumer Care Helpline: 1800-435-8475\n"
                    "Country of Origin: India"
                )
            }
        }
        if sample_id in sample_map:
            sample_data = sample_map[sample_id]
            extracted_text = sample_data["text"]
            image_url = f"/static/samples/{sample_data['file']}"
            ocr_source = "Pre-loaded Reference Package Sample"

    # Check if a file was uploaded
    elif "label_image" in request.files:
        file = request.files["label_image"]
        if file and file.filename != "" and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            safe_name = f"scan_{uuid.uuid4().hex[:10]}.{ext}"
            upload_folder = current_app.config.get("UPLOAD_FOLDER")
            file_path = os.path.join(upload_folder, safe_name)
            file.save(file_path)
            image_url = f"/uploads/{safe_name}"

            if check_tesseract_available():
                extracted_text, ocr_source = perform_ocr_on_image(file_path)
            else:
                ocr_source = "Tesseract binary not installed on host machine"
                extracted_text = raw_manual_text or (
                    "Note: Tesseract OCR is not installed in the local environment.\n"
                    "Please enter or adjust the label declarations in the text box below,\n"
                    "or click one of the 'Quick Test Presets' above."
                )

    # Manual text input fallback
    elif raw_manual_text:
        extracted_text = raw_manual_text
        ocr_source = "Manual Text Entry / Verification"

    else:
        return jsonify({"error": "No image file or sample selected."}), 400

    # Extract declared entities
    entities = extract_entities_from_text(extracted_text)

    # Run compliance rules evaluation
    compliance_result = LegalMetrologyComplianceEngine.evaluate(entities)

    return jsonify({
        "success": True,
        "image_url": image_url,
        "ocr_text": extracted_text,
        "ocr_source": ocr_source,
        "tesseract_available": check_tesseract_available(),
        "extracted_entities": entities,
        "compliance": compliance_result
    })


@scan_bp.route("/api/save", methods=["POST"])
def save_product():
    """
    Appends scanned product to history / CSV dataset
    """
    data = request.json or {}
    new_id = f"LMC-{int(datetime.now().timestamp() % 100000):05d}"

    record = {
        "id": new_id,
        "product_name": data.get("product_name", "Unlabeled Product"),
        "category": data.get("category", "Packaged Food"),
        "manufacturer": data.get("manufacturer", "Not Declared"),
        "net_quantity": data.get("net_quantity", "Not Declared"),
        "mrp": data.get("mrp", "Not Declared"),
        "mfg_date": data.get("mfg_date", "Not Declared"),
        "consumer_care": data.get("consumer_care", "Not Declared"),
        "country_of_origin": data.get("country_of_origin", "Not Declared"),
        "compliance_status": data.get("compliance_status", "NEEDS REVIEW"),
        "violations": data.get("violations", "None"),
        "scanned_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ocr_confidence": data.get("ocr_confidence", "95%")
    }

    success = save_record_to_dataset(record)
    return jsonify({"success": success, "record": record})
