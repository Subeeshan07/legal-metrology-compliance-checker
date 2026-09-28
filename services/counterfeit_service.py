"""
Food Counterfeit Risk Detection Engine.

Combines multiple packaging integrity signals to evaluate counterfeit risk:
1. Brand Squatting & Typo Inspection (e.g. 'Himalya' vs 'Himalayan')
2. Authorized Manufacturer & Address Verification
3. Pricing & MRP Anomaly Detection against genuine benchmarks
4. GS1 Barcode / GTIN-13 Validity & Registration
5. Packaging Layout and Declaration Region Consistency

Determines overall risk tier: LOW, MEDIUM, or HIGH, accompanied by auditable evidence.
"""

from typing import Dict, Any, Optional, List
from models.enums import CounterfeitRisk
from services.product_identification_service import product_identification_service
from services.barcode_service import BarcodeService
from services.packaging_layout_service import PackagingLayoutService
from services.normalization_service import normalize_price, normalize_quantity


class FoodCounterfeitRiskEngine:

    @classmethod
    def evaluate_risk(
        cls,
        extracted_entities: Dict[str, Any],
        raw_ocr_text: str = "",
        image_input = None,
        barcode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates counterfeit risk across all available physical and textual signals.
        """
        # If barcode not passed explicitly, attempt discovery from OCR text
        if not barcode and raw_ocr_text:
            extracted_barcodes = BarcodeService.extract_barcodes_from_text(raw_ocr_text)
            if extracted_barcodes:
                barcode = extracted_barcodes[0]["barcode"]

        # 1. Product Identification
        identification = product_identification_service.identify_product(
            extracted_entities,
            raw_ocr_text=raw_ocr_text,
            barcode=barcode,
        )
        reference = identification.get("reference")

        risk_score = 0.0  # 0.0 = Authentic/Low risk, 100.0 = Definite Counterfeit
        risk_factors: List[str] = []
        positive_signals: List[str] = []
        evidence_log: Dict[str, Any] = {}

        # 2. Typo / Brand Squatting Check
        full_text_lower = (raw_ocr_text + " " + extracted_entities.get("product_name", "")).lower()
        if reference:
            for known_fake in reference.get("known_counterfeit_typos", []):
                if known_fake.lower() in full_text_lower:
                    risk_score += 45.0
                    msg = f"Brand squatting pattern detected: text contains '{known_fake}', a known imitation variant of '{reference.get('brand')}'."
                    risk_factors.append(msg)
                    evidence_log["brand_spoofing"] = msg
                    break

        # 3. Manufacturer Legitimacy
        scanned_mfr = extracted_entities.get("manufacturer", "")
        if reference and scanned_mfr:
            authorized_mfrs = reference.get("authorized_manufacturers", [])
            matches_auth = any(
                auth.lower() in scanned_mfr.lower() or scanned_mfr.lower() in auth.lower()
                for auth in authorized_mfrs
            )

            if matches_auth:
                positive_signals.append(f"Manufacturer matches authorized entity: '{scanned_mfr}'.")
                evidence_log["manufacturer_check"] = "AUTHORIZED"
            else:
                risk_score += 30.0
                msg = f"Declared manufacturer '{scanned_mfr}' is not registered as an authorized producer for brand '{reference.get('brand')}'."
                risk_factors.append(msg)
                evidence_log["manufacturer_check"] = "UNAUTHORIZED_OR_UNLISTED"

        # 4. Pricing / MRP Anomaly Check
        norm_price = normalize_price(extracted_entities.get("mrp"))
        norm_qty = normalize_quantity(extracted_entities.get("net_quantity"))

        if reference and norm_price.get("amount"):
            scanned_price = norm_price.get("amount")
            # Find matching variant
            matched_var = None
            for v in reference.get("variants", []):
                if norm_qty.get("raw") and norm_qty.get("raw").lower() in v.get("net_quantity", "").lower():
                    matched_var = v
                    break

            if matched_var and "mrp_range" in matched_var:
                min_p, max_p = matched_var["mrp_range"]
                if scanned_price < min_p * 0.70:
                    risk_score += 35.0
                    msg = f"Drastic pricing anomaly: Declared price (Rs. {scanned_price:.2f}) is over 30% below verified genuine range (Rs. {min_p:.2f} - {max_p:.2f})."
                    risk_factors.append(msg)
                    evidence_log["pricing_anomaly"] = msg
                elif scanned_price > max_p * 1.50:
                    risk_score += 15.0
                    msg = f"Unauthorized price inflation: Price (Rs. {scanned_price:.2f}) exceeds authorized cap (Rs. {max_p:.2f})."
                    risk_factors.append(msg)
                    evidence_log["pricing_anomaly"] = msg
                else:
                    positive_signals.append(f"Price (Rs. {scanned_price:.2f}) is consistent with authorized benchmark.")

        # 5. Barcode Verification
        barcode_verification = BarcodeService.verify_barcode(barcode, reference_product=reference)
        evidence_log["barcode"] = barcode_verification

        if barcode_verification["status"] == "INVALID_CHECKSUM":
            risk_score += 40.0
            risk_factors.append(barcode_verification["message"])
        elif barcode_verification["status"] == "UNREGISTERED_FOR_BRAND":
            risk_score += 25.0
            risk_factors.append(barcode_verification["message"])
        elif barcode_verification["status"] == "MATCHED_GENUINE":
            positive_signals.append(barcode_verification["message"])

        # 6. Packaging Layout Inspection
        layout_res = PackagingLayoutService.analyze_layout(
            image_input,
            extracted_entities,
            reference_product=reference,
        )
        evidence_log["layout"] = layout_res
        if layout_res["layout_status"] == "IRREGULAR":
            risk_score += 15.0
            for anom in layout_res["anomalies"]:
                risk_factors.append(anom)
        else:
            positive_signals.append("Packaging design layout matches standard commercial distribution format.")

        # If product couldn't even be identified in reference database:
        if not identification["matched"]:
            risk_score += 10.0
            risk_factors.append("Product brand could not be matched against verified genuine knowledge base.")

        # Final risk classification
        total_risk = min(100.0, max(0.0, risk_score))
        if total_risk >= 50.0:
            risk_tier = CounterfeitRisk.HIGH
            recommendation = "HIGH COUNTERFEIT RISK: Significant discrepancies in branding, pricing, or manufacturer legitimacy. Quarantine product and report to brand integrity officer."
        elif total_risk >= 25.0:
            risk_tier = CounterfeitRisk.MEDIUM
            recommendation = "MEDIUM RISK: Minor anomalies detected (e.g. unverified manufacturer or barcode mismatch). Conduct secondary lab test or physical batch review."
        else:
            risk_tier = CounterfeitRisk.LOW
            recommendation = "LOW RISK: Packaging specifications, brand markings, and price points align with genuine product reference data."

        return {
            "risk_tier": str(risk_tier),
            "risk_score": round(total_risk, 1),
            "identified_product": {
                "matched": identification["matched"],
                "match_confidence": identification["confidence"],
                "brand": identification.get("brand"),
                "product_name": identification.get("product_name"),
            },
            "risk_factors": risk_factors,
            "positive_signals": positive_signals,
            "evidence": evidence_log,
            "recommendation": recommendation,
        }
