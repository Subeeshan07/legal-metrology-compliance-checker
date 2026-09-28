"""
Rule Registry for orchestrating Legal Metrology compliance rules.
"""

from typing import List, Dict, Any, Optional
from rules.base_rule import BaseRule
from rules.manufacturer_rule import ManufacturerRule
from rules.product_name_rule import ProductNameRule
from rules.net_quantity_rule import NetQuantityRule
from rules.mfg_date_rule import MfgDateRule
from rules.mrp_rule import MRPRule
from rules.consumer_care_rule import ConsumerCareRule
from rules.country_of_origin_rule import CountryOfOriginRule
from models.compliance import ComplianceReport, RuleEvaluation
from models.enums import ComplianceStatus
from services.normalization_service import normalize_declarations


class RuleRegistry:
    """
    Registry and execution engine for all registered Legal Metrology rules.
    """

    def __init__(self):
        self._rules: List[BaseRule] = []
        self._rule_map: Dict[str, BaseRule] = {}
        self._register_default_rules()

    def _register_default_rules(self):
        default_rules = [
            ManufacturerRule(),
            ProductNameRule(),
            NetQuantityRule(),
            MfgDateRule(),
            MRPRule(),
            ConsumerCareRule(),
            CountryOfOriginRule(),
        ]
        for rule in default_rules:
            self.register(rule)

    def register(self, rule: BaseRule):
        self._rules.append(rule)
        self._rule_map[rule.rule_id] = rule

    def get_rules(self) -> List[BaseRule]:
        return list(self._rules)

    def get_rule(self, rule_id: str) -> Optional[BaseRule]:
        return self._rule_map.get(rule_id)

    def evaluate(self, declarations: Dict[str, Any], normalized: Optional[Dict[str, Any]] = None) -> ComplianceReport:
        if normalized is None:
            normalized = normalize_declarations(declarations)

        evaluations: List[RuleEvaluation] = []
        violations: List[str] = []
        passed_count = 0
        violations_count = 0
        needs_review_count = 0

        for rule in self._rules:
            evaluation = rule.evaluate(declarations, normalized)
            evaluations.append(evaluation)

            if evaluation.status == ComplianceStatus.COMPLIANT:
                passed_count += 1
            elif evaluation.status == ComplianceStatus.NON_COMPLIANT:
                violations_count += 1
                violations.append(f"{evaluation.rule_id}: {evaluation.message}")
            elif evaluation.status == ComplianceStatus.NEEDS_REVIEW:
                needs_review_count += 1
                violations.append(f"{evaluation.rule_id}: {evaluation.message}")

        if violations_count > 0:
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif needs_review_count > 0:
            overall_status = ComplianceStatus.NEEDS_REVIEW
        else:
            overall_status = ComplianceStatus.COMPLIANT

        return ComplianceReport(
            overall_status=overall_status,
            compliant=(overall_status == ComplianceStatus.COMPLIANT),
            rule_results=evaluations,
            violations=violations,
            passed_count=passed_count,
            violations_count=violations_count,
            needs_review_count=needs_review_count,
        )


# Global default registry instance
default_registry = RuleRegistry()
