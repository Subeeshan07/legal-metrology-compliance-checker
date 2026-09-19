"""
Tests for the OCR service.

Task 1.4 — OCR Service Extraction
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from services.ocr_service import (
    OCRService,
    check_tesseract_available,
    perform_ocr_on_image,
)


class TestOCRService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.image_path = os.path.join(
            self.temp_dir.name,
            "label.png",
        )

        image = Image.new(
            "RGB",
            (1200, 600),
            color="white",
        )

        image.save(self.image_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_service_can_be_created(self):
        service = OCRService()

        self.assertIsInstance(
            service,
            OCRService,
        )

    def test_service_uses_configured_tesseract_command(self):
        custom_command = r"C:\Fake\Tesseract\tesseract.exe"

        service = OCRService(
            tesseract_cmd=custom_command,
        )

        self.assertEqual(
            service.tesseract_cmd,
            custom_command,
        )

    @patch(
        "services.ocr_service.pytesseract.get_tesseract_version"
    )
    def test_availability_returns_true_when_tesseract_works(
        self,
        mock_version,
    ):
        mock_version.return_value = "5.0"

        service = OCRService()

        result = service.check_availability()

        self.assertTrue(result)
        self.assertTrue(service.available)

    @patch(
        "services.ocr_service.pytesseract.get_tesseract_version"
    )
    def test_availability_returns_false_when_tesseract_fails(
        self,
        mock_version,
    ):
        mock_version.side_effect = RuntimeError(
            "Tesseract unavailable"
        )

        service = OCRService()

        result = service.check_availability()

        self.assertFalse(result)
        self.assertFalse(service.available)

    @patch(
        "services.ocr_service.preprocess_image_for_ocr"
    )
    @patch(
        "services.ocr_service.pytesseract.image_to_string"
    )
    def test_extract_text_returns_ocr_result(
        self,
        mock_image_to_string,
        mock_preprocess,
    ):
        mock_preprocess.return_value = object()
        mock_image_to_string.return_value = (
            "Net Quantity: 500 g"
        )

        service = OCRService()
        service.available = True

        result = service.extract_text(
            self.image_path
        )

        self.assertTrue(result["success"])

        self.assertEqual(
            result["text"],
            "Net Quantity: 500 g",
        )

        self.assertIsNone(
            result["error"]
        )

    @patch(
        "services.ocr_service.preprocess_image_for_ocr"
    )
    @patch(
        "services.ocr_service.pytesseract.image_to_string"
    )
    def test_extract_text_strips_whitespace(
        self,
        mock_image_to_string,
        mock_preprocess,
    ):
        mock_preprocess.return_value = object()

        mock_image_to_string.return_value = (
            "  MRP Rs. 50  \n"
        )

        service = OCRService()
        service.available = True

        result = service.extract_text(
            self.image_path
        )

        self.assertEqual(
            result["text"],
            "MRP Rs. 50",
        )

    @patch.object(
        OCRService,
        "check_availability",
        return_value=False,
    )
    def test_extract_text_handles_unavailable_tesseract(
        self,
        mock_check,
    ):
        service = OCRService()
        service.available = False

        result = service.extract_text(
            self.image_path
        )

        self.assertFalse(
            result["success"]
        )

        self.assertEqual(
            result["text"],
            "",
        )

        self.assertIsNotNone(
            result["error"]
        )

    @patch(
        "services.ocr_service.preprocess_image_for_ocr"
    )
    @patch(
        "services.ocr_service.pytesseract.image_to_string"
    )
    def test_extract_text_handles_ocr_exception(
        self,
        mock_image_to_string,
        mock_preprocess,
    ):
        mock_preprocess.return_value = object()

        mock_image_to_string.side_effect = (
            RuntimeError("OCR failure")
        )

        service = OCRService()
        service.available = True

        result = service.extract_text(
            self.image_path
        )

        self.assertFalse(
            result["success"]
        )

        self.assertEqual(
            result["text"],
            "",
        )

        self.assertIn(
            "OCR failure",
            result["error"],
        )

    def test_backward_compatible_availability_function_exists(self):
        self.assertTrue(
            callable(check_tesseract_available)
        )

    def test_backward_compatible_ocr_function_exists(self):
        self.assertTrue(
            callable(perform_ocr_on_image)
        )


if __name__ == "__main__":
    unittest.main()