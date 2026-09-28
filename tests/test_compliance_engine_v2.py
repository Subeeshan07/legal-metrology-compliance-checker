"""
Tests for Phase 2: Formalized Compliance Engine, Modular Rules, Normalization, and Extraction Improvements.
"""

import unittest
from models.enums import ComplianceStatus
from models.compliance import RuleEvaluation, ComplianceReport
from rules.rule_registry import default_registry, RuleRegistry
from rules.manufacturer_rule import ManufacturerRule
from rules.net_quantity_rule import NetQuantityRule
from rules.mfg_date_rule import MfgDateRule
from rules.mrp_rule import MRPRule
from rules.consumer_care_rule import ConsumerCareRule
from rules.country_of_origin_rule import CountryOfOriginRule
from services.normalization_service import (
    normalize_quantity,
    normalize_price,
    normalize_date,
    normalize_country,
    normalize_declarations,
)
from services.extraction_service import extract_entities_from_text
from services.compliance_service import LegalMetrologyComplianceEngine


class TestComplianceEngineV2(unittest.TestCase):

    def test_improved_entity_extraction_250_g(self):
        """
        Task 2.3 requirement: Fix known extraction weakness to recognize '250 g'.
        """
        text = "SNACK PACK\nWeight 250 g"
        extracted = extract_entities_from_text(text)
        self.assertEqual(extracted["net_quantity"], "250 g")

    def test_improved_entity_extraction_packed_during(self):
        """
        Task 2.3 requirement: Extract only the actual date from phrases like 'Packed during 06/2026'.
        """
        text = "CRUNCHY SNACKS\nPacked during 06/2026"
        extracted = extract_entities_from_text(text)
        self.assertEqual(extracted["mfg_date"], "06/2026")

    def test_normalization_quantity_variants(self):
        # Standard unit
        norm_std = normalize_quantity("250 g")
        self.assertTrue(norm_std["is_standard_unit"])
        self.assertEqual(norm_std["value"], 250.0)
        self.assertEqual(norm_std["unit"], "g")

        # Non-standard unit 'gms'
        norm_non_std = normalize_quantity("200 gms")
        self.assertFalse(norm_non_std["is_standard_unit"])
        self.assertEqual(norm_non_std["value"], 200.0)
        self.assertEqual(norm_non_std["standard_unit"], "g")

        # Volume
        norm_vol = normalize_quantity("1.5 L")
        self.assertTrue(norm_vol["is_standard_unit"])
        self.assertEqual(norm_vol["value"], 1.5)

    def test_normalization_mrp_variants(self):
        # Compliant with tax clause
        norm_comp = normalize_price("MRP Rs. 245.00 (Incl. of all taxes)")
        self.assertEqual(norm_comp["amount"], 245.0)
        self.assertTrue(norm_comp["has_tax_clause"])

        # Non-compliant without tax clause
        norm_non_comp = normalize_price("MRP Rs. 40.00")
        self.assertEqual(norm_non_comp["amount"], 40.0)
        self.assertFalse(norm_non_comp["has_tax_clause"])

    def test_normalization_date_variants(self):
        norm1 = normalize_date("05/2026")
        self.assertTrue(norm1["is_valid"])
        self.assertEqual(norm1["month"], 5)
        self.assertEqual(norm1["year"], 2026)

        norm2 = normalize_date("Packed during 06/2026")
        self.assertTrue(norm2["is_valid"])
        self.assertEqual(norm2["month"], 6)
        self.assertEqual(norm2["year"], 2026)

        norm_text = normalize_date("Mfg Date: May 2026")
        self.assertTrue(norm_text["is_valid"])
        self.assertEqual(norm_text["month"], 5)
        self.assertEqual(norm_text["year"], 2026)

    def test_rule_registry_default_rules(self):
        registry = default_registry
        rules = registry.get_rules()
        self.assertGreaterEqual(len(rules), 7)

    def test_evidence_based_compliance_results(self):
        declarations = {
            "product_name": "Himalayan Atta",
            "manufacturer": "Pristine Foods, Peenya, Bengaluru - 560058",
            "net_quantity": "5 kg",
            "mrp": "MRP Rs. 245.00 (Incl. of all taxes)",
            "mfg_date": "05/2026",
            "consumer_care": "care@pristine.com | 1800-220-4400",
            "country_of_origin": "India",
        }
        result = LegalMetrologyComplianceEngine.evaluate(declarations)
        self.assertEqual(result["overall_status"], "COMPLIANT")

        # Check evidence attached to checks
        for check in result["checks"]:
            self.assertIn("detected_value", check)
            self.assertIn("evidence", check)
            self.assertIn("normalized_value", check)


    def test_rule_registry_evaluate_report(self):
        declarations = {
            "product_name": "Crunchy Chips",
            "manufacturer": "Surya Snacks LLP",
            "net_quantity": "80 g",
            "mrp": "MRP Rs. 40.00",  # missing tax clause -> NON-COMPLIANT
            "mfg_date": "04/2026",
            "consumer_care": "",     # missing -> NON-COMPLIANT
            "country_of_origin": "", # missing -> NON-COMPLIANT
        }
        report = default_registry.evaluate(declarations)
        self.assertIsInstance(report, ComplianceReport)
        self.assertEqual(report.overall_status, ComplianceStatus.NON_COMPLIANT)
        self.assertFalse(report.compliant)
        self.assertGreaterEqual(len(report.violations), 1)


if __name__ == "__main__":
    unittest.main()
