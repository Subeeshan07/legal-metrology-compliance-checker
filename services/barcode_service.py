"""
Barcode and QR Code Extraction and Verification Service.

Extracts barcodes and QR codes from image data and OCR transcripts,
verifying standard GS1 GTIN-13 / EAN-13 checksum compliance and matching against genuine products.
"""

import re
from typing import Dict, Any, Optional, List


def validate_ean13_checksum(barcode_str: str) -> bool:
    """
    Validates standard GS1 EAN-13 / GTIN-13 checksum algorithm.
    """
    digits = [int(c) for c in barcode_str if c.isdigit()]
    if len(digits) != 13:
        return False

    checksum = digits[-1]
    # Sum of first 12 digits: odd positions * 1, even positions * 3
    total = sum(d if i % 2 == 0 else d * 3 for i, d in enumerate(digits[:12]))
    calculated_checksum = (10 - (total % 10)) % 10
    return checksum == calculated_checksum


class BarcodeService:

    @classmethod
    def extract_barcodes_from_text(cls, text: str) -> List[Dict[str, Any]]:
        """
        Scans text and OCR streams for 12 or 13-digit potential product barcode numbers.
        """
        results = []
        matches = re.finditer(r"\b(\d{12,13})\b", text)
        for m in matches:
            code = m.group(1)
            is_valid_checksum = validate_ean13_checksum(code) if len(code) == 13 else False
            results.append({
                "barcode": code,
                "length": len(code),
                "is_valid_checksum": is_valid_checksum,
                "format": "EAN-13" if len(code) == 13 else "UPC-A",
            })
        return results

    @classmethod
    def verify_barcode(
        cls,
        barcode: Optional[str],
        reference_product: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validates the barcode and verifies if it matches authorized variants in the reference profile.
        """
        if not barcode:
            return {
                "detected": False,
                "barcode": None,
                "valid_checksum": False,
                "matches_reference": False,
                "status": "NOT_DETECTED",
                "message": "No barcode detected on visible packaging.",
            }

        code_clean = str(barcode).strip()
        is_valid = validate_ean13_checksum(code_clean) if len(code_clean) == 13 else len(code_clean) in (12, 13)

        if not is_valid and len(code_clean) == 13:
            return {
                "detected": True,
                "barcode": code_clean,
                "valid_checksum": False,
                "matches_reference": False,
                "status": "INVALID_CHECKSUM",
                "message": f"Barcode {code_clean} failed GS1 EAN-13 mathematical checksum validation (possible fake).",
            }

        # Check against reference profile
        if reference_product:
            registered_barcodes = [
                v.get("barcode") for v in reference_product.get("variants", []) if v.get("barcode")
            ]
            if code_clean in registered_barcodes:
                return {
                    "detected": True,
                    "barcode": code_clean,
                    "valid_checksum": True,
                    "matches_reference": True,
                    "status": "MATCHED_GENUINE",
                    "message": f"Barcode {code_clean} matches verified genuine brand SKU.",
                }
            elif registered_barcodes:
                return {
                    "detected": True,
                    "barcode": code_clean,
                    "valid_checksum": is_valid,
                    "matches_reference": False,
                    "status": "UNREGISTERED_FOR_BRAND",
                    "message": f"Barcode {code_clean} does not belong to authorized brand SKU variants.",
                }

        return {
            "detected": True,
            "barcode": code_clean,
            "valid_checksum": is_valid,
            "matches_reference": None,
            "status": "VALID_FORMAT",
            "message": f"Barcode format valid ({code_clean}).",
        }
