# Legal Metrology Compliance Checker & Food Counterfeit Risk Intelligence System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Framework-Flask%203.0-green.svg)](https://flask.palletsprojects.com/)
[![Tesseract OCR](https://img.shields.io/badge/OCR-Tesseract%205.x-orange.svg)](https://github.com/tesseract-ocr/tesseract)
[![Tests Passing](https://img.shields.io/badge/Tests-130%20Passing-brightgreen.svg)]()
[![Docker Ready](https://img.shields.io/badge/Deployment-Docker%20%7C%20Gunicorn-blue.svg)]()

An enterprise regulatory surveillance and intelligence web platform designed to analyze packaged food product labels in accordance with the **Legal Metrology (Packaged Commodities) Rules, 2011 (India)** while simultaneously evaluating **Food Counterfeit Risk** using multi-signal computer vision, brand squatting detection, and GS1 GTIN-13 barcode verification.

---

## 🏛️ Regulatory Context & Core Philosophy

Under **Section 18 of the Legal Metrology Act, 2009** and **Rule 6 of the Legal Metrology (Packaged Commodities) Rules, 2011**, all pre-packaged commodities offered for retail sale in India must bear mandatory statutory declarations on the Principal Display Panel (PDP).

### Key Architectural Principle: Decoupled Dual Outcomes
A genuine product packaging may occasionally exhibit minor labeling non-compliance (e.g., omitting "incl. of all taxes"), while a sophisticated counterfeit package may flawlessly copy statutory text. 

Therefore, this platform enforces a **strict separation of final verdicts**:
1. **Outcome 1: Legal Metrology Compliance** (`COMPLIANT`, `NEEDS REVIEW`, `NON-COMPLIANT`)
2. **Outcome 2: Food Counterfeit Risk** (`LOW`, `MEDIUM`, `HIGH`)

---

## 🚀 Key Platform Capabilities

### 1. Unified Analysis Pipeline (`AnalysisOrchestrator`)
- **Stage 1: Image Quality Assessment**: Real-time evaluation of Laplacian blur variance, luminance, and specular glare ratio before OCR execution.
- **Stage 2: OCR Preprocessing & Word Confidence**: Grayscale scaling, contrast enhancement, Otsu thresholding, and word-level confidence derivation.
- **Stage 3: Entity Extraction & Normalization**: Extracts declarations and normalizes units (`250 g` -> `250.0 g`), currencies, and dates (`Packed during 06/2026` -> `06/2026`).
- **Stage 4: Modular Rule Engine (PCR, 2011)**: Independent statutory rules under `rules/` for Rule 6(1)(a)-(n) and Rule 13.
- **Stage 5: Multi-Signal Counterfeit Risk Engine**:
  - *Brand Squatting & Typo Inspection* (`Himalyan`, `Amool`, `Pristeen`).
  - *Authorized Manufacturer Verification* against verified producer facilities.
  - *GS1 GTIN-13 Barcode Checksum* (Modulo-10) and brand registration check.
  - *Packaging Principal Display Panel (PDP) Layout Consistency*.
- **Stage 6: Unified Surveillance Report & Audit Logging**: Records detailed JSON audit logs into persistent SQLite storage.

### 2. Dual-Outcome Executive Dashboard & Scanner UI
- Glassmorphic, modern dashboard featuring live KPI counters and **Chart.js** distribution graphs.
- Unified scanner supporting drag-and-drop packaging photos, GTIN-13 barcode entry, and ground-truth sample presets.
- Dual-verdict status banners presenting Legal Metrology results side-by-side with Counterfeit Risk score gauges.
- Official printable **Surveillance Inspection Audit Sheet** formatted for A4 PDF export with Department of Consumer Affairs styling.

### 3. Persistent Storage & Dual Synchronization
- Relational **SQLite** backend (`data/food_compliance.db`) storing full scan audit logs and entity history.
- Automatic migration and bidirectional mirroring with `legal_metrology_dataset.csv` (1,150+ synthetic surveillance records).

### 4. Golden Evaluation Dataset & Benchmark Metrics
- Ground-truth evaluation dataset (`tests/golden_dataset/golden_compliance_labels.json`).
- Automated evaluation script (`scripts/evaluate_benchmarks.py`) validating:
  - **100.0% Compliance Classification Accuracy**
  - **100.0% Counterfeit Risk Accuracy**
  - **100.0% Field-Level Extraction Accuracy**
  - **0.0% False Compliance Rate (FCR)**

### 5. Production Hardening & Security
- **Security Headers Middleware**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection`, `Referrer-Policy`.
- **MIME & Magic Byte Validation**: Inspects binary headers to reject disguised scripts and malicious uploads.
- **In-Memory Rate Limiting**: Sliding-window rate limiter protecting OCR endpoints from DoS abuse (30 scans/min per IP).
- **Health Endpoint**: `/health` reporting service status, database health, and OCR readiness.

---

## 🛠️ Repository Structure

```
legal-metrology-compliance-checker/
├── app.py                      # Application factory (create_app)
├── wsgi.py                     # Production WSGI entry point
├── Dockerfile                  # Production container definition (Tesseract + Gunicorn)
├── docker-compose.yml          # Container orchestration configuration
├── requirements.txt            # Python dependencies
├── config/
│   └── settings.py             # Central application configuration & paths
├── models/
│   ├── enums.py                # ComplianceStatus, CounterfeitRisk, ImageQualityGrade
│   ├── compliance.py           # RuleEvaluation, ComplianceReport, Normalization models
│   └── product.py              # ScannedProductRecord, ReferenceProduct models
├── rules/
│   ├── base_rule.py            # Abstract BaseRule interface
│   ├── manufacturer_rule.py    # Rule 6(1)(a) - Name & address of manufacturer
│   ├── product_name_rule.py    # Rule 6(1)(b) - Generic commodity name
│   ├── net_quantity_rule.py    # Rule 6(1)(c) & Rule 13 - Net quantity & SI units
│   ├── mfg_date_rule.py        # Rule 6(1)(d) - Month & year of manufacture
│   ├── mrp_rule.py             # Rule 6(1)(da) - MRP & inclusive of all taxes clause
│   ├── consumer_care_rule.py   # Rule 6(1)(e) - Grievance officer email & phone
│   ├── country_of_origin_rule.py # Rule 6(1)(n) - Country of origin declaration
│   └── rule_registry.py        # Dynamic rule registry & orchestrator
├── services/
│   ├── analysis_orchestrator.py # Unified end-to-end analysis pipeline
│   ├── image_quality_service.py # Blur, lighting, and glare assessment
│   ├── ocr_service.py          # Pluggable OCR engine & confidence scoring
│   ├── extraction_service.py   # Declaration entity parsing
│   ├── normalization_service.py# Structured metric normalization
│   ├── compliance_service.py   # Legal Metrology evaluation service
│   ├── counterfeit_service.py  # Food Counterfeit Risk scoring engine
│   ├── product_identification_service.py # Brand matching & reference identification
│   ├── barcode_service.py      # GS1 GTIN-13 checksum & brand registration
│   ├── packaging_layout_service.py # Spatial layout & PDP consistency
│   └── sample_service.py       # Ground-truth sample preset generation
├── repositories/
│   ├── product_repository.py   # Product catalog persistence interface
│   ├── database_repository.py  # SQLite persistence & scan audit logging
│   └── reference_repository.py # Genuine brand knowledge base access
├── routes/
│   ├── web_routes.py           # Web UI views
│   ├── scan_routes.py          # /api/scan, /api/scans, /api/save
│   ├── product_routes.py       # /api/products
│   ├── analytics_routes.py     # /api/stats
│   └── rules_routes.py         # /api/rules
├── scripts/
│   └── evaluate_benchmarks.py  # Golden dataset benchmarking & metrics script
├── tests/
│   ├── golden_dataset/         # Ground truth verified test cases
│   ├── test_compliance_engine_v2.py
│   ├── test_counterfeit_detection.py
│   ├── test_database_repository.py
│   ├── test_frontend.py
│   ├── test_golden_evaluation.py
│   ├── test_ocr_improvements.py
│   ├── test_regression_baseline.py
│   ├── test_routes.py
│   ├── test_security_hardening.py
│   └── test_unified_pipeline.py
└── docs/                       # Technical & architectural specifications
```

---

## ⚡ Quick Start

### 1. Local Development Setup
```bash
# Clone the repository
git clone https://github.com/Subeeshan07/legal-metrology-compliance-checker.git
cd legal-metrology-compliance-checker

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # On Windows
source .venv/bin/activate  # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Launch development server
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

### 2. Running Automated Tests & Evaluation Benchmarks
```bash
# Run complete regression test suite (130 tests)
python -m unittest discover -s tests -v

# Run golden dataset quality benchmark
python scripts/evaluate_benchmarks.py
```

---

### 3. Production Deployment with Docker
```bash
docker compose up --build -d
```
Verify the live health endpoint:
```bash
curl http://localhost:5000/health
```

---

## 📖 Documentation
Detailed technical guides are available in the [`docs/`](docs/) directory:
- [System Architecture Specification](docs/architecture/system_architecture.md)
- [REST API Reference](docs/api_reference.md)
- [Legal Metrology Compliance Methodology](docs/compliance_methodology.md)
- [Food Counterfeit Risk Methodology](docs/counterfeit_methodology.md)
- [Production Deployment Guide](docs/deployment_guide.md)

---

## ⚖️ License & Statutory Disclaimer
Developed for regulatory surveillance demonstration and evaluation in the **Smart India Hackathon (SIH)**. Synthetic demonstration dataset does not represent active commercial enforcement actions.
