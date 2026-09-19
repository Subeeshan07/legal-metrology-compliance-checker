"""
Unit tests for reusable file utilities.

Task 1.3 — Utility Extraction
"""

import unittest

from utils.file_utils import (
    ALLOWED_IMAGE_EXTENSIONS,
    allowed_file,
    get_file_extension,
)


class TestFileUtils(unittest.TestCase):

    def test_allowed_image_extensions(self):
        for filename in [
            "label.png",
            "label.jpg",
            "label.jpeg",
            "label.webp",
            "label.bmp",
            "label.tiff",
        ]:
            with self.subTest(filename=filename):
                self.assertTrue(allowed_file(filename))

    def test_uppercase_extension_is_allowed(self):
        self.assertTrue(allowed_file("PRODUCT.JPG"))
        self.assertTrue(allowed_file("LABEL.PNG"))

    def test_disallowed_extension_is_rejected(self):
        self.assertFalse(allowed_file("malware.exe"))
        self.assertFalse(allowed_file("document.pdf"))
        self.assertFalse(allowed_file("archive.zip"))

    def test_filename_without_extension_is_rejected(self):
        self.assertFalse(allowed_file("product_label"))

    def test_empty_filename_is_rejected(self):
        self.assertFalse(allowed_file(""))
        self.assertFalse(allowed_file(None))

    def test_get_file_extension(self):
        self.assertEqual(
            get_file_extension("product.JPEG"),
            "jpeg",
        )

    def test_custom_allowed_extensions(self):
        self.assertTrue(
            allowed_file(
                "report.pdf",
                {"pdf"},
            )
        )

    def test_default_extension_set_contains_expected_formats(self):
        self.assertEqual(
            ALLOWED_IMAGE_EXTENSIONS,
            {
                "png",
                "jpg",
                "jpeg",
                "webp",
                "bmp",
                "tiff",
            },
        )


if __name__ == "__main__":
    unittest.main()