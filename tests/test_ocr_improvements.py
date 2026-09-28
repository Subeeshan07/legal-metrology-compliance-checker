"""
Tests for Phase 3: OCR and Image Quality Improvements.
"""

import unittest
from PIL import Image, ImageDraw
import numpy as np

from services.image_quality_service import ImageQualityAssessmentService
from utils.image_preprocessing import (
    convert_to_grayscale,
    resize_for_ocr,
    enhance_contrast,
    apply_otsu_threshold,
    preprocess_image_pipeline,
)
from services.ocr_service import (
    BaseOCREngine,
    TesseractOCREngine,
    OCRService,
)


class DummyCustomEngine(BaseOCREngine):
    engine_name = "MockEngine"

    def check_availability(self) -> bool:
        return True

    def extract_text_and_confidence(self, processed_image):
        return {
            "text": "MOCK RECOGNIZED TEXT",
            "confidence": 98.5,
            "word_confidences": [{"word": "MOCK", "confidence": 98.5}],
            "source": "Mock Custom Engine",
        }


class TestOCRImprovements(unittest.TestCase):

    def test_image_quality_service_good_image(self):
        # Create clear sharp image with realistic label background
        img = Image.new("RGB", (800, 600), color="#f1f5f9")
        draw = ImageDraw.Draw(img)
        draw.text((100, 100), "SAMPLE SHARP HIGH RESOLUTION TEXT", fill="#000000")


        report = ImageQualityAssessmentService.evaluate_image(img)
        self.assertIn("quality_score", report)
        self.assertIn("quality_grade", report)
        self.assertFalse(report["is_low_resolution"])
        self.assertEqual(report["lighting_quality"], "GOOD")
        self.assertFalse(report["has_glare"])

    def test_image_quality_service_low_resolution(self):
        small_img = Image.new("RGB", (200, 150), color="#ffffff")
        report = ImageQualityAssessmentService.evaluate_image(small_img)
        self.assertTrue(report["is_low_resolution"])
        self.assertIn("Low image resolution", " ".join(report["warnings"]))

    def test_image_quality_service_dark_image(self):
        dark_img = Image.new("RGB", (800, 600), color="#101010")
        report = ImageQualityAssessmentService.evaluate_image(dark_img)
        self.assertEqual(report["lighting_quality"], "UNDEREXPOSED")

    def test_preprocessing_pipeline(self):
        img = Image.new("RGB", (500, 300), color="#808080")
        processed = preprocess_image_pipeline(img, target_min_width=1000, binarize=True)
        self.assertGreaterEqual(processed.size[0], 1000)
        self.assertEqual(processed.mode, "L")

    def test_otsu_thresholding(self):
        # Gradient image
        arr = np.linspace(0, 255, 256, dtype=np.uint8).repeat(256).reshape((256, 256))
        img = Image.fromarray(arr, mode="L")
        binarized = apply_otsu_threshold(img)
        self.assertEqual(binarized.mode, "L")
        unique_vals = set(np.array(binarized).flatten())
        self.assertTrue(unique_vals.issubset({0, 255}))

    def test_ocr_engine_abstraction_pluggable(self):
        custom_engine = DummyCustomEngine()
        service = OCRService(engine=custom_engine)
        self.assertTrue(service.check_availability())

        # Test extraction with custom engine
        dummy_img = Image.new("RGB", (200, 200), color="#ffffff")
        res = custom_engine.extract_text_and_confidence(dummy_img)
        self.assertEqual(res["text"], "MOCK RECOGNIZED TEXT")
        self.assertEqual(res["confidence"], 98.5)


if __name__ == "__main__":
    unittest.main()
