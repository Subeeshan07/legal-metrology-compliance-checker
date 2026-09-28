"""
Tests for Phase 5: Unified Analysis Pipeline & Distinct Final Outcomes.
"""

import unittest
from app import app
from services.analysis_orchestrator import AnalysisOrchestrator


class TestUnifiedPipeline(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_orchestrator_runs_end_to_end(self):
        label_text = (
            "HIMALAYAN CHAKKI FRESH ATTA\n"
            "Net Quantity: 5 kg\n"
            "MRP Rs. 245.00 (Incl. of all taxes)\n"
            "Mfg Date: 05/2026\n"
            "Manufactured by: Pristine Foods & Agro Ltd, Phase 2, Peenya, Bengaluru - 560058\n"
            "Consumer Care: care@pristine.com | 1800-220-4400\n"
            "Country of Origin: India\n"
            "Barcode: 8901234567890"
        )
        res = AnalysisOrchestrator.analyze_scan(manual_text=label_text)
        self.assertTrue(res["success"])
        self.assertIn("compliance", res)
        self.assertIn("counterfeit_risk", res)
        self.assertIn("unified_report", res)

        # Check decoupling of verdicts
        self.assertEqual(res["compliance"]["overall_status"], "COMPLIANT")
        self.assertEqual(res["counterfeit_risk"]["risk_tier"], "LOW")

    def test_genuine_product_with_non_compliant_label(self):
        """
        Demonstrates the key requirement: A genuine product can have a labeling issue
        (e.g. missing taxes clause) but still have low counterfeit risk.
        """
        label_text = (
            "HIMALAYAN CHAKKI FRESH ATTA\n"
            "Net Quantity: 5 kg\n"
            "MRP Rs. 245.00\n"  # NON-COMPLIANT: Missing 'incl of all taxes'
            "Mfg Date: 05/2026\n"
            "Manufactured by: Pristine Foods & Agro Ltd, Phase 2, Peenya, Bengaluru - 560058\n"
            "Consumer Care: care@pristine.com | 1800-220-4400\n"
            "Country of Origin: India\n"
            "Barcode: 8901234567890"
        )
        res = AnalysisOrchestrator.analyze_scan(manual_text=label_text)
        # Legal compliance should fail
        self.assertEqual(res["compliance"]["overall_status"], "NON-COMPLIANT")
        # Counterfeit risk should still be LOW because manufacturer and barcode match genuine reference
        self.assertEqual(res["counterfeit_risk"]["risk_tier"], "LOW")

    def test_scan_api_endpoint_returns_unified_payload(self):
        response = self.client.post("/api/scan", data={"sample_id": "compliant"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("compliance", data)
        self.assertIn("counterfeit_risk", data)
        self.assertIn("unified_report", data)
        self.assertIn("legal_compliance", data["unified_report"])
        self.assertIn("counterfeit_analysis", data["unified_report"])


if __name__ == "__main__":
    unittest.main()
