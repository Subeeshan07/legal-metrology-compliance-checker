"""
Rule 6(1)(a): Name and complete address of the manufacturer, packer, or importer.
"""

import re
from typing import Dict, Any
from rules.base_rule import BaseRule
from models.compliance import RuleEvaluation
from models.enums import ComplianceStatus


class ManufacturerRule(BaseRule):
    rule_id = "Rule 6(1)(a)"
    title = "Manufacturer / Packer / Importer Details"
    description = (
        "Every package shall bear the name and complete address of the manufacturer, "
        "or packer, or importer."
    )
    penalty_ref = "Section 36 of Legal Metrology Act, 2009: Fine up to Rs. 25,000 for first offence."

    def evaluate(self, declarations: Dict[str, Any], normalized: Dict[str, Any] = None) -> RuleEvaluation:
        mfr_text = declarations.get("manufacturer", "")

        if not mfr_text or mfr_text.strip().lower() in ["not declared", "missing", "none", ""]:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=None,
                evidence=None,
                message="Manufacturer/Packer name and address are absent from the packaging.",
                penalty_ref=self.penalty_ref,
            )

        text_lower = mfr_text.lower()
        has_pin = bool(re.search(r"\b\d{6}\b", mfr_text))
        has_location = any(
            kw in text_lower
            for kw in [
                "road", "street", "plot", "midc", "phase", "sector",
                "industrial", "sy.", "gat", "nagar", "city", "village", "area"
            ]
        )

        if not has_pin and not has_location and len(mfr_text.split()) < 4:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NEEDS_REVIEW,
                passed=False,
                detected_value=mfr_text,
                evidence=mfr_text,
                message="Manufacturer name detected, but complete physical address or PIN code is missing/abbreviated.",
                penalty_ref=self.penalty_ref,
            )

        return RuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.title,
            status=ComplianceStatus.COMPLIANT,
            passed=True,
            detected_value=mfr_text,
            evidence=mfr_text,
            message="Valid manufacturer/packer identification detected.",
            penalty_ref=self.penalty_ref,
        )
