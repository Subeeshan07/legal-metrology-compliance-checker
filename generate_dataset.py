"""
Synthetic Dataset Generator for Legal Metrology Packaged Commodity Compliance Checker
Legal Metrology (Packaged Commodities) Rules, 2011 (India)

DISCLAIMER:
This dataset is synthetic and programmatically generated for demonstration, testing,
and educational evaluation in the Smart India Hackathon. It does NOT represent real
market surveillance data or official enforcement proceedings against any entity.
"""

import csv
import random
from datetime import datetime, timedelta

# Categories & Realistic Product Names
CATEGORIES = {
    "Atta & Flours": [
        "Sharbati Whole Wheat Atta", "Multigrain Fibre Atta", "Chakki Fresh Pure Atta",
        "Organic Besan Gram Flour", "Rice Flour Fine", "Ragi Millet Flour", "Maida Refined Wheat Flour"
    ],
    "Biscuits & Cookies": [
        "Crispy Butter Cookies", "Digestive High Fibre Biscuits", "Choco Chip Delight Cookies",
        "Marie Crisp Tea Biscuits", "Bourbon Chocolate Cream Biscuits", "Almond Cashew Shortbread", "Salted Crackers"
    ],
    "Dairy Products": [
        "Pasteurized Cow Ghee", "Standardized Tonned Milk", "Pure Malai Paneer",
        "Salted Table Butter", "Greek Style Plain Yogurt", "Sterilized Flavoured Milk"
    ],
    "Edible Oils": [
        "Cold Pressed Mustard Oil", "Refined Sunflower Cooking Oil", "Virgin Cold Pressed Coconut Oil",
        "Refined Groundnut Oil", "Blended Edible Vegetable Oil", "Pure Sesame Gingelly Oil"
    ],
    "Spices & Condiments": [
        "Kashmiri Degi Mirch Powder", "Agmark Haldi Turmeric Powder", "Coriander Dhania Powder",
        "Royal Garam Masala Blend", "Whole Cumin Jeera Seeds", "Black Mustard Seeds", "Kasuri Methi"
    ],
    "Snacks & Namkeen": [
        "Spicy Aloo Bhujia", "Roasted Salted Makhana", "Crunchy Moong Dal Namkeen",
        "Khatta Meetha Mixture", "Masala Potato Wafers", "Tangy Tomato Nacho Chips", "Diet Murmura Mix"
    ],
    "Beverages & Juices": [
        "100% Valencia Orange Juice", "Alphonso Mango Nectar", "Mixed Fruit Orchard Blend",
        "Sparkling Apple Cider Drink", "Tender Coconut Water Drink", "Lemon Iced Tea Concentrate"
    ],
    "Ready-to-Eat": [
        "Instant Masala Noodles", "Dal Makhani Heat & Eat Meal", "Rava Upma Breakfast Mix",
        "Poha Instant Breakfast Bowl", "Palak Paneer Ready Curry", "Gulab Jamun Instant Mix"
    ],
    "Chocolates & Confectionery": [
        "Dark Silk Chocolate Bar", "Roasted Almond Milk Bar", "Caramel Toffee Pouch",
        "Mint Peppermint Lozenges", "Fruit Jelly Chews Pouch"
    ],
    "Tea & Coffee": [
        "Premium Assam CTC Tea", "Darjeeling Whole Leaf Black Tea", "Roasted Arabica Coffee Beans",
        "Instant Chicory Coffee Powder", "Green Tea Lemon Honey Bags"
    ]
}

