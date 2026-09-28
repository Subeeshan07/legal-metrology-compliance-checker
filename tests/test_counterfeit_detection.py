"""
Tests for Phase 4: Food Counterfeit Risk Detection.
"""

import unittest
from services.barcode_service import BarcodeService, validate_ean13_checksum
from services.counterfeit_service import FoodCounterfeitRiskEngine
from repositories.reference_repository import reference_repository


class TestCounterfeitDetection(unittest.TestCase):

    def test_reference_repository_loads_products(self):
        refs = reference_repository.get_all()
        self.assertGreaterEqual(len(refs), 3)
        brands = [r["brand"] for r in refs]
        self.assertIn("Himalayan", brands)
        self.assertIn("Surya", brands)

    def test_barcode_checksum_validation(self):
        # Valid EAN-13
        self.assertTrue(validate_ean13_checksum("8901234567890"))
        # Invalid EAN-13 (tampered checksum digit)
        self.assertFalse(validate_ean13_checksum("8901234567899"))

    def test_genuine_product_low_risk(self):
        genuine_declarations = {
            "product_name": "Himalayan Chakki Fresh Atta",
            "manufacturer": "Pristine Foods & Agro Ltd, Phase 2, Peenya Industrial Area, Bengaluru - 560058",
            "net_quantity": "5 kg",
            "mrp": "MRP Rs. 245.00 (Incl. of all taxes)",
            "mfg_date": "05/2026",
            "consumer_care": "care@pristine.com | 1800-220-4400",
            "country_of_origin": "India",
        }
        ocr_text = (
            "HIMALAYAN CHAKKI FRESH ATTA\n"
            "Net Quantity: 5 kg\n"
            "MRP Rs. 245.00 (Incl. of all taxes)\n"
            "Barcode: 8901234567890"
        )
        result = FoodCounterfeitRiskEngine.evaluate_risk(
            extracted_entities=genuine_declarations,
            raw_ocr_text=ocr_text,
            barcode="8901234567890",
        )
        self.assertEqual(result["risk_tier"], "LOW")
        self.assertTrue(result["identified_product"]["matched"])
        self.assertEqual(result["identified_product"]["brand"], "Himalayan")

    def test_counterfeit_brand_spoofing_high_risk(self):
        fake_declarations = {
            "product_name": "Himalya Chakki Fresh Atta",  # Spoofed name with typo
            "manufacturer": "Fake Mills Ltd, Unknown Area",
            "net_quantity": "5 kg",
            "mrp": "MRP Rs. 110.00",  # Abnormally cheap (Rs 110 vs Rs 245)
            "mfg_date": "05/2026",
            "consumer_care": "",
            "country_of_origin": "India",
        }
        ocr_text = "HIMALYA CHAKKI ATTA - Special Discount Rs 110"
        result = FoodCounterfeitRiskEngine.evaluate_risk(
            extracted_entities=fake_declarations,
            raw_ocr_text=ocr_text,
        )
        self.assertEqual(result["risk_tier"], "HIGH")
        self.assertGreaterEqual(len(result["risk_factors"]), 1)
        self.assertIn("brand_spoofing", result["evidence"])


if __name__ == "__main__":
    unittest.main()
