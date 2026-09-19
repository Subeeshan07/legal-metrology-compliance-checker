"""
Unit tests for reusable image-processing utilities.

Task 1.3 — Utility Extraction
"""

import os
import tempfile
import unittest

from PIL import Image

from utils.image_utils import preprocess_image_for_ocr


class TestImageUtils(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_image(
        self,
        filename,
        size=(500, 250),
        mode="RGB",
    ):
        path = os.path.join(
            self.temp_dir.name,
            filename,
        )

        if mode == "RGBA":
            color = (255, 255, 255, 255)
        else:
            color = "white"

        image = Image.new(
            mode,
            size,
            color=color,
        )

        image.save(path)

        return path

    def test_small_image_is_upscaled_to_minimum_width(self):
        path = self._create_image(
            "small.png",
            size=(500, 250),
        )

        processed = preprocess_image_for_ocr(path)

        self.assertEqual(
            processed.width,
            1000,
        )

        self.assertEqual(
            processed.height,
            500,
        )

    def test_large_image_is_not_resized(self):
        path = self._create_image(
            "large.png",
            size=(1200, 600),
        )

        processed = preprocess_image_for_ocr(path)

        self.assertEqual(
            processed.size,
            (1200, 600),
        )

    def test_processed_image_is_grayscale(self):
        path = self._create_image(
            "rgb.png",
        )

        processed = preprocess_image_for_ocr(path)

        self.assertEqual(
            processed.mode,
            "L",
        )

    def test_rgba_image_can_be_processed(self):
        path = self._create_image(
            "rgba.png",
            mode="RGBA",
        )

        processed = preprocess_image_for_ocr(path)

        self.assertEqual(
            processed.mode,
            "L",
        )

        self.assertEqual(
            processed.width,
            1000,
        )

    def test_custom_minimum_width_is_supported(self):
        path = self._create_image(
            "custom.png",
            size=(300, 150),
        )

        processed = preprocess_image_for_ocr(
            path,
            min_width=600,
        )

        self.assertEqual(
            processed.size,
            (600, 300),
        )


if __name__ == "__main__":
    unittest.main()