"""
Database-backed persistence repository using SQLite.

Manages persistent entities for scans, products, compliance results,
and counterfeit evaluations with automated CSV migration and synchronization.
"""

import os
import sqlite3
import logging
import json
import contextlib
from typing import Dict, Any, List, Optional
import pandas as pd

from config.settings import Config

logger = logging.getLogger(__name__)


class DatabaseRepository:

    def __init__(self, db_path: Optional[str] = None, csv_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.csv_path = csv_path or Config.DATASET_PATH
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()
        self._auto_migrate_from_csv_if_needed()

    @contextlib.contextmanager
    def _get_connection(self):
        """Context manager that ensures the SQLite connection is always closed."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Creates database schema if tables do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    product_name TEXT,
                    category TEXT,
                    manufacturer TEXT,
                    net_quantity TEXT,
                    mrp TEXT,
                    mfg_date TEXT,
                    consumer_care TEXT,
                    country_of_origin TEXT,
                    compliance_status TEXT,
                    violations TEXT,
                    scanned_timestamp TEXT,
                    ocr_confidence TEXT
                )
            """)

            # 2. Scans audit table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    scan_id TEXT PRIMARY KEY,
                    product_id TEXT,
                    image_url TEXT,
                    ocr_text TEXT,
                    ocr_confidence TEXT,
                    compliance_status TEXT,
                    counterfeit_risk TEXT,
                    risk_score REAL,
                    quality_grade TEXT,
                    timestamp TEXT,
                    report_json TEXT
                )
            """)
            conn.commit()

    def _auto_migrate_from_csv_if_needed(self):
        """Migrates records from the prototype CSV if the database is newly initialized."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM products")
                count = cursor.fetchone()[0]
                if count > 0:
                    return

            if os.path.isfile(self.csv_path):
                df = pd.read_csv(self.csv_path, encoding="utf-8")
                if not df.empty:
                    with self._get_connection() as conn:
                        df.to_sql("products", conn, if_exists="append", index=False)
                    logger.info(f"Auto-migrated {len(df)} records from {self.csv_path} to SQLite database.")
        except Exception as e:
            logger.warning(f"CSV database migration warning: {e}")

    def load_dataset(self) -> pd.DataFrame:
        """
        Loads the complete product dataset as a pandas DataFrame.
        Maintains complete backward compatibility with the existing prototype.
        """
        try:
            with self._get_connection() as conn:
                return pd.read_sql("SELECT * FROM products ORDER BY rowid DESC", conn)
        except Exception as e:
            logger.error(f"Error loading dataset from SQLite: {e}")
            if os.path.isfile(self.csv_path):
                return pd.read_csv(self.csv_path, encoding="utf-8")
            return pd.DataFrame()

    def save_record_to_dataset(self, record_dict: Dict[str, Any]) -> bool:
        """
        Appends a newly scanned product record to SQLite and mirrors to CSV.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO products (
                        id, product_name, category, manufacturer, net_quantity, mrp,
                        mfg_date, consumer_care, country_of_origin, compliance_status,
                        violations, scanned_timestamp, ocr_confidence
                    ) VALUES (
                        :id, :product_name, :category, :manufacturer, :net_quantity, :mrp,
                        :mfg_date, :consumer_care, :country_of_origin, :compliance_status,
                        :violations, :scanned_timestamp, :ocr_confidence
                    )
                """, {
                    "id": record_dict.get("id"),
                    "product_name": record_dict.get("product_name", "Unlabeled Product"),
                    "category": record_dict.get("category", "Packaged Food"),
                    "manufacturer": record_dict.get("manufacturer", "Not Declared"),
                    "net_quantity": record_dict.get("net_quantity", "Not Declared"),
                    "mrp": record_dict.get("mrp", "Not Declared"),
                    "mfg_date": record_dict.get("mfg_date", "Not Declared"),
                    "consumer_care": record_dict.get("consumer_care", "Not Declared"),
                    "country_of_origin": record_dict.get("country_of_origin", "Not Declared"),
                    "compliance_status": record_dict.get("compliance_status", "NEEDS REVIEW"),
                    "violations": record_dict.get("violations", "None"),
                    "scanned_timestamp": record_dict.get("scanned_timestamp", ""),
                    "ocr_confidence": record_dict.get("ocr_confidence", "95%"),
                })
                conn.commit()

            # Mirror to CSV to guarantee file-based consumers and legacy tests remain intact
            if os.path.isfile(self.csv_path):
                try:
                    df = pd.read_csv(self.csv_path, encoding="utf-8")
                    new_df = pd.DataFrame([record_dict])
                    updated_df = pd.concat([new_df, df], ignore_index=True) if not df.empty else new_df
                    updated_df.to_csv(self.csv_path, index=False, encoding="utf-8")
                except Exception as csv_err:
                    logger.warning(f"Error mirroring record to CSV: {csv_err}")

            return True
        except Exception as e:
            logger.error(f"Error saving product record: {e}")
            return False

    def save_product_record(self, record_dict: Dict[str, Any]) -> bool:
        """Saves or updates a product record directly in SQLite."""
        return self.save_record_to_dataset(record_dict)

    def save_scan_audit(self, scan_data: Dict[str, Any]) -> bool:
        """
        Saves full scan audit log with both legal metrology and counterfeit findings.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO scans (
                        scan_id, product_id, image_url, ocr_text, ocr_confidence,
                        compliance_status, counterfeit_risk, risk_score,
                        quality_grade, timestamp, report_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_data.get("scan_id"),
                    scan_data.get("product_id"),
                    scan_data.get("image_url"),
                    scan_data.get("ocr_text"),
                    scan_data.get("ocr_confidence"),
                    scan_data.get("compliance_status"),
                    scan_data.get("counterfeit_risk"),
                    scan_data.get("risk_score", 0.0),
                    scan_data.get("quality_grade"),
                    scan_data.get("timestamp"),
                    json.dumps(scan_data.get("report", {})),
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving scan audit: {e}")
            return False

    def get_scan(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific scan by scan_id."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
                row = cursor.fetchone()
                if row:
                    item = dict(row)
                    if item.get("report_json"):
                        try:
                            item["report"] = json.loads(item["report_json"])
                        except Exception:
                            item["report"] = {}
                    return item
                return None
        except Exception as e:
            logger.error(f"Error getting scan: {e}")
            return None

    def list_scans(self, limit: int = 50, offset: int = 0, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns paginated scan history."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if search:
                    query = """
                        SELECT * FROM scans 
                        WHERE scan_id LIKE ? OR product_id LIKE ? OR compliance_status LIKE ? OR counterfeit_risk LIKE ?
                        ORDER BY rowid DESC LIMIT ? OFFSET ?
                    """
                    pattern = f"%{search}%"
                    cursor.execute(query, (pattern, pattern, pattern, pattern, limit, offset))
                else:
                    query = "SELECT * FROM scans ORDER BY rowid DESC LIMIT ? OFFSET ?"
                    cursor.execute(query, (limit, offset))
                
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    item = dict(row)
                    if item.get("report_json"):
                        try:
                            item["report"] = json.loads(item["report_json"])
                        except Exception:
                            item["report"] = {}
                    results.append(item)
                return results
        except Exception as e:
            logger.error(f"Error listing scans: {e}")
            return []


# Singleton database repository instance
db_repository = DatabaseRepository()
