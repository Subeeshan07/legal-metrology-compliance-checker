"""
Analytics and dashboard statistics API routes.
"""

import re
from flask import Blueprint, jsonify
from repositories.product_repository import load_dataset

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Returns aggregate compliance metrics and distribution charts for Chart.js
    """
    df = load_dataset()
    if df.empty:
        return jsonify({
            "total_products": 0,
            "compliant": 0,
            "non_compliant": 0,
            "needs_review": 0,
            "compliance_distribution": {"Compliant": 0, "Non-Compliant": 0, "Needs Review": 0},
            "top_violations": {},
            "categories": {}
        })

    total = len(df)
    status_counts = df["compliance_status"].value_counts().to_dict()
    compliant = int(status_counts.get("COMPLIANT", 0))
    non_compliant = int(status_counts.get("NON-COMPLIANT", 0))
    needs_review = int(status_counts.get("NEEDS REVIEW", 0))

    # Parse common violations
    violation_freq = {}
    for entry in df["violations"].dropna():
        if "None" in str(entry):
            continue
        parts = str(entry).split(";")
        for p in parts:
            p_clean = p.strip()
            if p_clean:
                # Group by rule number
                rule_match = re.match(r"(Rule\s*[\w\(\)]+)", p_clean)
                key = rule_match.group(1) if rule_match else p_clean[:35]
                # Label mapping for chart readability
                label_map = {
                    "Rule 6(1)(da)": "Rule 6(1)(da): MRP / Tax Clause Absent",
                    "Rule 6(1)(c)": "Rule 6(1)(c): Net Qty / Non-standard Units",
                    "Rule 6(1)(e)": "Rule 6(1)(e): Consumer Care Grievance Missing",
                    "Rule 6(1)(n)": "Rule 6(1)(n): Country of Origin Absent",
                    "Rule 6(1)(a)": "Rule 6(1)(a): Incomplete Manufacturer Address",
                    "Rule 6(1)(d)": "Rule 6(1)(d): Month & Year of Mfg Missing",
                    "Rule 7": "Rule 7: Font Size / Legibility Non-conformity"
                }
                display_label = label_map.get(key, key)
                violation_freq[display_label] = violation_freq.get(display_label, 0) + 1

    # Sort top violations
    top_violations = dict(sorted(violation_freq.items(), key=lambda item: item[1], reverse=True)[:6])

    # Category breakdown
    category_counts = df["category"].value_counts().head(8).to_dict()

    return jsonify({
        "total_products": total,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "needs_review": needs_review,
        "compliance_distribution": {
            "Compliant": compliant,
            "Non-Compliant": non_compliant,
            "Needs Review": needs_review
        },
        "top_violations": top_violations,
        "categories": category_counts
    })
