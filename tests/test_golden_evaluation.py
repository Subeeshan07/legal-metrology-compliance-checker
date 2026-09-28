"""
Automated Golden Dataset Regression & Evaluation Test Suite.
Verifies accuracy benchmarks across all golden packaging examples.
"""

import json
import os
import unittest
from services.analysis_orchestrator import AnalysisOrchestrator


class TestGoldenDatasetEvaluation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dataset_path = os.path.join(
            os.path.dirname(__file__),
            "golden_dataset",
            "golden_compliance_labels.json"
        )
        with open(dataset_path, "r", encoding="utf-8") as f:
            cls.golden_samples = json.load(f)

    def test_golden_dataset_metrics(self):
        """
        Executes end-to-end evaluation and asserts zero false compliances
        and >= 95% classification accuracy across all evaluation vectors.
        """
        total = len(self.golden_samples)
        correct_compliance = 0
        correct_counterfeit = 0
        false_compliances = 0

        for item in self.golden_samples:
            res = AnalysisOrchestrator.analyze_scan(
                manual_text=item["raw_text"],
                barcode=item.get("barcode")
            )
            actual_comp = res["compliance"]["overall_status"]
            actual_risk = res["counterfeit_risk"]["risk_tier"]

            if actual_comp == item["expected_compliance_status"]:
                correct_compliance += 1
            elif actual_comp == "COMPLIANT" and item["expected_compliance_status"] != "COMPLIANT":
                false_compliances += 1

            if actual_risk == item["expected_counterfeit_risk"]:
                correct_counterfeit += 1

        comp_accuracy = (correct_compliance / total) * 100
        risk_accuracy = (correct_counterfeit / total) * 100

        self.assertEqual(false_compliances, 0, "Safety violation: False compliance detected in golden dataset!")
        self.assertGreaterEqual(comp_accuracy, 95.0)
        self.assertGreaterEqual(risk_accuracy, 95.0)


if __name__ == "__main__":
    unittest.main()
