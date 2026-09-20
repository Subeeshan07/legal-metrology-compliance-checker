"""
Compliance evaluation service for the Legal Metrology Compliance Checker.

This module contains the compliance engine responsible for evaluating
structured declarations extracted from packaged commodity labels.

Task 1.6 moves the existing compliance logic out of app.py without
intentionally changing its behaviour.
"""

import re
from datetime import datetime


class LegalMetrologyComplianceEngine:
    """
    Evaluates extracted product packaging declarations against the
    provisions of the Legal Metrology (Packaged Commodities) Rules, 2011.
    """

    VALID_SI_UNITS = {
        "g",
        "kg",
        "ml",
        "l",
        "m",
        "cm",
        "mm",
        "n",
        "u",
        "pcs",
        "pieces",
    }

    AMBIGUOUS_UNITS = {
        "gms",
        "gm",
        "kilo",
        "kilos",
        "ml.",
        "ltr",
        "litres",
        "liter",
    }

    @classmethod
    def check_rule_6_1_a_manufacturer(cls, manufacturer_text):
        """
        Rule 6(1)(a): Name and complete address of the manufacturer,
        packer, or importer.
        """

        if (
            not manufacturer_text
            or manufacturer_text.strip().lower()
            in ["not declared", "missing", "none", ""]
        ):
            return {
                "rule": "Rule 6(1)(a)",
                "title": "Manufacturer / Packer / Importer Details",
                "status": "FAIL",
                "message": (
                    "Manufacturer/Packer name and address are absent "
                    "from the packaging."
                ),
                "recommendation": (
                    "Declare complete legal entity name with physical "
                    "address including city and postal PIN code."
                ),
            }

        text_lower = manufacturer_text.lower()

        has_pin = (
            re.search(r"\b\d{6}\b", manufacturer_text)
            is not None
        )

        has_location = any(
            keyword in text_lower
            for keyword in [
                "road",
                "street",
                "plot",
                "midc",
                "phase",
                "sector",
                "industrial",
                "sy.",
                "gat",
                "nagar",
                "city",
                "village",
                "area",
            ]
        )

        if (
            not has_pin
            and not has_location
            and len(manufacturer_text.split()) < 4
        ):
            return {
                "rule": "Rule 6(1)(a)",
                "title": "Manufacturer / Packer / Importer Details",
                "status": "WARNING",
                "message": (
                    "Manufacturer name detected, but complete physical "
                    "address or PIN code is missing/abbreviated."
                ),
                "recommendation": (
                    "Provide full manufacturing/packing unit address "
                    "with postal PIN code as required by Rule 6(1)(a)."
                ),
            }

        return {
            "rule": "Rule 6(1)(a)",
            "title": "Manufacturer / Packer / Importer Details",
            "status": "PASS",
            "message": (
                "Valid manufacturer/packer identification detected."
            ),
            "recommendation": "Compliant with Rule 6(1)(a).",
        }

    @classmethod
    def check_rule_6_1_b_product_name(cls, product_name):
        """
        Rule 6(1)(b): Common or generic name of the commodity
        contained in the package.
        """

        if (
            not product_name
            or product_name.strip().lower()
            in ["not declared", "missing", "none", ""]
        ):
            return {
                "rule": "Rule 6(1)(b)",
                "title": "Generic / Common Name of Commodity",
                "status": "FAIL",
                "message": (
                    "Generic or common name of the commodity is missing."
                ),
                "recommendation": (
                    "Print generic commodity name prominently on the "
                    "Principal Display Panel (PDP)."
                ),
            }

        if len(product_name.strip()) < 3:
            return {
                "rule": "Rule 6(1)(b)",
                "title": "Generic / Common Name of Commodity",
                "status": "WARNING",
                "message": (
                    "Commodity name detected is too short or ambiguous."
                ),
                "recommendation": (
                    "Ensure the generic description clearly identifies "
                    "the nature of the packaged food."
                ),
            }

        return {
            "rule": "Rule 6(1)(b)",
            "title": "Generic / Common Name of Commodity",
            "status": "PASS",
            "message": (
                f"Generic/common commodity name declared: "
                f"'{product_name.strip()}'."
            ),
            "recommendation": "Compliant with Rule 6(1)(b).",
        }

    @classmethod
    def check_rule_6_1_c_net_quantity(cls, net_quantity):
        """
        Rule 6(1)(c): Net quantity in terms of standard unit
        of weight or measure.

        Rule 13: Standard symbols must be used.
        """

        if (
            not net_quantity
            or net_quantity.strip().lower()
            in ["not declared", "missing", "none", ""]
        ):
            return {
                "rule": "Rule 6(1)(c)",
                "title": "Net Quantity & Standard Units",
                "status": "FAIL",
                "message": (
                    "Net quantity declaration is absent from "
                    "the packaging."
                ),
                "recommendation": (
                    "Declare net quantity in standard metric units "
                    "(g, kg, ml, L, or N) on the Principal Display Panel."
                ),
            }

        qty_str = net_quantity.lower().strip()
        tokens = qty_str.split()

        # Preserve existing handling of ambiguous unit abbreviations.
        for amb in cls.AMBIGUOUS_UNITS:
            if amb in tokens or qty_str.endswith(amb):
                return {
                    "rule": "Rule 6(1)(c)",
                    "title": "Net Quantity & Standard Units",
                    "status": "WARNING",
                    "message": (
                        f"Non-standard unit symbol detected ('{amb}'). "
                        "Rule 13 mandates standard SI symbols "
                        "(use 'g' instead of 'gms/gm', 'ml' or 'L' "
                        "instead of 'ltr/ML')."
                    ),
                    "recommendation": (
                        "Change abbreviation to standard metric units: "
                        "'g' for grams, 'kg' for kilograms, 'ml' for "
                        "millilitres, 'L' for litres."
                    ),
                }

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)",
            net_quantity,
        )

        if not match:
            return {
                "rule": "Rule 6(1)(c)",
                "title": "Net Quantity & Standard Units",
                "status": "WARNING",
                "message": (
                    "Net quantity format is ambiguous or "
                    "unverified by OCR."
                ),
                "recommendation": (
                    "Ensure numeric quantity is clearly followed "
                    "by standard unit symbol."
                ),
            }

        unit = match.group(2).lower()

        if unit not in cls.VALID_SI_UNITS:
            return {
                "rule": "Rule 6(1)(c)",
                "title": "Net Quantity & Standard Units",
                "status": "WARNING",
                "message": (
                    f"Detected unit symbol '{unit}' is non-standard "
                    "under Second Schedule of PCR, 2011."
                ),
                "recommendation": (
                    "Use approved standard SI unit symbol."
                ),
            }

        return {
            "rule": "Rule 6(1)(c)",
            "title": "Net Quantity & Standard Units",
            "status": "PASS",
            "message": (
                f"Net quantity properly declared: "
                f"'{net_quantity.strip()}'."
            ),
            "recommendation": (
                "Compliant with Rule 6(1)(c) and Rule 13."
            ),
        }

    @classmethod
    def check_rule_6_1_d_mfg_date(cls, mfg_date):
        """
        Rule 6(1)(d): Month and year in which the commodity
        is manufactured or pre-packed.
        """

        if (
            not mfg_date
            or mfg_date.strip().lower()
            in ["not declared", "missing", "none", ""]
        ):
            return {
                "rule": "Rule 6(1)(d)",
                "title": "Month & Year of Manufacture / Packing",
                "status": "FAIL",
                "message": (
                    "Month and year of manufacture/pre-packing "
                    "is absent."
                ),
                "recommendation": (
                    "Declare date of manufacturing or packing "
                    "in MM/YYYY or Month YYYY format."
                ),
            }

        date_pattern = (
            r"(\b\d{1,2}[/\-\.]\d{2,4}\b|"
            r"\b[A-Za-z]{3,9}\s*\d{4}\b|"
            r"\b\d{4}\b)"
        )

        if not re.search(date_pattern, mfg_date):
            return {
                "rule": "Rule 6(1)(d)",
                "title": "Month & Year of Manufacture / Packing",
                "status": "WARNING",
                "message": (
                    f"Date format '{mfg_date}' is ambiguous "
                    "or partially obscured."
                ),
                "recommendation": (
                    "Ensure month and year are clearly legible "
                    "(e.g., '04/2026' or 'Apr 2026')."
                ),
            }

        return {
            "rule": "Rule 6(1)(d)",
            "title": "Month & Year of Manufacture / Packing",
            "status": "PASS",
            "message": (
                f"Manufacturing/Packing date declared: "
                f"'{mfg_date.strip()}'."
            ),
            "recommendation": "Compliant with Rule 6(1)(d).",
        }

    @classmethod
    def check_rule_6_1_da_mrp(cls, mrp):
        """
        Rule 6(1)(da): Maximum Retail Price inclusive of all taxes.
        """

        if (
            not mrp
            or mrp.strip().lower()
            in ["not declared", "missing", "none", ""]
        ):
            return {
                "rule": "Rule 6(1)(da)",
                "title": "Maximum Retail Price (MRP)",
                "status": "FAIL",
                "message": (
                    "Maximum Retail Price (MRP) declaration is absent."
                ),
                "recommendation": (
                    "Declare MRP in Indian Rupees with mandatory "
                    "phrase 'Inclusive of all taxes'."
                ),
            }

        mrp_lower = mrp.lower()

        has_tax_phrase = any(
            phrase in mrp_lower
            for phrase in [
                "incl",
                "all tax",
                "all taxes",
                "inclusive of all taxes",
            ]
        )

        # Retained from the existing implementation for compatibility.
        has_currency = (
            any(
                curr in mrp_lower
                for curr in ["rs", "₹", "inr"]
            )
            or re.search(r"\d+", mrp)
        )

        if not has_tax_phrase:
            return {
                "rule": "Rule 6(1)(da)",
                "title": "Maximum Retail Price (MRP)",
                "status": "FAIL",
                "message": (
                    f"MRP declared as '{mrp}', but the mandatory "
                    "phrase 'Inclusive of all taxes' is missing."
                ),
                "recommendation": (
                    "Rule 6(1)(da) strictly mandates stating "
                    "'MRP Rs. XX.XX (incl. of all taxes)'."
                ),
            }

        return {
            "rule": "Rule 6(1)(da)",
            "title": "Maximum Retail Price (MRP)",
            "status": "PASS",
            "message": (
                f"MRP properly declared with tax clause: "
                f"'{mrp.strip()}'."
            ),
            "recommendation": "Compliant with Rule 6(1)(da).",
        }

    @classmethod
    def check_rule_6_1_e_consumer_care(cls, consumer_care):
        """
        Rule 6(1)(e): Consumer grievance redressal details.
        """

        if (
            not consumer_care
            or consumer_care.strip().lower()
            in ["not declared", "missing", "none", ""]
        ):
            return {
                "rule": "Rule 6(1)(e)",
                "title": "Consumer Care / Grievance Redressal",
                "status": "FAIL",
                "message": (
                    "Consumer grievance redressal details "
                    "are completely absent."
                ),
                "recommendation": (
                    "Provide official helpline telephone number "
                    "and email address for consumer complaints."
                ),
            }

        cc_lower = consumer_care.lower()

        has_email = (
            re.search(
                r"[\w\.-]+@[\w\.-]+\.\w+",
                consumer_care,
            )
            is not None
            or "email" in cc_lower
        )

        has_phone = (
            re.search(
                r"(\+?\d{1,3}[- ]?)?"
                r"\(?\d{3,5}\)?[- ]?\d{3,6}|"
                r"\b1800[- ]?\d{3}[- ]?\d{3,4}\b",
                consumer_care,
            )
            is not None
            or "ph" in cc_lower
            or "tel" in cc_lower
            or "helpline" in cc_lower
        )

        if not has_email and not has_phone:
            return {
                "rule": "Rule 6(1)(e)",
                "title": "Consumer Care / Grievance Redressal",
                "status": "FAIL",
                "message": (
                    "Neither consumer care telephone nor email "
                    "address could be verified."
                ),
                "recommendation": (
                    "Include at least an active helpline telephone "
                    "number and official email address."
                ),
            }

        if not has_email:
            return {
                "rule": "Rule 6(1)(e)",
                "title": "Consumer Care / Grievance Redressal",
                "status": "WARNING",
                "message": (
                    "Consumer helpline telephone found, but "
                    "grievance email address is missing."
                ),
                "recommendation": (
                    "Provide both telephone number and email address "
                    "as required under Rule 6(1)(e)."
                ),
            }

        return {
            "rule": "Rule 6(1)(e)",
            "title": "Consumer Care / Grievance Redressal",
            "status": "PASS",
            "message": (
                "Consumer care grievance mechanism details detected."
            ),
            "recommendation": "Compliant with Rule 6(1)(e).",
        }

    @classmethod
    def check_rule_6_1_n_country_of_origin(
        cls,
        country_of_origin,
    ):
        """
        Rule 6(1)(n): Country of origin declaration.
        """

        if (
            not country_of_origin
            or country_of_origin.strip().lower()
            in ["not declared", "missing", "none", ""]
        ):
            return {
                "rule": "Rule 6(1)(n)",
                "title": "Country of Origin Declaration",
                "status": "FAIL",
                "message": (
                    "Country of origin declaration is missing."
                ),
                "recommendation": (
                    "Declare 'Country of Origin: India' or originating "
                    "nation clearly on the package."
                ),
            }

        return {
            "rule": "Rule 6(1)(n)",
            "title": "Country of Origin Declaration",
            "status": "PASS",
            "message": (
                f"Country of origin declared: "
                f"'{country_of_origin.strip()}'."
            ),
            "recommendation": "Compliant with Rule 6(1)(n).",
        }

    @classmethod
    def evaluate(cls, extracted):
        """
        Runs all compliance rules and determines final verdict.
        """

        checks = [
            cls.check_rule_6_1_b_product_name(
                extracted.get("product_name")
            ),
            cls.check_rule_6_1_a_manufacturer(
                extracted.get("manufacturer")
            ),
            cls.check_rule_6_1_c_net_quantity(
                extracted.get("net_quantity")
            ),
            cls.check_rule_6_1_d_mfg_date(
                extracted.get("mfg_date")
            ),
            cls.check_rule_6_1_da_mrp(
                extracted.get("mrp")
            ),
            cls.check_rule_6_1_e_consumer_care(
                extracted.get("consumer_care")
            ),
            cls.check_rule_6_1_n_country_of_origin(
                extracted.get("country_of_origin")
            ),
        ]

        has_failure = any(
            check["status"] == "FAIL"
            for check in checks
        )

        has_warning = any(
            check["status"] == "WARNING"
            for check in checks
        )

        if has_failure:
            overall_status = "NON-COMPLIANT"
        elif has_warning:
            overall_status = "NEEDS REVIEW"
        else:
            overall_status = "COMPLIANT"

        violations = []

        for check in checks:
            if check["status"] in ["FAIL", "WARNING"]:
                violations.append(
                    f"{check['rule']}: {check['message']}"
                )

        violations_str = (
            "; ".join(violations)
            if violations
            else "None (Fully Compliant with Rule 6)"
        )

        return {
            "overall_status": overall_status,
            "checks": checks,
            "violations": violations,
            "violations_summary": violations_str,
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }