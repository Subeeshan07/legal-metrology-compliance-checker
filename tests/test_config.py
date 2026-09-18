"""
Tests for centralized application configuration.

Task 1.2 — Configuration Extraction
"""

import os
import unittest
from unittest.mock import patch

from config.settings import Config, detect_tesseract_command, resolve_path


class TestConfiguration(unittest.TestCase):

    def test_upload_folder_is_absolute(self):
        self.assertTrue(os.path.isabs(Config.UPLOAD_FOLDER))

    def test_samples_folder_is_absolute(self):
        self.assertTrue(os.path.isabs(Config.SAMPLES_FOLDER))

    def test_dataset_path_is_absolute(self):
        self.assertTrue(os.path.isabs(Config.DATASET_PATH))

    def test_default_upload_limit_is_16_mb(self):
        self.assertEqual(
            Config.MAX_CONTENT_LENGTH,
            16 * 1024 * 1024,
        )

    def test_allowed_configured_tesseract_command(self):
        configured_path = r"C:\custom\tesseract.exe"

        with patch.dict(
            os.environ,
            {"TESSERACT_CMD": configured_path},
        ):
            result = detect_tesseract_command()

        self.assertEqual(result, configured_path)

    def test_relative_path_is_resolved_to_absolute_path(self):
        result = resolve_path("uploads", "fallback")

        self.assertTrue(os.path.isabs(result))
        self.assertTrue(result.endswith("uploads"))


if __name__ == "__main__":
    unittest.main()
