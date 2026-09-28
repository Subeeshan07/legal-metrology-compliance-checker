"""
Scan and evaluation API routes for label OCR, compliance checking, and saving records.
"""

import os
import uuid
from datetime import datetime
from flask import Blueprint, current_app, jsonify, request
from services.ocr_service import check_tesseract_available
from services.analysis_orchestrator import AnalysisOrchestrator
from repositories.product_repository import save_record_to_dataset
from repositories.database_repository import db_repository
from utils.file_utils import allowed_file

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/api/scan", methods=["POST"])
def scan_product():
    """
    Unified multi-stage scan pipeline:
    1. Image Quality Assessment
    2. OCR Processing & Confidence
    3. Mandatory Entity Extraction & Normalization
    4. Legal Metrology Compliance Checking (Rule 6 & Rule 13)
    5. Food Counterfeit Risk Detection
    """
    sample_id = request.form.get("sample_id")
    raw_manual_text = request.form.get("manual_text", "").strip()
    barcode_input = request.form.get("barcode", "").strip() or None
    image_url = None
    file_path = None
    manual_text = None

    # Check preset sample
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
                    "Country of Origin: India\n"
                    "Barcode: 8901234567890"
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
            manual_text = sample_data["text"]
            image_url = f"/static/samples/{sample_data['file']}"
            sample_dir = current_app.config.get("SAMPLES_FOLDER")
            if sample_dir:
                file_path = os.path.join(sample_dir, sample_data["file"])

    # Check uploaded file
    elif "label_image" in request.files:
        file = request.files["label_image"]
        if file and file.filename != "" and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            safe_name = f"scan_{uuid.uuid4().hex[:10]}.{ext}"
            upload_folder = current_app.config.get("UPLOAD_FOLDER")
            file_path = os.path.join(upload_folder, safe_name)
            file.save(file_path)
            image_url = f"/uploads/{safe_name}"

            if not check_tesseract_available():
                manual_text = raw_manual_text or (
                    "Note: Tesseract OCR is not installed in the local environment.\n"
                    "Please enter or adjust the label declarations in the text box below,\n"
                    "or click one of the 'Quick Test Presets' above."
                )

    elif raw_manual_text:
        manual_text = raw_manual_text

    else:
        return jsonify({"error": "No image file or sample selected."}), 400

    # Run unified analysis orchestrator
    analysis = AnalysisOrchestrator.analyze_scan(
        image_path=file_path,
        manual_text=manual_text,
        barcode=barcode_input,
    )

    # Save scan audit record into SQLite
    scan_audit_id = f"SCAN-{uuid.uuid4().hex[:8].upper()}"
    try:
        db_repository.save_scan_audit({
            "scan_id": scan_audit_id,
            "product_id": analysis.get("unified_report", {}).get("product_identity", {}).get("identified_brand", "Unknown"),
            "image_url": image_url,
            "ocr_text": analysis.get("ocr_text", ""),
            "ocr_confidence": str(analysis.get("ocr_confidence", "N/A")),
            "compliance_status": analysis.get("compliance", {}).get("overall_status", "NEEDS REVIEW"),
            "counterfeit_risk": analysis.get("counterfeit_risk", {}).get("risk_level", "LOW"),
            "risk_score": float(analysis.get("counterfeit_risk", {}).get("risk_score", 0.0)),
            "quality_grade": analysis.get("image_quality", {}).get("quality_grade", "ACCEPTABLE"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report": analysis.get("unified_report", {})
        })
    except Exception as e:
        current_app.logger.warning(f"Could not persist scan audit: {e}")

    return jsonify({
        "success": True,
        "scan_id": scan_audit_id,
        "image_url": image_url,
        "ocr_text": analysis["ocr_text"],
        "ocr_source": analysis["ocr_source"],
        "ocr_confidence": analysis["ocr_confidence"],
        "tesseract_available": analysis["tesseract_available"],
        "extracted_entities": analysis["extracted_entities"],
        "compliance": analysis["compliance"],
        "counterfeit_risk": analysis["counterfeit_risk"],
        "image_quality": analysis["image_quality"],
        "unified_report": analysis["unified_report"],
    })


@scan_bp.route("/api/scans", methods=["GET"])
def list_scans():
    """
    Returns recent scans from SQLite audit database.
    """
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))
    search = request.args.get("search", "").strip() or None
    scans = db_repository.list_scans(limit=limit, offset=offset, search=search)
    return jsonify({"scans": scans, "total": len(scans)})


@scan_bp.route("/api/save", methods=["POST"])
def save_product():
    """
    Appends scanned product to history / CSV dataset and SQLite database
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
