"""
Declaration Normalization Service for Legal Metrology.

Normalizes extracted entity variants into standardized numerical,
temporal, and categorical data representations while preserving raw OCR evidence.
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime


STANDARD_UNITS = {
    "weight": {"g", "kg", "mg"},
    "volume": {"ml", "l", "cl"},
    "length": {"m", "cm", "mm"},
    "count": {"n", "u", "pcs", "pieces"},
}

ALL_STANDARD_UNITS = {u for category in STANDARD_UNITS.values() for u in category}

NON_STANDARD_UNIT_MAPPING = {
    "gm": "g",
    "gms": "g",
    "gram": "g",
    "grams": "g",
    "kilo": "kg",
    "kilos": "kg",
    "ml.": "ml",
    "millilitres": "ml",
    "milliliters": "ml",
    "ltr": "l",
    "ltrs": "l",
    "liter": "l",
    "litres": "l",
    "liters": "l",
    "unit": "n",
    "units": "n",
    "piece": "pcs",
    "nos": "n",
    "no": "n",
}

MONTH_NAMES = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def normalize_quantity(qty_str: Optional[str]) -> Dict[str, Any]:
    """
    Normalizes a net quantity string into structured numerical value and unit.
    """
    if not qty_str or qty_str.strip().lower() in ["not declared", "none", ""]:
        return {
            "raw": qty_str or "",
            "value": None,
            "unit": None,
            "is_standard_unit": False,
            "standard_unit": None,
            "declared": False,
        }

    raw = qty_str.strip()
    match = re.search(r"(\d+(?:\.\d+)?)\s*([a-zA-Z\.]+)", raw)
    if not match:
        return {
            "raw": raw,
            "value": None,
            "unit": None,
            "is_standard_unit": False,
            "standard_unit": None,
            "declared": True,
        }

    val = float(match.group(1))
    unit_raw = match.group(2).lower().rstrip(".")
    is_standard = unit_raw in ALL_STANDARD_UNITS
    std_unit = unit_raw if is_standard else NON_STANDARD_UNIT_MAPPING.get(unit_raw, unit_raw)

    return {
        "raw": raw,
        "value": val,
        "unit": unit_raw,
        "is_standard_unit": is_standard,
        "standard_unit": std_unit,
        "declared": True,
    }


def normalize_price(mrp_str: Optional[str]) -> Dict[str, Any]:
    """
    Normalizes a maximum retail price string into numerical amount and tax clause status.
    """
    if not mrp_str or mrp_str.strip().lower() in ["not declared", "none", ""]:
        return {
            "raw": mrp_str or "",
            "amount": None,
            "currency": "INR",
            "has_tax_clause": False,
            "declared": False,
        }

    raw = mrp_str.strip()
    amount_match = re.search(r"(?:Rs\.?|INR|₹)?\s*(\d+(?:\.\d{1,2})?)", raw, re.IGNORECASE)
    amount = float(amount_match.group(1)) if amount_match else None

    # Check mandatory tax clause Rule 6(1)(da)
    tax_clause_pattern = r"(?:incl(?:usive|\.)?\s*of\s*all\s*taxes|incl\.\s*taxes|incl\s*taxes)"
    has_tax_clause = bool(re.search(tax_clause_pattern, raw, re.IGNORECASE))

    return {
        "raw": raw,
        "amount": amount,
        "currency": "INR",
        "has_tax_clause": has_tax_clause,
        "declared": amount is not None,
    }


def normalize_date(date_str: Optional[str]) -> Dict[str, Any]:
    """
    Extracts and standardizes month and year from messy packaging text like
    'Packed during 06/2026', 'Mfg Date: May 2026', or '04-2026'.
    """
    if not date_str or date_str.strip().lower() in ["not declared", "none", ""]:
        return {
            "raw": date_str or "",
            "month": None,
            "year": None,
            "formatted": None,
            "declared": False,
            "is_valid": False,
        }

    raw = date_str.strip()

    # Match numeric MM/YYYY or MM-YYYY
    num_match = re.search(r"\b(0?[1-9]|1[0-2])[\/\-](20\d\d)\b", raw)
    if num_match:
        m = int(num_match.group(1))
        y = int(num_match.group(2))
        return {
            "raw": raw,
            "month": m,
            "year": y,
            "formatted": f"{m:02d}/{y}",
            "declared": True,
            "is_valid": True,
        }

    # Match textual Month YYYY (e.g., 'May 2026', 'April 2025')
    text_match = re.search(r"\b([A-Za-z]{3,9})\s+[\/\-]?\s*(20\d\d)\b", raw)
    if text_match:
        m_name = text_match.group(1).lower()
        if m_name in MONTH_NAMES:
            m = MONTH_NAMES[m_name]
            y = int(text_match.group(2))
            return {
                "raw": raw,
                "month": m,
                "year": y,
                "formatted": f"{m:02d}/{y}",
                "declared": True,
                "is_valid": True,
            }

    # Fallback year only
    year_match = re.search(r"\b(20\d\d)\b", raw)
    if year_match:
        return {
            "raw": raw,
            "month": None,
            "year": int(year_match.group(1)),
            "formatted": year_match.group(1),
            "declared": True,
            "is_valid": False,
        }

    return {
        "raw": raw,
        "month": None,
        "year": None,
        "formatted": None,
        "declared": False,
        "is_valid": False,
    }


def normalize_country(country_str: Optional[str]) -> Dict[str, Any]:
    """
    Standardizes country of origin name.
    """
    if not country_str or country_str.strip().lower() in ["not declared", "none", ""]:
        return {
            "raw": country_str or "",
            "standardized": None,
            "declared": False,
        }

    raw = country_str.strip()
    raw_lower = raw.lower()
    if "india" in raw_lower:
        standardized = "India"
    else:
        standardized = raw.title()

    return {
        "raw": raw,
        "standardized": standardized,
        "declared": True,
    }


def normalize_declarations(entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes all extracted packaging declarations into structured data.
    """
    return {
        "quantity": normalize_quantity(entities.get("net_quantity")),
        "mrp": normalize_price(entities.get("mrp")),
        "mfg_date": normalize_date(entities.get("mfg_date")),
        "country": normalize_country(entities.get("country_of_origin")),
        "manufacturer": {
            "raw": entities.get("manufacturer", ""),
            "declared": bool(entities.get("manufacturer") and entities.get("manufacturer").lower() not in ["not declared", "none", ""]),
        },
        "product_name": {
            "raw": entities.get("product_name", ""),
            "declared": bool(entities.get("product_name") and entities.get("product_name").lower() not in ["not declared", "none", ""]),
        },
        "consumer_care": {
            "raw": entities.get("consumer_care", ""),
            "declared": bool(entities.get("consumer_care") and entities.get("consumer_care").lower() not in ["not declared", "none", ""]),
        },
    }
