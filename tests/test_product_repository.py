import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from repositories.product_repository import (
    load_dataset,
    save_record_to_dataset,
)


class TestProductRepository(unittest.TestCase):

    def test_load_dataset_returns_dataframe(self):
        dataset = load_dataset()

        self.assertIsInstance(dataset, pd.DataFrame)

    def test_load_existing_dataset(self):
        dataset = load_dataset()

        self.assertFalse(dataset.empty)

    def test_load_dataset_when_file_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = os.path.join(
                temp_dir,
                "missing_dataset.csv",
            )

            with patch(
                "repositories.product_repository.DATASET_PATH",
                missing_path,
            ):
                dataset = load_dataset()

            self.assertIsInstance(dataset, pd.DataFrame)
            self.assertTrue(dataset.empty)

    def test_load_dataset_when_csv_is_invalid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = os.path.join(
                temp_dir,
                "invalid_dataset.csv",
            )

            with open(
                invalid_path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(b"\xff\xfe\x00".decode("latin1"))

            with patch(
                "repositories.product_repository.DATASET_PATH",
                invalid_path,
            ):
                dataset = load_dataset()

            self.assertIsInstance(dataset, pd.DataFrame)
            self.assertTrue(dataset.empty)

    def test_save_record_creates_new_dataset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_path = os.path.join(
                temp_dir,
                "dataset.csv",
            )

            record = {
                "id": "TEST-001",
                "product_name": "Test Product",
                "category": "Test",
                "compliance_status": "COMPLIANT",
            }

            with patch(
                "repositories.product_repository.DATASET_PATH",
                dataset_path,
            ):
                result = save_record_to_dataset(record)

            saved_dataset = pd.read_csv(dataset_path)

            self.assertTrue(result)
            self.assertEqual(len(saved_dataset), 1)
            self.assertEqual(
                saved_dataset.iloc[0]["id"],
                "TEST-001",
            )

    def test_save_record_preserves_existing_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_path = os.path.join(
                temp_dir,
                "dataset.csv",
            )

            existing_dataset = pd.DataFrame([
                {
                    "id": "OLD-001",
                    "product_name": "Existing Product",
                    "category": "Existing",
                    "compliance_status": "COMPLIANT",
                }
            ])

            existing_dataset.to_csv(
                dataset_path,
                index=False,
                encoding="utf-8",
            )

            new_record = {
                "id": "NEW-001",
                "product_name": "New Product",
                "category": "New",
                "compliance_status": "NON-COMPLIANT",
            }

            with patch(
                "repositories.product_repository.DATASET_PATH",
                dataset_path,
            ):
                result = save_record_to_dataset(new_record)

            saved_dataset = pd.read_csv(dataset_path)

            self.assertTrue(result)
            self.assertEqual(len(saved_dataset), 2)

            self.assertIn(
                "OLD-001",
                saved_dataset["id"].values,
            )

            self.assertIn(
                "NEW-001",
                saved_dataset["id"].values,
            )

    def test_new_record_is_inserted_first(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_path = os.path.join(
                temp_dir,
                "dataset.csv",
            )

            existing_dataset = pd.DataFrame([
                {
                    "id": "OLD-001",
                    "product_name": "Existing Product",
                }
            ])

            existing_dataset.to_csv(
                dataset_path,
                index=False,
                encoding="utf-8",
            )

            new_record = {
                "id": "NEW-001",
                "product_name": "New Product",
            }

            with patch(
                "repositories.product_repository.DATASET_PATH",
                dataset_path,
            ):
                save_record_to_dataset(new_record)

            saved_dataset = pd.read_csv(dataset_path)

            self.assertEqual(
                saved_dataset.iloc[0]["id"],
                "NEW-001",
            )

            self.assertEqual(
                saved_dataset.iloc[1]["id"],
                "OLD-001",
            )


if __name__ == "__main__":
    unittest.main()