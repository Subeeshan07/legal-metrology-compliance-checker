"""
Base rule interface for Legal Metrology compliance rules.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from models.compliance import RuleEvaluation
from models.enums import ComplianceStatus


class BaseRule(ABC):
    """
    Abstract base class for all individual Legal Metrology compliance rules.
    """

    rule_id: str = ""
    title: str = ""
    description: str = ""
    penalty_ref: str = ""

    @abstractmethod
    def evaluate(self, declarations: Dict[str, Any], normalized: Dict[str, Any] = None) -> RuleEvaluation:
        """
        Evaluates declared packaging properties and returns a RuleEvaluation.
        """
        pass
