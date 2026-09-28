"""
Compliance evaluation domain models.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any, Dict
from models.enums import ComplianceStatus


@dataclass
class RuleEvaluation:
    rule_id: str
    rule_name: str
    status: ComplianceStatus
    passed: bool
    detected_value: Optional[str] = None
    normalized_value: Optional[Any] = None
    evidence: Optional[str] = None
    message: str = ""
    penalty_ref: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": str(self.status),
            "passed": self.passed,
            "detected_value": self.detected_value,
            "normalized_value": self.normalized_value,
            "evidence": self.evidence,
            "message": self.message,
            "penalty_ref": self.penalty_ref,
        }


@dataclass
class ComplianceReport:
    overall_status: ComplianceStatus
    compliant: bool
    rule_results: List[RuleEvaluation] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    passed_count: int = 0
    violations_count: int = 0
    needs_review_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": str(self.overall_status),
            "compliant": self.compliant,
            "passed_count": self.passed_count,
            "violations_count": self.violations_count,
            "needs_review_count": self.needs_review_count,
            "violations": self.violations,
            "rules": [r.to_dict() for r in self.rule_results],
        }
