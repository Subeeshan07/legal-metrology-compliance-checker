"""
Rule 6(1)(b): Generic or common name of the commodity.
"""

from typing import Dict, Any
from rules.base_rule import BaseRule
from models.compliance import RuleEvaluation
from models.enums import ComplianceStatus


class ProductNameRule(BaseRule):
    rule_id = "Rule 6(1)(b)"
    title = "Generic / Common Name of Commodity"
    description = (
        "The common or generic name of the commodity contained in the package must "
        "be prominently displayed on the Principal Display Panel."
    )
    penalty_ref = "Fine up to Rs. 50,000 for second offence, imprisonment up to one year for subsequent offences."

    def evaluate(self, declarations: Dict[str, Any], normalized: Dict[str, Any] = None) -> RuleEvaluation:
        product_name = declarations.get("product_name", "")

        if not product_name or product_name.strip().lower() in ["not declared", "missing", "none", ""]:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=None,
                evidence=None,
                message="Generic or common name of the commodity is missing.",
                penalty_ref=self.penalty_ref,
            )

        if len(product_name.strip()) < 3:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NEEDS_REVIEW,
                passed=False,
                detected_value=product_name,
                evidence=product_name,
                message="Commodity name detected is too short or ambiguous.",
                penalty_ref=self.penalty_ref,
            )

        return RuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.title,
            status=ComplianceStatus.COMPLIANT,
            passed=True,
            detected_value=product_name,
            evidence=product_name,
            message="Commodity name clearly stated.",
            penalty_ref=self.penalty_ref,
        )
