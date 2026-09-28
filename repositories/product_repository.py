"""
Product dataset repository.

This module contains persistence operations for the Legal Metrology
product dataset.

The current persistence backend remains the existing CSV file.
"""

import logging
import os

import pandas as pd

from config.settings import Config


logger = logging.getLogger(__name__)

DATASET_PATH = Config.DATASET_PATH


def load_dataset():
    """
    Load the Legal Metrology product dataset from the configured CSV file.

    Returns an empty DataFrame when the dataset does not exist or cannot
    be loaded. This preserves the behavior of the original prototype.
    """
    if not os.path.isfile(DATASET_PATH):
        logger.warning("Dataset CSV not found. Returning empty DataFrame.")
        return pd.DataFrame()

    try:
        return pd.read_csv(DATASET_PATH, encoding="utf-8")
    except Exception as e:
        logger.error(f"Error loading CSV dataset: {e}")
        return pd.DataFrame()


def save_record_to_dataset(record_dict):
    """
    Save a newly scanned product record to the CSV dataset.

    New records are inserted before existing records to preserve the
    behavior of the original prototype.
    """
    df = load_dataset()
    new_df = pd.DataFrame([record_dict])

    if df.empty:
        updated_df = new_df
    else:
        updated_df = pd.concat([new_df, df], ignore_index=True)

    updated_df.to_csv(DATASET_PATH, index=False, encoding="utf-8")
    return True