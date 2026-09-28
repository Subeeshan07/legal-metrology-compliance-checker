"""
Legal Metrology rules reference API routes.
"""

from flask import Blueprint, jsonify

rules_bp = Blueprint("rules", __name__)


@rules_bp.route("/api/rules", methods=["GET"])
def get_rules_reference():
    """
    Returns Legal Metrology (Packaged Commodities) Rules, 2011 documentation
    for educational and reference tab.
    """
    rules = [
        {
            "rule": "Rule 6(1)(a)",
            "title": "Name and Address of Manufacturer / Packer",
            "description": "Every package shall bear the name and complete address of the manufacturer, or packer, or importer.",
            "penalty": "Section 36 of Legal Metrology Act, 2009: Fine up to Rs. 25,000 for first offence."
        },
        {
            "rule": "Rule 6(1)(b)",
            "title": "Generic or Common Name",
            "description": "The common or generic name of the commodity contained in the package must be prominently displayed on the Principal Display Panel.",
            "penalty": "Fine up to Rs. 50,000 for second offence, imprisonment up to one year for subsequent offences."
        },
        {
            "rule": "Rule 6(1)(c) & Rule 13",
            "title": "Net Quantity & Standard Units",
            "description": "Net quantity must be declared using standard SI symbols: 'g' for grams (not 'gms'/'gm'), 'kg' for kilograms, 'ml' for millilitres (not 'ML'/'ltr'), 'L' for litres, or 'N' for numbers.",
            "penalty": "Seizure of non-standard packaged commodities under Section 15 of the Act."
        },
        {
            "rule": "Rule 6(1)(d)",
            "title": "Month and Year of Manufacture / Packing",
            "description": "Month and year of manufacture or pre-packing must be stated clearly (e.g., '04/2026' or 'April 2026').",
            "penalty": "Mandatory declaration under consumer right to information."
        },
        {
            "rule": "Rule 6(1)(da)",
            "title": "Maximum Retail Price (MRP)",
            "description": "The retail sale price of the package in the format 'MRP Rs. XX.XX (incl. of all taxes)' or '₹ XX.XX (inclusive of all taxes)'. Charging above MRP is strictly punishable.",
            "penalty": "Section 36(2): Fine up to Rs. 25,000 for first offence, Rs. 50,000 for second offence."
        },
        {
            "rule": "Rule 6(1)(e)",
            "title": "Consumer Grievance Redressal",
            "description": "Name, address, telephone number, and email address of the person/cell that can be contacted in case of consumer complaints.",
            "penalty": "Non-compliance treated as deceptive packaging practice."
        },
        {
            "rule": "Rule 6(1)(n)",
            "title": "Country of Origin",
            "description": "Mandatory declaration of country of origin / manufacture for all domestic and imported packaged goods.",
            "penalty": "Required under Consumer Protection (E-Commerce) Rules and Legal Metrology amendment."
        }
    ]
    return jsonify({"rules": rules})
