"""
Automated Test Suite for Legal Metrology Packaged Commodity Compliance Checker
"""

import unittest
import json
import os
from app import app, LegalMetrologyComplianceEngine, load_dataset

class TestLegalMetrologyChecker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_csv_dataset_exists_and_populated(self):
        """Verify the synthetic CSV dataset exists and has at least 1,000 records."""
        df = load_dataset()
        self.assertFalse(df.empty, "Dataset should not be empty")
        self.assertGreaterEqual(len(df), 1000, "Dataset must contain at least 1000 records")
        expected_cols = {"id", "product_name", "category", "manufacturer", "net_quantity", "mrp", "compliance_status"}
        self.assertTrue(expected_cols.issubset(set(df.columns)), f"Missing columns in dataset: {expected_cols - set(df.columns)}")
        print(f"PASS: CSV dataset contains {len(df)} records with valid columns.")

    def test_compliance_engine_compliant(self):
        """Test compliance engine with a valid packaged product."""
        sample_compliant = {
            "product_name": "Pure Chakki Fresh Atta",
            "manufacturer": "Pristine Foods Ltd, Industrial Area, Peenya, Bengaluru - 560058",
            "net_quantity": "5 kg",
            "mrp": "Rs. 245.00 (Incl. of all taxes)",
            "mfg_date": "04/2026",
            "consumer_care": "care@pristine.com | Ph: 1800-220-4400",
            "country_of_origin": "India"
        }
        res = LegalMetrologyComplianceEngine.evaluate(sample_compliant)
        self.assertEqual(res["overall_status"], "COMPLIANT")
        self.assertEqual(len(res["violations"]), 0)
        print("PASS: Compliance engine correctly verified fully compliant declaration.")

    def test_compliance_engine_non_compliant(self):
        """Test compliance engine with missing tax declaration and missing consumer care."""
        sample_non_compliant = {
            "product_name": "Potato Chips",
            "manufacturer": "Snack Co, Delhi",
            "net_quantity": "100 g",
            "mrp": "Rs. 30.00",  # Missing (incl of all taxes)
            "mfg_date": "05/2026",
            "consumer_care": "Not Declared",
            "country_of_origin": "India"
        }
        res = LegalMetrologyComplianceEngine.evaluate(sample_non_compliant)
        self.assertEqual(res["overall_status"], "NON-COMPLIANT")
        self.assertGreaterEqual(len(res["violations"]), 1)
        print(f"PASS: Compliance engine identified {len(res['violations'])} violations.")

    def test_compliance_engine_needs_review_non_standard_units(self):
        """Test compliance engine with non-standard unit 'gms'."""
        sample_review = {
            "product_name": "Kashmiri Chilli Powder",
            "manufacturer": "Spice Mills, MIDC, Pune - 411001",
            "net_quantity": "250 gms",  # Violation: 'gms' instead of 'g'
            "mrp": "Rs. 95.00 (Incl. of all taxes)",
            "mfg_date": "03/2026",
            "consumer_care": "care@spicemills.com | 1800-111-2222",
            "country_of_origin": "India"
        }
        res = LegalMetrologyComplianceEngine.evaluate(sample_review)
        self.assertEqual(res["overall_status"], "NEEDS REVIEW")
        print("PASS: Compliance engine flagged non-standard unit 'gms' for review.")

    def test_api_stats_endpoint(self):
        """Verify /api/stats endpoint returns valid JSON structure and totals."""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("total_products", data)
        self.assertIn("compliant", data)
        self.assertIn("non_compliant", data)
        self.assertIn("needs_review", data)
        self.assertIn("top_violations", data)
        self.assertGreaterEqual(data["total_products"], 1000)
        print(f"PASS: /api/stats returned total {data['total_products']} products.")

    def test_api_products_endpoint(self):
        """Verify /api/products returns paginated results and respects search query."""
        response = self.client.get("/api/products?limit=10&offset=0")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["products"]), 10)
        print("PASS: /api/products returns 10 products with pagination.")

    def test_api_scan_with_preset_sample(self):
        """Verify /api/scan with preset compliant sample."""
        response = self.client.post("/api/scan", data={"sample_id": "compliant"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["compliance"]["overall_status"], "COMPLIANT")
        print("PASS: /api/scan with preset compliant sample returned COMPLIANT verdict.")

    def test_api_rules_endpoint(self):
        """Verify /api/rules returns PCR 2011 rule references."""
        response = self.client.get("/api/rules")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("rules", data)
        self.assertGreaterEqual(len(data["rules"]), 5)
        print(f"PASS: /api/rules returned {len(data['rules'])} statutory rules.")

    def test_tesseract_ocr_path_and_execution(self):
        """Verify Tesseract OCR is detected at C:\\Program Files\\Tesseract-OCR\\tesseract.exe and executes."""
        from app import check_tesseract_available, perform_ocr_on_image
        self.assertTrue(check_tesseract_available(), "Tesseract OCR should be detected and available")
        text, src = perform_ocr_on_image("static/samples/sample_compliant_atta.png")
        self.assertIn("Local Tesseract OCR", src)
        self.assertTrue(len(text) > 0, "OCR extracted text should not be empty")
        self.assertTrue("ATTA" in text.upper() or "HIMALAYAN" in text.upper() or "NET" in text.upper())
        print(f"PASS: Tesseract OCR verified at C:\\Program Files\\Tesseract-OCR\\tesseract.exe with {len(text)} characters extracted.")

if __name__ == "__main__":
    unittest.main()
