"""
Product domain models for extracted packaging information and dataset records.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ExtractedProduct:
    product_name: str = ""
    manufacturer: str = ""
    net_quantity: str = ""
    mrp: str = ""
    mfg_date: str = ""
    consumer_care: str = ""
    country_of_origin: str = ""
    raw_text: str = ""
    normalized_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_name": self.product_name,
            "manufacturer": self.manufacturer,
            "net_quantity": self.net_quantity,
            "mrp": self.mrp,
            "mfg_date": self.mfg_date,
            "consumer_care": self.consumer_care,
            "country_of_origin": self.country_of_origin,
            "raw_text": self.raw_text,
            "normalized_fields": self.normalized_fields,
        }


@dataclass
class ProductRecord:
    id: str
    product_name: str
    category: str
    manufacturer: str
    net_quantity: str
    mrp: str
    mfg_date: str
    consumer_care: str
    country_of_origin: str
    compliance_status: str
    violations: str
    scanned_timestamp: str
    ocr_confidence: str = "95%"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "product_name": self.product_name,
            "category": self.category,
            "manufacturer": self.manufacturer,
            "net_quantity": self.net_quantity,
            "mrp": self.mrp,
            "mfg_date": self.mfg_date,
            "consumer_care": self.consumer_care,
            "country_of_origin": self.country_of_origin,
            "compliance_status": self.compliance_status,
            "violations": self.violations,
            "scanned_timestamp": self.scanned_timestamp,
            "ocr_confidence": self.ocr_confidence,
        }
