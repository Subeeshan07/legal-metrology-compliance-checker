"""
Domain enumeration types for compliance checking and counterfeit analysis.
"""

from enum import Enum


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON-COMPLIANT"
    NEEDS_REVIEW = "NEEDS REVIEW"

    def __str__(self):
        return self.value


class CounterfeitRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    def __str__(self):
        return self.value
