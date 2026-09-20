import unittest

from services.extraction_service import extract_entities_from_text


class TestExtractionService(unittest.TestCase):

    def test_returns_expected_structure(self):
        result = extract_entities_from_text("TEST PRODUCT")

        expected_keys = {
            "product_name",
            "manufacturer",
            "net_quantity",
            "mrp",
            "mfg_date",
            "consumer_care",
            "country_of_origin",
            "raw_text",
        }

        self.assertEqual(set(result.keys()), expected_keys)

    def test_preserves_raw_text(self):
        text = "TEST PRODUCT\nNet Qty: 100 g"

        result = extract_entities_from_text(text)

        self.assertEqual(result["raw_text"], text)

    def test_extracts_product_name(self):
        text = (
            "PREMIUM BISCUITS\n"
            "Net Qty: 100 g"
        )

        result = extract_entities_from_text(text)

        self.assertEqual(
            result["product_name"],
            "PREMIUM BISCUITS",
        )

    def test_extracts_net_quantity(self):
        text = (
            "PREMIUM BISCUITS\n"
            "Net Quantity: 500 g"
        )

        result = extract_entities_from_text(text)

        self.assertEqual(
            result["net_quantity"],
            "500 g",
        )

    def test_extracts_net_quantity_fallback(self):
        """
        Test the existing standalone quantity fallback.

        The current fallback regex recognises values such as
        '250 gm' but does not recognise plain '250 g'.

        Task 1.5 preserves this existing behaviour rather than
        changing the extraction algorithm.
        """
        text = (
            "PREMIUM BISCUITS\n"
            "Pack Size 250 gm"
        )

        result = extract_entities_from_text(text)

        self.assertEqual(
            result["net_quantity"],
            "250 gm",
        )

    def test_extracts_mrp(self):
        text = (
            "PREMIUM BISCUITS\n"
            "MRP Rs. 50.00 (Incl. of all taxes)"
        )

        result = extract_entities_from_text(text)

        self.assertIn("MRP", result["mrp"])
        self.assertIn("50.00", result["mrp"])

    def test_extracts_standalone_price_fallback(self):
        text = (
            "PREMIUM BISCUITS\n"
            "Price Rs. 75.00"
        )

        result = extract_entities_from_text(text)

        self.assertEqual(
            result["mrp"],
            "MRP Rs. 75.00",
        )

    def test_extracts_manufacturing_date(self):
        text = (
            "PREMIUM BISCUITS\n"
            "Mfg Date: 05/2026"
        )

        result = extract_entities_from_text(text)

        self.assertEqual(
            result["mfg_date"],
            "05/2026",
        )

    def test_extracts_manufacturing_date_fallback(self):
        """
        Test the existing MM/YYYY fallback.

        The text intentionally avoids primary date keywords such
        as 'Packed' or 'Mfg' so that the fallback regex is tested.
        """
        text = (
            "PREMIUM BISCUITS\n"
            "Production period 06/2026"
        )

        result = extract_entities_from_text(text)

        self.assertEqual(
            result["mfg_date"],
            "06/2026",
        )

    def test_extracts_consumer_care(self):
        text = (
            "PREMIUM BISCUITS\n"
            "Consumer Care: help@example.com | "
            "Ph: 9876543210"
        )

        result = extract_entities_from_text(text)

        self.assertIn(
            "Consumer Care",
            result["consumer_care"],
        )

    def test_extracts_consumer_care_fallback(self):
        text = (
            "PREMIUM BISCUITS\n"
            "Email help@example.com\n"
            "Phone 9876543210"
        )

        result = extract_entities_from_text(text)

        self.assertIn(
            "help@example.com",
            result["consumer_care"],
        )

        self.assertIn(
            "9876543210",
            result["consumer_care"],
        )

    def test_extracts_manufacturer(self):
        text = (
            "PREMIUM BISCUITS\n"
            "Manufactured by: ABC Foods Pvt Ltd"
        )

        result = extract_entities_from_text(text)

        self.assertIn(
            "ABC Foods Pvt Ltd",
            result["manufacturer"],
        )

    def test_extracts_manufacturer_fallback(self):
        text = (
            "PREMIUM BISCUITS\n"
            "ABC Foods Pvt Ltd"
        )

        result = extract_entities_from_text(text)

        self.assertEqual(
            result["manufacturer"],
            "ABC Foods Pvt Ltd",
        )

    def test_extracts_country_of_origin(self):
        text = (
            "PREMIUM BISCUITS\n"
            "Country of Origin: India"
        )

        result = extract_entities_from_text(text)

        self.assertEqual(
            result["country_of_origin"],
            "India",
        )

    def test_empty_text_returns_empty_fields(self):
        result = extract_entities_from_text("")

        self.assertEqual(result["product_name"], "")
        self.assertEqual(result["manufacturer"], "")
        self.assertEqual(result["net_quantity"], "")
        self.assertEqual(result["mrp"], "")
        self.assertEqual(result["mfg_date"], "")
        self.assertEqual(result["consumer_care"], "")
        self.assertEqual(result["country_of_origin"], "")
        self.assertEqual(result["raw_text"], "")


if __name__ == "__main__":
    unittest.main()