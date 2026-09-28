"""
Tests for Phase 7: Frontend Expansion.
Verifies templates render dual outcomes, barcode elements, and /api/scans endpoint.
"""

import unittest
from app import app


class TestFrontendExpansion(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_index_renders_dual_outcome_elements(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")

        # Verify dual outcome containers exist
        self.assertIn("status-banner", html)
        self.assertIn("counterfeit-banner", html)
        self.assertIn("banner-risk-low", html)

        # Verify Barcode and Quality components exist
        self.assertIn("barcode-input", html)
        self.assertIn("image-quality-card", html)
        self.assertIn("quality-grade-badge", html)

        # Verify printable / audit modal exists
        self.assertIn("print-modal", html)
        self.assertIn("rep-counterfeit-box", html)

    def test_api_scans_endpoint_returns_json(self):
        response = self.client.get("/api/scans")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("scans", data)
        self.assertIn("total", data)
        self.assertIsInstance(data["scans"], list)

    def test_scan_with_barcode_input(self):
        response = self.client.post("/api/scan", data={
            "sample_id": "compliant",
            "barcode": "8901234567890"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("scan_id", data)
        self.assertIn("counterfeit_risk", data)
        self.assertEqual(data["counterfeit_risk"]["risk_level"], "LOW")


if __name__ == "__main__":
    unittest.main()
