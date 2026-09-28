"""
Tests for sample label generation service.
"""

import os
import tempfile
import unittest
from services.sample_service import (
    SAMPLE_DEFINITIONS,
    ensure_sample_labels,
    render_label_image,
)


class TestSampleService(unittest.TestCase):

    def test_sample_definitions_exist(self):
        self.assertGreaterEqual(len(SAMPLE_DEFINITIONS), 3)
        sample_ids = [s["sample_id"] for s in SAMPLE_DEFINITIONS]
        self.assertIn("compliant", sample_ids)
        self.assertIn("non_compliant", sample_ids)
        self.assertIn("needs_review", sample_ids)

    def test_render_label_image_creates_valid_image(self):
        definition = SAMPLE_DEFINITIONS[0]
        img = render_label_image(definition)
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (700, 480))
        self.assertEqual(img.mode, "RGB")

    def test_ensure_sample_labels_writes_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            created = ensure_sample_labels(samples_folder=temp_dir, force=True)
            self.assertEqual(len(created), len(SAMPLE_DEFINITIONS))
            for path in created:
                self.assertTrue(os.path.isfile(path))
                self.assertGreater(os.path.getsize(path), 0)

    def test_ensure_sample_labels_skips_existing_unless_forced(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first_run = ensure_sample_labels(samples_folder=temp_dir)
            self.assertEqual(len(first_run), len(SAMPLE_DEFINITIONS))

            # Second run without force should not recreate
            second_run = ensure_sample_labels(samples_folder=temp_dir, force=False)
            self.assertEqual(len(second_run), 0)


if __name__ == "__main__":
    unittest.main()
