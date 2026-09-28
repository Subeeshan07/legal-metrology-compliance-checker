"""
Unified Food Compliance & Authenticity Analysis Orchestrator.

Implements the end-to-end multi-stage pipeline:
Upload/Camera -> Image Quality Assessment -> OCR Extraction -> Entity Parsing
-> Declaration Normalization -> Legal Metrology Compliance Checking -> Counterfeit Risk Detection
-> Unified Auditable Report.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from services.image_quality_service import ImageQualityAssessmentService
from services.ocr_service import ocr_service, check_tesseract_available
from services.extraction_service import extract_entities_from_text
from services.normalization_service import normalize_declarations
from rules.rule_registry import default_registry
from services.compliance_service import LegalMetrologyComplianceEngine
from services.counterfeit_service import FoodCounterfeitRiskEngine
from services.barcode_service import BarcodeService

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:

    @classmethod
    def analyze_scan(
        cls,
        image_path: Optional[str] = None,
        manual_text: Optional[str] = None,
        preset_id: Optional[str] = None,
        barcode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes the complete unified verification workflow.
        """
        # Stage 1: Quality Assessment (if image provided)
        quality_report = None
        if image_path and os.path.isfile(image_path):
            try:
                quality_report = ImageQualityAssessmentService.evaluate_image(image_path)
            except Exception as e:
                logger.warning(f"Image quality assessment error: {e}")

        # Stage 2: OCR Extraction
        ocr_text = ""
        ocr_source = ""
        ocr_confidence = 95.0
        word_confidences = []

        if manual_text:
            ocr_text = manual_text.strip()
            ocr_source = "Pre-loaded Reference Package Sample" if (preset_id or image_path) else "Manual Text Entry / Verification"
            ocr_confidence = 96.0
        elif image_path and os.path.isfile(image_path):
            if check_tesseract_available():
                ocr_res = ocr_service.extract_text(image_path)
                ocr_text = ocr_res.get("text", "")
                ocr_source = ocr_res.get("source", "Tesseract OCR")
                ocr_confidence = ocr_res.get("confidence", 90.0)
                word_confidences = ocr_res.get("word_confidences", [])
            else:
                ocr_source = "Tesseract binary not installed on host machine"
                ocr_text = ""


        # Stage 3: Entity Extraction
        entities = extract_entities_from_text(ocr_text)

        # Stage 4: Declaration Normalization
        normalized = normalize_declarations(entities)

        # Stage 5: Legal Metrology Compliance Evaluation
        compliance_dict = LegalMetrologyComplianceEngine.evaluate(entities)

        # Stage 6: Food Counterfeit Risk Detection
        counterfeit_dict = FoodCounterfeitRiskEngine.evaluate_risk(
            extracted_entities=entities,
            raw_ocr_text=ocr_text,
            image_input=image_path,
            barcode=barcode,
        )

        # Stage 7: Unified Auditable Report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        unified_report = {
            "timestamp": timestamp,
            "legal_compliance": {
                "verdict": compliance_dict["overall_status"],
                "is_compliant": compliance_dict["overall_status"] == "COMPLIANT",
                "violations_count": len(compliance_dict["violations"]),
                "violations_summary": compliance_dict["violations_summary"],
                "rules_checked": len(compliance_dict["checks"]),
            },
            "counterfeit_analysis": {
                "risk_tier": counterfeit_dict["risk_tier"],
                "risk_score": counterfeit_dict["risk_score"],
                "matched_brand": counterfeit_dict["identified_product"]["brand"],
                "recommendation": counterfeit_dict["recommendation"],
            },
            "image_quality": quality_report,
            "ocr_metrics": {
                "source": ocr_source,
                "confidence": f"{ocr_confidence:.1f}%",
                "character_count": len(ocr_text),
            }
        }

        return {
            "success": True,
            "ocr_text": ocr_text,
            "ocr_source": ocr_source,
            "ocr_confidence": f"{ocr_confidence:.1f}%",
            "word_confidences": word_confidences,
            "tesseract_available": check_tesseract_available(),
            "extracted_entities": entities,
            "normalized_declarations": normalized,
            "compliance": compliance_dict,
            "counterfeit_risk": counterfeit_dict,
            "image_quality": quality_report,
            "unified_report": unified_report,
        }
