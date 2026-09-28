"""
Rule 6(1)(da): Maximum Retail Price (MRP) and inclusive of all taxes clause.
"""

from typing import Dict, Any
from rules.base_rule import BaseRule
from models.compliance import RuleEvaluation
from models.enums import ComplianceStatus
from services.normalization_service import normalize_price


class MRPRule(BaseRule):
    rule_id = "Rule 6(1)(da)"
    title = "Maximum Retail Price (MRP)"
    description = (
        "The retail sale price of the package in the format 'MRP Rs. XX.XX (incl. of all taxes)' "
        "or '₹ XX.XX (inclusive of all taxes)'."
    )
    penalty_ref = "Section 36(2): Fine up to Rs. 25,000 for first offence, Rs. 50,000 for second offence."

    def evaluate(self, declarations: Dict[str, Any], normalized: Dict[str, Any] = None) -> RuleEvaluation:
        mrp_str = declarations.get("mrp", "")
        norm_price = (normalized or {}).get("mrp") or normalize_price(mrp_str)

        if not norm_price.get("declared") or not mrp_str or mrp_str.strip().lower() in ["not declared", "missing", "none", ""]:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=None,
                normalized_value=None,
                evidence=None,
                message="Maximum Retail Price (MRP) declaration is completely absent.",
                penalty_ref=self.penalty_ref,
            )

        if not norm_price.get("has_tax_clause"):
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=mrp_str,
                normalized_value=norm_price,
                evidence=mrp_str,
                message="MRP is stated but mandatory '(incl. of all taxes)' clause is absent.",
                penalty_ref=self.penalty_ref,
            )

        return RuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.title,
            status=ComplianceStatus.COMPLIANT,
            passed=True,
            detected_value=mrp_str,
            normalized_value=norm_price,
            evidence=mrp_str,
            message="Valid MRP with statutory '(incl. of all taxes)' clause detected.",
            penalty_ref=self.penalty_ref,
        )
