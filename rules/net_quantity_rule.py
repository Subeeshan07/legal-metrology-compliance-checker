"""
Rule 6(1)(c) & Rule 13: Net quantity declaration in standard SI units.
"""

import re
from typing import Dict, Any
from rules.base_rule import BaseRule
from models.compliance import RuleEvaluation
from models.enums import ComplianceStatus
from services.normalization_service import normalize_quantity, ALL_STANDARD_UNITS, NON_STANDARD_UNIT_MAPPING


class NetQuantityRule(BaseRule):
    rule_id = "Rule 6(1)(c) & Rule 13"
    title = "Net Quantity & Standard Units"
    description = (
        "Net quantity must be declared using standard SI symbols: 'g' for grams, "
        "'kg' for kilograms, 'ml' for millilitres, 'l'/'L' for litres, or 'n'/'N' for count."
    )
    penalty_ref = "Seizure of non-standard packaged commodities under Section 15 of the Act."

    def evaluate(self, declarations: Dict[str, Any], normalized: Dict[str, Any] = None) -> RuleEvaluation:
        qty_str = declarations.get("net_quantity", "")
        norm_qty = (normalized or {}).get("quantity") or normalize_quantity(qty_str)

        if not norm_qty.get("declared") or not qty_str or qty_str.strip().lower() in ["not declared", "missing", "none", ""]:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=None,
                normalized_value=None,
                evidence=None,
                message="Net quantity declaration is absent from the packaging.",
                penalty_ref=self.penalty_ref,
            )

        unit = norm_qty.get("unit")
        if not unit:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=qty_str,
                normalized_value=norm_qty,
                evidence=qty_str,
                message=f"Net quantity '{qty_str}' has no recognizable measurement unit.",
                penalty_ref=self.penalty_ref,
            )

        if not norm_qty.get("is_standard_unit") or unit in NON_STANDARD_UNIT_MAPPING:
            standard_alt = norm_qty.get("standard_unit", "g")
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NEEDS_REVIEW,
                passed=False,
                detected_value=qty_str,
                normalized_value=norm_qty,
                evidence=qty_str,
                message=f"Non-standard unit symbol '{unit}' used. Rule 13 prescribes standard SI unit '{standard_alt}'.",
                penalty_ref=self.penalty_ref,
            )

        return RuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.title,
            status=ComplianceStatus.COMPLIANT,
            passed=True,
            detected_value=qty_str,
            normalized_value=norm_qty,
            evidence=qty_str,
            message=f"Standard net quantity declaration detected ({qty_str}).",
            penalty_ref=self.penalty_ref,
        )
