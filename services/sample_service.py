"""
Sample label image generation and preset service.

Generates realistic synthetic packaged food label samples for quick
one-click testing of compliance and verification workflows.
"""

import os
import logging
from PIL import Image, ImageDraw
from config.settings import Config

logger = logging.getLogger(__name__)

SAMPLE_DEFINITIONS = [
    {
        "sample_id": "compliant",
        "filename": "sample_compliant_atta.png",
        "title": "Compliant Label (Whole Wheat Atta)",
        "lines": [
            "HIMALAYAN CHAKKI FRESH ATTA",
            "100% Pure Whole Wheat Flour",
            "Net Quantity: 5 kg",
            "MRP Rs. 245.00 (Incl. of all taxes)",
            "Mfg Date: 05/2026",
            "Batch No: HCF-2026-B8",
            "Manufactured by: Pristine Foods & Agro Ltd,",
            "Phase 2, Peenya Industrial Area, Bengaluru - 560058",
            "Consumer Care: care@pristine.com | Ph: 1800-220-4400",
            "Country of Origin: India"
        ],
    },
    {
        "sample_id": "non_compliant",
        "filename": "sample_non_compliant_chips.png",
        "title": "Non-Compliant Label (Missing Tax Clause & Care & Origin)",
        "lines": [
            "CRUNCHY POTATO MASALA CHIPS",
            "Net Qty: 80 g",
            "MRP Rs. 40.00",  # VIOLATION: Missing 'incl of all taxes'
            "Mfg Date: 04/2026",
            "Manufactured by: Surya Snacks LLP, Industrial Zone",
            # VIOLATION: Missing Consumer Care email/phone
            # VIOLATION: Missing Country of Origin
        ],
    },
    {
        "sample_id": "needs_review",
        "filename": "sample_needs_review_spice.png",
        "title": "Needs Review Label (Non-standard Unit & Incomplete Address)",
        "lines": [
            "KASHMIRI DEGI RED CHILLI POWDER",
            "Net Quantity: 200 gms",  # VIOLATION: 'gms' instead of standard 'g'
            "MRP Rs. 145.00 (Incl. of all taxes)",
            "PKD: 06/2026",
            "Mfd by: Kaveri Spices & Naturals, Idukki",  # VIOLATION: Incomplete street address
            "Consumer Care Helpline: 1800-435-8475",    # VIOLATION: Missing email
            "Country of Origin: India"
        ],
    }
]


def render_label_image(definition):
    """
    Renders an in-memory PIL image representing a product label.
    """
    img = Image.new("RGB", (700, 480), color="#ffffff")
    draw = ImageDraw.Draw(img)

    # Header banner
    draw.rectangle([(0, 0), (700, 50)], fill="#0f172a")
    draw.text((20, 16), "LEGAL METROLOGY PACKAGING LABEL SAMPLE", fill="#38bdf8")

    # Draw label declaration text lines
    y = 70
    for i, line in enumerate(definition["lines"]):
        if i == 0:
            draw.text((30, y), line, fill="#0f172a")
            y += 35
        elif "MRP" in line or "Net" in line:
            draw.text((30, y), line, fill="#1e293b")
            y += 32
        else:
            draw.text((30, y), line, fill="#334155")
            y += 30

    # Outer border
    draw.rectangle([(10, 10), (690, 470)], outline="#cbd5e1", width=2)
    return img


def ensure_sample_labels(samples_folder=None, force=False):
    """
    Ensures that preset label sample images exist in the specified directory.
    If images are missing or force is True, renders them with Pillow.
    """
    folder = samples_folder or Config.SAMPLES_FOLDER
    os.makedirs(folder, exist_ok=True)

    created_files = []
    for item in SAMPLE_DEFINITIONS:
        target_path = os.path.join(folder, item["filename"])
        if force or not os.path.exists(target_path):
            img = render_label_image(item)
            img.save(target_path, format="PNG")
            created_files.append(target_path)
            logger.info(f"Generated sample label image: {target_path}")

    return created_files
