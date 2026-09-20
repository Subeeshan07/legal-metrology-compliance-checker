"""
Entity Extraction Service

Responsible for converting OCR/manual label text into structured
packaged-commodity declaration fields.

Task 1.5 intentionally preserves the extraction behaviour of the
original Flask prototype. Extraction improvements will be handled
separately after the architecture refactor is stable.
"""

import re


def extract_entities_from_text(raw_text):
    """
    Parse OCR/manual label text using targeted regular expressions
    and heuristic extraction.

    Returns the mandatory packaged commodity declaration fields
    currently supported by the application.
    """

    lines = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    ]

    cleaned_text = " \n ".join(lines)

    extracted = {
        "product_name": "",
        "manufacturer": "",
        "net_quantity": "",
        "mrp": "",
        "mfg_date": "",
        "consumer_care": "",
        "country_of_origin": "",
        "raw_text": raw_text,
    }

    # ------------------------------------------------------------------
    # 1. Net Quantity
    # ------------------------------------------------------------------
    # Matches examples such as:
    # Net Qty: 500 g
    # Net Wt. 1 kg
    # Net Content: 250 g
    # Net Quantity: 200 gms

    net_qty_match = re.search(
        r"(?:Net\s*(?:Quantity|Qty|Content|Wt|Weight)?[:\s\-]*)"
        r"\s*(\d+(?:\.\d+)?\s*"
        r"(?:kg|g|gm|gms|ml|l|ltr|litres?|units?|pieces?|pcs|n))\b",
        cleaned_text,
        re.IGNORECASE,
    )

    if net_qty_match:
        extracted["net_quantity"] = net_qty_match.group(1).strip()

    else:
        # Fallback standalone quantity search
        fallback_qty = re.search(
            r"\b(\d+(?:\.\d+)?\s*(?:kg|gms?|ml|ltr|litres?))\b",
            cleaned_text,
            re.IGNORECASE,
        )

        if fallback_qty:
            extracted["net_quantity"] = fallback_qty.group(1).strip()

    # ------------------------------------------------------------------
    # 2. Maximum Retail Price (MRP)
    # ------------------------------------------------------------------

    mrp_match = re.search(
        r"(?:M\.?R\.?P\.?|Maximum\s*Retail\s*Price)"
        r"[:\s\-]*([^\n\r]+)",
        cleaned_text,
        re.IGNORECASE,
    )

    if mrp_match:
        mrp_line = mrp_match.group(0).strip()
        mrp_cleaned = re.sub(r"\s+", " ", mrp_line)
        extracted["mrp"] = mrp_cleaned

    else:
        # Fallback standalone currency search
        standalone_mrp = re.search(
            r"(?:Rs\.?|INR|₹)\s*"
            r"(\d+(?:\.\d{2})?)\s*"
            r"(\([^\)]*\))?",
            cleaned_text,
            re.IGNORECASE,
        )

        if standalone_mrp:
            extracted["mrp"] = (
                f"MRP {standalone_mrp.group(0).strip()}"
            )

    # ------------------------------------------------------------------
    # 3. Manufacturing / Packing Date
    # ------------------------------------------------------------------

    mfg_match = re.search(
        r"(?:Mfg(?:\s*Date)?|Date\s*of\s*Mfg|"
        r"Date\s*of\s*Packing|PKD|Packed|Manufactured|"
        r"Batch\s*Date)"
        r"[:\s\-]*([A-Za-z0-9\/\-\. ]{4,15})",
        cleaned_text,
        re.IGNORECASE,
    )

    if mfg_match:
        extracted["mfg_date"] = mfg_match.group(1).strip()

    else:
        # Fallback MM/YYYY or MM-YYYY
        dt_fallback = re.search(
            r"\b(0[1-9]|1[0-2])[\/\-]"
            r"(202[0-9]|20[2-9][0-9])\b",
            cleaned_text,
        )

        if dt_fallback:
            extracted["mfg_date"] = (
                dt_fallback.group(0).strip()
            )

    # ------------------------------------------------------------------
    # 4. Consumer Care Details
    # ------------------------------------------------------------------

    cc_match = re.search(
        r"(?:Consumer\s*Care|Customer\s*Care|Helpline|"
        r"Feedback|Consumer\s*Cell|Contact\s*Us)"
        r"[:\s\-]*([^\n]+(?:\n[^\n]+)?)",
        cleaned_text,
        re.IGNORECASE,
    )

    if cc_match:
        extracted["consumer_care"] = re.sub(
            r"\s+",
            " ",
            cc_match.group(0).strip(),
        )

    else:
        # Fallback to email / telephone detection
        email_match = re.search(
            r"[\w\.-]+@[\w\.-]+\.\w+",
            cleaned_text,
        )

        phone_match = re.search(
            r"(?:1800[- ]?\d{3}[- ]?\d{3,4}|"
            r"\+?91[- ]?\d{10}|"
            r"\b\d{10}\b)",
            cleaned_text,
        )

        cc_parts = []

        if email_match:
            cc_parts.append(
                f"Email: {email_match.group(0)}"
            )

        if phone_match:
            cc_parts.append(
                f"Ph: {phone_match.group(0)}"
            )

        if cc_parts:
            extracted["consumer_care"] = " | ".join(
                cc_parts
            )

    # ------------------------------------------------------------------
    # 5. Manufacturer / Packer / Marketer
    # ------------------------------------------------------------------

    mfr_match = re.search(
        r"(?:Manufactured\s*by|Packed\s*by|"
        r"Marketed\s*by|Mfg\s*by|Mfd\s*by|"
        r"Produced\s*by)"
        r"[:\s\-]*([^\n]+(?:\n[^\n]+)?)",
        cleaned_text,
        re.IGNORECASE,
    )

    if mfr_match:
        extracted["manufacturer"] = re.sub(
            r"\s+",
            " ",
            mfr_match.group(1).strip(),
        )

    else:
        # Fallback company-name heuristic
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in [
                    "ltd",
                    "pvt",
                    "industries",
                    "foods",
                    "agro",
                    "llp",
                    "mills",
                ]
            ):
                extracted["manufacturer"] = line.strip()
                break

    # ------------------------------------------------------------------
    # 6. Country of Origin
    # ------------------------------------------------------------------

    origin_match = re.search(
        r"(?:Country\s*of\s*Origin|Made\s*in|Product\s*of)"
        r"[:\s\-]*([A-Za-z\s]+)",
        cleaned_text,
        re.IGNORECASE,
    )

    if origin_match:
        extracted["country_of_origin"] = (
            origin_match.group(1).strip()
        )

    elif (
        "made in india" in cleaned_text.lower()
        or "origin: india" in cleaned_text.lower()
    ):
        extracted["country_of_origin"] = "India"

    # ------------------------------------------------------------------
    # 7. Product Name
    # ------------------------------------------------------------------

    # Product name is usually one of the first prominent label lines.
    for line in lines[:5]:
        line_clean = line.strip()

        if (
            len(line_clean) > 3
            and not any(
                keyword in line_clean.lower()
                for keyword in [
                    "mrp",
                    "mfg",
                    "net qty",
                    "batch",
                    "fssai",
                    "ingredients",
                ]
            )
        ):
            extracted["product_name"] = line_clean
            break

    if not extracted["product_name"] and lines:
        extracted["product_name"] = lines[0]

    return extracted