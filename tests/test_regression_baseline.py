"""
Regression baseline for the Legal Metrology Compliance Checker.

These tests protect externally observable prototype behaviour before the
application is refactored into a modular architecture.

Task: 0.4 — Regression / Smoke-Test Baseline
"""

import os
import unittest

from app import app, load_dataset, check_tesseract_available


class TestRegressionBaseline(unittest.TestCase):
    """
    Regression tests for the existing prototype.

    These tests intentionally focus on externally observable behaviour
    rather than internal implementation details. This allows the internal
    architecture to be refactored later without changing the expected
    application behaviour.
    """

    @classmethod
    def setUpClass(cls):
        """
        Configure Flask for testing and create a reusable test client.
        """
        app.config["TESTING"] = True
        cls.client = app.test_client()

    # ---------------------------------------------------------
    # Application Smoke Tests
    # ---------------------------------------------------------

    def test_application_exists(self):
        """
        Flask application should be constructed successfully.
        """
        self.assertIsNotNone(app)

    def test_home_page_loads(self):
        """
        Main application page should remain accessible.
        """
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    # ---------------------------------------------------------
    # API Contract Tests
    # ---------------------------------------------------------

    def test_stats_api_contract(self):
        """
        Dashboard statistics API must preserve its
        existing response contract.
        """
        response = self.client.get("/api/stats")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertIsInstance(data, dict)

        self.assertIn("total_products", data)
        self.assertIn("compliant", data)
        self.assertIn("non_compliant", data)
        self.assertIn("needs_review", data)

        self.assertGreaterEqual(data["total_products"], 1)

        # Total products should equal the sum of all
        # compliance status categories.
        self.assertEqual(
            data["total_products"],
            data["compliant"]
            + data["non_compliant"]
            + data["needs_review"]
        )

    def test_products_api_contract(self):
        """
        Products API should return a successful JSON response.
        """
        response = self.client.get("/api/products")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertIsInstance(data, dict)

    def test_rules_api_contract(self):
        """
        Compliance rules endpoint should expose
        the prototype Legal Metrology rules.
        """
        response = self.client.get("/api/rules")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertIsInstance(data, dict)
        self.assertIn("rules", data)

        # The current prototype contains seven statutory checks,
        # but we keep the regression requirement slightly flexible.
        self.assertGreaterEqual(len(data["rules"]), 5)

    # ---------------------------------------------------------
    # Dataset Regression Tests
    # ---------------------------------------------------------

    def test_dataset_can_be_loaded(self):
        """
        The prototype dataset must remain loadable.
        """
        dataset = load_dataset()

        self.assertIsNotNone(dataset)
        self.assertGreater(len(dataset), 0)

    def test_dataset_file_exists(self):
        """
        The packaged prototype dataset must remain available.
        """
        self.assertTrue(
            os.path.exists("legal_metrology_dataset.csv"),
            "legal_metrology_dataset.csv could not be found."
        )

    # ---------------------------------------------------------
    # Preset Scan Regression
    # ---------------------------------------------------------

    def test_compliant_preset_scan(self):
        """
        Known compliant preset should remain processable
        and return a COMPLIANT verdict.
        """
        response = self.client.post(
            "/api/scan",
            data={"sample_id": "compliant"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertIsInstance(data, dict)
        self.assertTrue(data["success"])

        self.assertIn("compliance", data)

        self.assertEqual(
            data["compliance"]["overall_status"],
            "COMPLIANT"
        )

    # ---------------------------------------------------------
    # Invalid Request Behaviour
    # ---------------------------------------------------------

    def test_scan_without_input_does_not_crash_server(self):
        """
        A scan request without an image, OCR text, or preset
        must not cause an unhandled server-side failure.

        The exact 4xx response may evolve during future API work,
        so this regression test only protects against 5xx failures.
        """
        response = self.client.post(
            "/api/scan",
            data={}
        )

        self.assertLess(
            response.status_code,
            500,
            "Empty scan request caused a server-side failure."
        )

    # ---------------------------------------------------------
    # OCR Environment Regression
    # ---------------------------------------------------------

    def test_tesseract_is_available(self):
        """
        Development baseline requires the Tesseract
        OCR executable to be available.
        """
        self.assertTrue(
            check_tesseract_available(),
            "Tesseract OCR executable is not available."
        )


if __name__ == "__main__":
    unittest.main()