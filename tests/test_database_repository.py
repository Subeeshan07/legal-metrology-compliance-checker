"""
Tests for Phase 6: Database Repository and Persistence Layer.
"""

import os
import tempfile
import unittest
import pandas as pd
from repositories.database_repository import DatabaseRepository


class TestDatabaseRepository(unittest.TestCase):

    def test_database_initialization_and_crud(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            csv_path = os.path.join(temp_dir, "test.csv")

            # Create an empty CSV
            pd.DataFrame(columns=["id", "product_name"]).to_csv(csv_path, index=False)

            repo = DatabaseRepository(db_path=db_path, csv_path=csv_path)

            # Insert a record
            record = {
                "id": "TEST-DB-001",
                "product_name": "Test Atta",
                "category": "Flour",
                "compliance_status": "COMPLIANT",
            }
            success = repo.save_record_to_dataset(record)
            self.assertTrue(success)

            # Query back
            df = repo.load_dataset()
            self.assertEqual(len(df), 1)
            self.assertEqual(df.iloc[0]["id"], "TEST-DB-001")

            # Verify CSV synchronization
            csv_df = pd.read_csv(csv_path)
            self.assertEqual(len(csv_df), 1)
            self.assertEqual(csv_df.iloc[0]["id"], "TEST-DB-001")

    def test_save_scan_audit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            csv_path = os.path.join(temp_dir, "test.csv")

            repo = DatabaseRepository(db_path=db_path, csv_path=csv_path)

            scan_audit = {
                "scan_id": "SCAN-12345",
                "product_id": "TEST-DB-001",
                "image_url": "/uploads/test.png",
                "ocr_text": "Sample text",
                "ocr_confidence": "94.5%",
                "compliance_status": "COMPLIANT",
                "counterfeit_risk": "LOW",
                "risk_score": 10.0,
                "quality_grade": "EXCELLENT",
                "timestamp": "2026-09-28 12:00:00",
                "report": {"verdict": "COMPLIANT"},
            }
            saved = repo.save_scan_audit(scan_audit)
            self.assertTrue(saved)


if __name__ == "__main__":
    unittest.main()