MANUFACTURERS = [
    {"name": "Ananya Consumer Goods Ltd", "addr": "Plot 42, Sector 8, IMT Manesar, Gurugram, Haryana - 122050", "city": "Gurugram"},
    {"name": "Vedic Agro Industries Pvt Ltd", "addr": "Gat No. 118, Urse, Talegaon MIDC, Pune, Maharashtra - 410506", "city": "Pune"},
    {"name": "Pristine Foods & Agro Ltd", "addr": "Phase 2, Peenya Industrial Area, Bengaluru, Karnataka - 560058", "city": "Bengaluru"},
    {"name": "Kaveri Spices & Naturals", "addr": "14/B, Spice Park, Puttady, Idukki, Kerala - 685551", "city": "Idukki"},
    {"name": "Surya Packaged Commodities LLP", "addr": "Industrial Growth Centre, Mandideep, Bhopal, MP - 462046", "city": "Bhopal"},
    {"name": "Godavari Mills & Refineries", "addr": "Sy. No. 340, Autonagar, Guntur, Andhra Pradesh - 522001", "city": "Guntur"},
    {"name": "Himalayan Organic Ventures", "addr": "SIDCUL Industrial Estate, Pantnagar, Uttarakhand - 263153", "city": "Pantnagar"},
    {"name": "Navrang Agro Commodities Corp", "addr": "GIDC Naroda, Ahmedabad, Gujarat - 382330", "city": "Ahmedabad"}
]

STANDARD_UNITS = {
    "weight_kg": ["1 kg", "2 kg", "5 kg", "10 kg"],
    "weight_g": ["50 g", "100 g", "200 g", "250 g", "400 g", "500 g", "750 g"],
    "volume_l": ["1 L", "2 L", "5 L"],
    "volume_ml": ["100 ml", "200 ml", "250 ml", "500 ml", "750 ml"],
    "count": ["10 N", "25 N", "50 N"]
}

VIOLATION_TYPES = [
    ("Rule 6(1)(da)", "Missing 'Inclusive of all taxes' declaration with MRP", "Non-Compliant"),
    ("Rule 6(1)(c)", "Non-standard unit abbreviation used ('gms' / 'gm' instead of standard 'g')", "Needs Review"),
    ("Rule 6(1)(c)", "Non-standard unit abbreviation used ('ML' / 'ltr' instead of 'ml' / 'L')", "Needs Review"),
    ("Rule 6(1)(e)", "Missing consumer care email address", "Needs Review"),
    ("Rule 6(1)(e)", "Complete consumer care grievance contact details missing", "Non-Compliant"),
    ("Rule 6(1)(n)", "Missing Country of Origin declaration", "Non-Compliant"),
    ("Rule 6(1)(a)", "Physical address of manufacturer incomplete (missing PIN code/city)", "Needs Review"),
    ("Rule 6(1)(a)", "Manufacturer/packer declaration entirely missing", "Non-Compliant"),
    ("Rule 6(1)(d)", "Month and year of manufacture/packing missing", "Non-Compliant"),
    ("Rule 6(1)(c)", "Net quantity declaration absent", "Non-Compliant"),
    ("Rule 6(1)(da)", "Maximum Retail Price (MRP) declaration absent", "Non-Compliant"),
    ("Rule 7", "Font size / unit symbol ambiguous or truncated under OCR", "Needs Review")
]

