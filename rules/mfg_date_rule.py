"""
Rule 6(1)(d): Month and year of manufacture or pre-packing.
"""

from typing import Dict, Any
from rules.base_rule import BaseRule
from models.compliance import RuleEvaluation
from models.enums import ComplianceStatus
from services.normalization_service import normalize_date


class MfgDateRule(BaseRule):
    rule_id = "Rule 6(1)(d)"
    title = "Month & Year of Manufacture / Packing"
    description = (
        "Month and year of manufacture or pre-packing must be stated clearly "
        "(e.g., '04/2026' or 'April 2026')."
    )
    penalty_ref = "Mandatory declaration under consumer right to information."

    def evaluate(self, declarations: Dict[str, Any], normalized: Dict[str, Any] = None) -> RuleEvaluation:
        mfg_str = declarations.get("mfg_date", "")
        norm_date = (normalized or {}).get("mfg_date") or normalize_date(mfg_str)

        if not mfg_str or mfg_str.strip().lower() in ["not declared", "missing", "none", ""]:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=None,
                normalized_value=None,
                evidence=None,
                message="Month and year of manufacture/packing are completely absent.",
                penalty_ref=self.penalty_ref,
            )

        if not norm_date.get("is_valid"):
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NEEDS_REVIEW,
                passed=False,
                detected_value=mfg_str,
                normalized_value=norm_date,
                evidence=mfg_str,
                message=f"Date '{mfg_str}' does not clearly display both month and year.",
                penalty_ref=self.penalty_ref,
            )

        return RuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.title,
            status=ComplianceStatus.COMPLIANT,
            passed=True,
            detected_value=mfg_str,
            normalized_value=norm_date,
            evidence=mfg_str,
            message=f"Manufacturing / Packing date clearly stated ({norm_date.get('formatted')}).",
            penalty_ref=self.penalty_ref,
        )
