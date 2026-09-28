"""
Rule 6(1)(e): Consumer grievance redressal details.
"""

import re
from typing import Dict, Any
from rules.base_rule import BaseRule
from models.compliance import RuleEvaluation
from models.enums import ComplianceStatus


class ConsumerCareRule(BaseRule):
    rule_id = "Rule 6(1)(e)"
    title = "Consumer Grievance Redressal"
    description = (
        "Name, address, telephone number, and email address of the person/cell that "
        "can be contacted in case of consumer complaints."
    )
    penalty_ref = "Non-compliance treated as deceptive packaging practice."

    def evaluate(self, declarations: Dict[str, Any], normalized: Dict[str, Any] = None) -> RuleEvaluation:
        cc_str = declarations.get("consumer_care", "")

        if not cc_str or cc_str.strip().lower() in ["not declared", "missing", "none", ""]:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=None,
                evidence=None,
                message="Consumer grievance redressal contact information is completely absent.",
                penalty_ref=self.penalty_ref,
            )

        has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", cc_str))
        has_phone = bool(
            re.search(
                r"(?:1800[- ]?\d{3}[- ]?\d{3,4}|\+?91[- ]?\d{10}|\b\d{10}\b|helpline|ph:|tel:)",
                cc_str,
                re.IGNORECASE,
            )
        )

        if not has_email and not has_phone:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NON_COMPLIANT,
                passed=False,
                detected_value=cc_str,
                evidence=cc_str,
                message="Consumer care section detected but neither telephone number nor email address is present.",
                penalty_ref=self.penalty_ref,
            )

        if has_email and not has_phone:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NEEDS_REVIEW,
                passed=False,
                detected_value=cc_str,
                evidence=cc_str,
                message="Email address detected, but telephone/helpline number is missing.",
                penalty_ref=self.penalty_ref,
            )

        if has_phone and not has_email:
            return RuleEvaluation(
                rule_id=self.rule_id,
                rule_name=self.title,
                status=ComplianceStatus.NEEDS_REVIEW,
                passed=False,
                detected_value=cc_str,
                evidence=cc_str,
                message="Helpline phone detected, but consumer grievance email address is missing.",
                penalty_ref=self.penalty_ref,
            )

        return RuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.title,
            status=ComplianceStatus.COMPLIANT,
            passed=True,
            detected_value=cc_str,
            evidence=cc_str,
            message="Both telephone helpline and grievance email address detected.",
            penalty_ref=self.penalty_ref,
        )