def generate_record(rec_id):
    category = random.choice(list(CATEGORIES.keys()))
    base_prod = random.choice(CATEGORIES[category])
    mfr_info = random.choice(MANUFACTURERS)
    
    # Decide compliance category: 58% Compliant, 28% Non-Compliant, 14% Needs Review
    roll = random.random()
    if roll < 0.58:
        status = "COMPLIANT"
    elif roll < 0.86:
        status = "NON-COMPLIANT"
    else:
        status = "NEEDS REVIEW"

    # Base valid attributes
    if category in ["Edible Oils", "Beverages & Juices"]:
        if random.random() < 0.6:
            unit_str = random.choice(STANDARD_UNITS["volume_ml"])
        else:
            unit_str = random.choice(STANDARD_UNITS["volume_l"])
    elif category == "Atta & Flours":
        unit_str = random.choice(STANDARD_UNITS["weight_kg"])
    else:
        unit_str = random.choice(STANDARD_UNITS["weight_g"])

    prod_name = f"{base_prod} {unit_str}"
    manufacturer = f"{mfr_info['name']}, {mfr_info['addr']}"
    
    # Net quantity
    net_quantity = unit_str
    
    # MRP
    mrp_val = random.randint(25, 950)
    mrp = f"Rs. {mrp_val}.00 (Incl. of all taxes)"
    
    # Mfg Date
    random_days = random.randint(15, 240)
    mfg_dt = datetime.now() - timedelta(days=random_days)
    mfg_date = mfg_dt.strftime("%m/%Y")
    
    # Consumer care
    short_slug = mfr_info['name'].lower().split()[0]
    consumer_care = f"Email: care@{short_slug}.com | Ph: 1800-{random.randint(100,999)}-{random.randint(1000,9999)}"
    
    # Country of origin
    country_of_origin = "India" if random.random() < 0.95 else "Imported (Origin: Sri Lanka)"
    
    violations = []
    ocr_confidence = f"{random.randint(88, 99)}%"

    if status == "NON-COMPLIANT":
        ocr_confidence = f"{random.randint(75, 96)}%"
        # Select 1 or 2 serious violations
        sample_violations = [v for v in VIOLATION_TYPES if v[2] == "Non-Compliant"]
        chosen = random.sample(sample_violations, k=random.choice([1, 2]))
        for rule, desc, _ in chosen:
            violations.append(f"{rule}: {desc}")
            # Corrupt the corresponding field
            if "MRP" in desc or "taxes" in desc:
                if "absent" in desc:
                    mrp = "Not Declared"
                else:
                    mrp = f"Rs. {mrp_val}.00"  # Missing inclusive of all taxes
            elif "Country of Origin" in desc:
                country_of_origin = "Not Declared"
            elif "consumer care" in desc.lower():
                consumer_care = "Not Declared"
            elif "manufacturer" in desc.lower():
                manufacturer = "Not Declared"
            elif "manufacture/packing" in desc.lower():
                mfg_date = "Not Declared"
            elif "Net quantity" in desc:
                net_quantity = "Not Declared"

    elif status == "NEEDS REVIEW":
        ocr_confidence = f"{random.randint(62, 85)}%"
        review_violations = [v for v in VIOLATION_TYPES if v[2] == "Needs Review"]
        chosen = random.sample(review_violations, k=random.choice([1, 2]))
        for rule, desc, _ in chosen:
            violations.append(f"{rule}: {desc}")
            if "'gms'" in desc:
                net_quantity = net_quantity.replace(" g", " gms").replace(" kg", " kgs")
            elif "'ML'" in desc:
                net_quantity = net_quantity.replace(" ml", " ML").replace(" L", " ltr")
            elif "email address" in desc:
                consumer_care = f"Helpline: 1800-{random.randint(100,999)}-{random.randint(1000,9999)} (Email missing)"
            elif "Physical address" in desc:
                manufacturer = f"{mfr_info['name']}, {mfr_info['city']}"  # Missing full street address & PIN
            elif "Font size" in desc:
                # Ambiguous OCR scan
                ocr_confidence = f"{random.randint(58, 72)}%"

    scan_dt = datetime.now() - timedelta(days=random.randint(0, 60), minutes=random.randint(5, 1400))
    scanned_timestamp = scan_dt.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "id": f"LMC-{rec_id:05d}",
        "product_name": prod_name,
        "category": category,
        "manufacturer": manufacturer,
        "net_quantity": net_quantity,
        "mrp": mrp,
        "mfg_date": mfg_date,
        "consumer_care": consumer_care,
        "country_of_origin": country_of_origin,
        "compliance_status": status,
        "violations": "; ".join(violations) if violations else "None (Fully Compliant with Rule 6)",
        "scanned_timestamp": scanned_timestamp,
        "ocr_confidence": ocr_confidence
    }

def main():
    total_records = 1150
    output_file = "legal_metrology_dataset.csv"
    
    headers = [
        "id", "product_name", "category", "manufacturer", "net_quantity",
        "mrp", "mfg_date", "consumer_care", "country_of_origin",
        "compliance_status", "violations", "scanned_timestamp", "ocr_confidence"
    ]
    
    records = [generate_record(i) for i in range(1001, 1001 + total_records)]
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Successfully generated {len(records)} synthetic records in '{output_file}'.")
    
    # Display summary statistics
    statuses = {}
    for r in records:
        statuses[r["compliance_status"]] = statuses.get(r["compliance_status"], 0) + 1
    for st, count in statuses.items():
        pct = (count / len(records)) * 100
        print(f" - {st}: {count} records ({pct:.1f}%)")

if __name__ == "__main__":
    main()
