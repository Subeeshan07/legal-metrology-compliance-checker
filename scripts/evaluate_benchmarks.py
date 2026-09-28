"""
Benchmarking and Quality Metrics Evaluation Script.

Evaluates the Legal Metrology Compliance Checker & Food Counterfeit
Risk Analysis pipeline against the golden evaluation dataset.
Computes:
- Field-level extraction accuracy
- Rule-level compliance verdict accuracy
- False Compliance Rate (FCR) & False Non-Compliance Rate (FNCR)
- Counterfeit Risk classification accuracy
"""

import json
import os
import sys

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from services.analysis_orchestrator import AnalysisOrchestrator


def run_benchmark():
    dataset_path = os.path.join(REPO_ROOT, "tests", "golden_dataset", "golden_compliance_labels.json")
    if not os.path.exists(dataset_path):
        print(f"Error: Golden dataset not found at {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    total_samples = len(samples)
    print(f"\n================================================================================")
    print(f"     LEGAL METROLOGY & FOOD COUNTERFEIT EVALUATION BENCHMARK")
    print(f"================================================================================")
    print(f"Total Golden Dataset Test Cases: {total_samples}\n")

    correct_compliance = 0
    correct_counterfeit = 0
    false_compliances = 0
    false_non_compliances = 0
    total_fields = 0
    matched_fields = 0

    results_table = []

    for item in samples:
        cid = item["id"]
        raw_text = item["raw_text"]
        barcode = item.get("barcode")
        expected_status = item["expected_compliance_status"]
        expected_risk = item["expected_counterfeit_risk"]
        expected_entities = item.get("expected_entities", {})

        # Run pipeline
        res = AnalysisOrchestrator.analyze_scan(
            manual_text=raw_text,
            barcode=barcode
        )

        actual_status = res["compliance"]["overall_status"]
        actual_risk = res["counterfeit_risk"].get("risk_tier") or res["counterfeit_risk"].get("risk_level")
        extracted = res["extracted_entities"]

        # Check compliance match
        comp_match = (actual_status == expected_status)
        if comp_match:
            correct_compliance += 1
        else:
            if actual_status == "COMPLIANT" and expected_status != "COMPLIANT":
                false_compliances += 1
            elif actual_status == "NON-COMPLIANT" and expected_status == "COMPLIANT":
                false_non_compliances += 1

        # Check counterfeit match
        risk_match = (actual_risk == expected_risk)
        if risk_match:
            correct_counterfeit += 1

        # Check field accuracy
        for k, v in expected_entities.items():
            total_fields += 1
            act_v = extracted.get(k, "")
            if v.lower() in act_v.lower() or act_v.lower() in v.lower():
                matched_fields += 1

        results_table.append({
            "id": cid,
            "expected_comp": expected_status,
            "actual_comp": actual_status,
            "comp_match": "PASS" if comp_match else "FAIL",
            "expected_risk": expected_risk,
            "actual_risk": actual_risk,
            "risk_match": "PASS" if risk_match else "FAIL",
        })

    # Print summary table
    print(f"{'ID':<12} | {'Exp Compliance':<16} | {'Act Compliance':<16} | {'Comp':<6} | {'Exp Risk':<10} | {'Act Risk':<10} | {'Risk':<6}")
    print("-" * 88)
    for r in results_table:
        print(f"{r['id']:<12} | {r['expected_comp']:<16} | {r['actual_comp']:<16} | {r['comp_match']:<6} | {r['expected_risk']:<10} | {r['actual_risk']:<10} | {r['risk_match']:<6}")

    comp_acc = (correct_compliance / total_samples) * 100
    risk_acc = (correct_counterfeit / total_samples) * 100
    field_acc = (matched_fields / total_fields) * 100 if total_fields else 0
    fcr = (false_compliances / total_samples) * 100
    fncr = (false_non_compliances / total_samples) * 100

    print(f"\n================================================================================")
    print(f"                            FINAL BENCHMARK METRICS")
    print(f"================================================================================")
    print(f"Compliance Classification Accuracy : {comp_acc:.1f}% ({correct_compliance}/{total_samples})")
    print(f"Counterfeit Risk Accuracy          : {risk_acc:.1f}% ({correct_counterfeit}/{total_samples})")
    print(f"Field-Level Extraction Accuracy    : {field_acc:.1f}% ({matched_fields}/{total_fields})")
    print(f"False Compliance Rate (FCR)        : {fcr:.1f}% (Safety Critical)")
    print(f"False Non-Compliance Rate (FNCR)    : {fncr:.1f}%")
    print(f"================================================================================\n")

    return {
        "compliance_accuracy": comp_acc,
        "counterfeit_accuracy": risk_acc,
        "field_accuracy": field_acc,
        "fcr": fcr,
        "fncr": fncr,
    }


if __name__ == "__main__":
    run_benchmark()
