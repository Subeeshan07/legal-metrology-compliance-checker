"""
Reference Product Repository for Authenticity and Counterfeit Risk Verification.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

REFERENCE_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "reference_products.json",
)


class ReferenceProductRepository:
    """
    Persistence and query layer for verified genuine brand reference profiles.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or REFERENCE_DATA_PATH
        self._cache: Optional[List[Dict[str, Any]]] = None

    def get_all(self) -> List[Dict[str, Any]]:
        if self._cache is not None:
            return self._cache

        if not os.path.isfile(self.data_path):
            logger.warning(f"Reference product file not found: {self.data_path}")
            return []

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
                return self._cache
        except Exception as e:
            logger.error(f"Error loading reference products: {e}")
            return []

    def get_by_id(self, ref_id: str) -> Optional[Dict[str, Any]]:
        for item in self.get_all():
            if item.get("id") == ref_id:
                return item
        return None

    def get_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        clean_code = str(barcode).strip()
        for item in self.get_all():
            for v in item.get("variants", []):
                if v.get("barcode") == clean_code:
                    return item
        return None

    def find_matching_product(self, product_name: str, brand: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Finds the closest reference product by matching brand and product title tokens.
        """
        if not product_name:
            return None

        candidates = self.get_all()
        clean_name = product_name.lower()
        clean_brand = (brand or "").lower()

        # Exact brand match
        for item in candidates:
            item_brand = item.get("brand", "").lower()
            item_title = item.get("product_name", "").lower()

            if clean_brand and clean_brand == item_brand:
                return item

            if item_brand in clean_name or clean_name in item_title:
                return item

        # Token overlap match
        name_tokens = set(clean_name.split())
        best_match = None
        highest_overlap = 0

        for item in candidates:
            ref_tokens = set(item.get("product_name", "").lower().split())
            overlap = len(name_tokens.intersection(ref_tokens))
            if overlap > highest_overlap and overlap >= 2:
                highest_overlap = overlap
                best_match = item

        return best_match


# Default singleton instance
reference_repository = ReferenceProductRepository()
