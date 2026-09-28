"""
Rule 6(1)(n): Mandatory declaration of country of origin.
"""

from typing import Dict, Any
from rules.base_rule import BaseRule
from models.compliance import RuleEvaluation
from models.enums import ComplianceStatus
from services.normalization_service import normalize_country


class CountryOfOriginRule(BaseRule):
    rule_id = "Rule 6(1)(n)"
    title = "Country of Origin Declaration"
    description = (
        "Mandatory declaration of country of origin / manufacture for all domestic "
        "and imported packaged goods."
    )
    penalty_ref = "Required under Consumer Protection (E-Commerce) Rules and Legal Metrology amendment."

    def evaluate(self, declarations: Dict[str, Any], normalized: Dict[str, Any] = None) -> RuleEvaluation:
        origin_str = declarations.get("country_of_origin", "")
        norm_country = (normalized or {}).get("country") or normalize_country(origin_str)

        if not norm_country.get("declared") or not origin_str or origin_str.strip().lower() in ["not declared", "missing", "none", ""]:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=None,
                normalized_value=None,
                evidence=None,
                message="Country of Origin declaration is completely absent.",
                penalty_ref=self.penalty_ref,
            )

        country_name = norm_country.get("standardized") or origin_str.strip()
        return RuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.title,
            status=ComplianceStatus.COMPLIANT,
            passed=True,
            detected_value=origin_str,
            normalized_value=norm_country,
            evidence=origin_str,
            message=f"Country of Origin clearly declared ({country_name}).",
            penalty_ref=self.penalty_ref,
        )
