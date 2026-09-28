"""
Tests for extracted route blueprints: web, scan, product, analytics, and rules.
"""

import unittest
from unittest.mock import patch
import pandas as pd
from app import app


class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Legal Metrology", response.data)

    def test_stats_route(self):
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("total_products", data)
        self.assertIn("compliant", data)
        self.assertIn("compliance_distribution", data)

    def test_products_route(self):
        response = self.client.get("/api/products")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("products", data)
        self.assertIn("total", data)
        self.assertIsInstance(data["products"], list)

    def test_rules_route(self):
        response = self.client.get("/api/rules")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("rules", data)
        self.assertGreaterEqual(len(data["rules"]), 7)

    def test_scan_route_preset(self):
        response = self.client.post("/api/scan", data={"sample_id": "compliant"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("compliance", data)
        self.assertEqual(data["compliance"]["overall_status"], "COMPLIANT")

    def test_scan_route_no_input(self):
        response = self.client.post("/api/scan", data={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_save_product_route(self):
        with patch("routes.scan_routes.save_record_to_dataset", return_value=True):
            response = self.client.post(
                "/api/save",
                json={
                    "product_name": "Test Atta",
                    "category": "Flour",
                    "compliance_status": "COMPLIANT",
                },
            )
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data["success"])
            self.assertIn("record", data)
            self.assertEqual(data["record"]["product_name"], "Test Atta")


if __name__ == "__main__":
    unittest.main()
