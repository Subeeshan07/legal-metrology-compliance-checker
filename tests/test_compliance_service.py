import unittest

from services.compliance_service import LegalMetrologyComplianceEngine


class TestComplianceService(unittest.TestCase):

    def test_manufacturer_missing_fails(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_a_manufacturer("")
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["rule"], "Rule 6(1)(a)")

    def test_manufacturer_complete_passes(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_a_manufacturer(
                "ABC Foods Pvt Ltd, "
                "Industrial Area, Chennai - 600001"
            )
        )

        self.assertEqual(result["status"], "PASS")

    def test_product_name_missing_fails(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_b_product_name("")
        )

        self.assertEqual(result["status"], "FAIL")

    def test_product_name_valid_passes(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_b_product_name(
                "Premium Biscuits"
            )
        )

        self.assertEqual(result["status"], "PASS")

    def test_net_quantity_standard_unit_passes(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_c_net_quantity("500 g")
        )

        self.assertEqual(result["status"], "PASS")

    def test_net_quantity_ambiguous_unit_warns(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_c_net_quantity("500 gms")
        )

        self.assertEqual(result["status"], "WARNING")

    def test_net_quantity_missing_fails(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_c_net_quantity("")
        )

        self.assertEqual(result["status"], "FAIL")

    def test_manufacturing_date_valid_passes(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_d_mfg_date("05/2026")
        )

        self.assertEqual(result["status"], "PASS")

    def test_manufacturing_date_invalid_warns(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_d_mfg_date("unknown")
        )

        self.assertEqual(result["status"], "WARNING")

    def test_mrp_with_tax_phrase_passes(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_da_mrp(
                "MRP Rs. 50.00 (Incl. of all taxes)"
            )
        )

        self.assertEqual(result["status"], "PASS")

    def test_mrp_without_tax_phrase_fails(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_da_mrp(
                "MRP Rs. 50.00"
            )
        )

        self.assertEqual(result["status"], "FAIL")

    def test_consumer_care_email_and_phone_passes(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_e_consumer_care(
                "Email: care@example.com "
                "Ph: 9876543210"
            )
        )

        self.assertEqual(result["status"], "PASS")

    def test_consumer_care_phone_only_warns(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_e_consumer_care(
                "Helpline: 1800-123-4567"
            )
        )

        self.assertEqual(result["status"], "WARNING")

    def test_consumer_care_missing_fails(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_e_consumer_care("")
        )

        self.assertEqual(result["status"], "FAIL")

    def test_country_of_origin_present_passes(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_n_country_of_origin("India")
        )

        self.assertEqual(result["status"], "PASS")

    def test_country_of_origin_missing_fails(self):
        result = (
            LegalMetrologyComplianceEngine
            .check_rule_6_1_n_country_of_origin("")
        )

        self.assertEqual(result["status"], "FAIL")

    def test_fully_compliant_product(self):
        product = {
            "product_name": "Premium Biscuits",
            "manufacturer": (
                "ABC Foods Pvt Ltd, "
                "Industrial Area, Chennai - 600001"
            ),
            "net_quantity": "500 g",
            "mfg_date": "05/2026",
            "mrp": "MRP Rs. 50.00 (Incl. of all taxes)",
            "consumer_care": (
                "Email: care@example.com "
                "Ph: 9876543210"
            ),
            "country_of_origin": "India",
        }

        result = LegalMetrologyComplianceEngine.evaluate(product)

        self.assertEqual(
            result["overall_status"],
            "COMPLIANT",
        )

        self.assertEqual(len(result["checks"]), 7)
        self.assertEqual(result["violations"], [])

        self.assertEqual(
            result["violations_summary"],
            "None (Fully Compliant with Rule 6)",
        )

    def test_non_compliant_product(self):
        product = {
            "product_name": "Premium Biscuits",
            "manufacturer": "",
            "net_quantity": "500 g",
            "mfg_date": "05/2026",
            "mrp": "MRP Rs. 50.00",
            "consumer_care": "",
            "country_of_origin": "",
        }

        result = LegalMetrologyComplianceEngine.evaluate(product)

        self.assertEqual(
            result["overall_status"],
            "NON-COMPLIANT",
        )

        self.assertGreater(
            len(result["violations"]),
            0,
        )

    def test_warning_product_needs_review(self):
        product = {
            "product_name": "Premium Biscuits",
            "manufacturer": (
                "ABC Foods Pvt Ltd, "
                "Industrial Area, Chennai - 600001"
            ),
            "net_quantity": "500 gms",
            "mfg_date": "05/2026",
            "mrp": "MRP Rs. 50.00 (Incl. of all taxes)",
            "consumer_care": (
                "Email: care@example.com "
                "Ph: 9876543210"
            ),
            "country_of_origin": "India",
        }

        result = LegalMetrologyComplianceEngine.evaluate(product)

        self.assertEqual(
            result["overall_status"],
            "NEEDS REVIEW",
        )

    def test_evaluate_returns_expected_structure(self):
        product = {}

        result = LegalMetrologyComplianceEngine.evaluate(product)

        expected_keys = {
            "overall_status",
            "checks",
            "violations",
            "violations_summary",
            "timestamp",
        }

        self.assertEqual(
            set(result.keys()),
            expected_keys,
        )

    def test_evaluate_always_runs_seven_checks(self):
        result = LegalMetrologyComplianceEngine.evaluate({})

        self.assertEqual(
            len(result["checks"]),
            7,
        )

    def test_timestamp_is_returned(self):
        result = LegalMetrologyComplianceEngine.evaluate({})

        self.assertTrue(result["timestamp"])


if __name__ == "__main__":
    unittest.main()