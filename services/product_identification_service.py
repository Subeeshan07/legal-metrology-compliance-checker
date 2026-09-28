"""
Product Identification Service.

Identifies brand, product line, and variant from OCR text, extracted entities,
and barcodes by matching against verified reference profiles.
"""

from typing import Dict, Any, Optional
from repositories.reference_repository import reference_repository, ReferenceProductRepository


class ProductIdentificationService:

    def __init__(self, repo: Optional[ReferenceProductRepository] = None):
        self.repo = repo or reference_repository

    def identify_product(
        self,
        extracted_entities: Dict[str, Any],
        raw_ocr_text: str = "",
        barcode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Determines the most probable genuine product candidate from extracted declarations.
        """
        # 1. Barcode direct lookup
        if barcode:
            ref_by_barcode = self.repo.get_by_barcode(barcode)
            if ref_by_barcode:
                return {
                    "matched": True,
                    "confidence": 98.0,
                    "match_type": "BARCODE_GTIN_EXACT",
                    "reference": ref_by_barcode,
                    "brand": ref_by_barcode.get("brand"),
                    "product_name": ref_by_barcode.get("product_name"),
                }

        # 2. Product Name / Text Matching
        prod_name = extracted_entities.get("product_name", "")
        mfr_name = extracted_entities.get("manufacturer", "")

        ref = self.repo.find_matching_product(prod_name)
        if not ref and raw_ocr_text:
            # Try matching individual lines in raw text
            for line in raw_ocr_text.splitlines():
                if len(line.strip()) > 4:
                    ref = self.repo.find_matching_product(line.strip())
                    if ref:
                        break

        if ref:
            # Score match confidence based on token matching
            tokens_in_text = [t.lower() for t in (prod_name + " " + raw_ocr_text).split()]
            ref_tokens = [t.lower() for t in ref.get("product_name", "").split()]
            matched_count = sum(1 for t in ref_tokens if t in tokens_in_text)
            ratio = matched_count / max(1, len(ref_tokens))
            confidence = round(min(95.0, max(50.0, ratio * 100.0)), 1)

            return {
                "matched": True,
                "confidence": confidence,
                "match_type": "TEXT_HEURISTIC",
                "reference": ref,
                "brand": ref.get("brand"),
                "product_name": ref.get("product_name"),
            }

        return {
            "matched": False,
            "confidence": 0.0,
            "match_type": "UNIDENTIFIED",
            "reference": None,
            "brand": None,
            "product_name": prod_name or "Unidentified Product",
        }


product_identification_service = ProductIdentificationService()
