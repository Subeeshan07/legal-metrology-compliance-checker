# Legal Metrology Packaged Commodity Compliance Checker

An automated regulatory surveillance and compliance assessment web application designed for analyzing packaged food product labels in accordance with the **Legal Metrology (Packaged Commodities) Rules, 2011 (India)** and the **Legal Metrology Act, 2009**.

Built for demonstration and evaluation in **Smart India Hackathon (SIH)**.

---

## 🏛️ Regulatory Context: Legal Metrology (Packaged Commodities) Rules, 2011

Under **Section 18 of the Legal Metrology Act, 2009** and **Rule 6 of the Legal Metrology (Packaged Commodities) Rules, 2011**, all pre-packaged commodities offered for retail sale in India must bear mandatory statutory declarations on the Principal Display Panel (PDP).

The compliance engine checks the 7 mandatory statutory declarations:

| Statutory Provision | Mandatory Declaration | Verification Standard |
|---|---|---|
| **Rule 6(1)(a)** | Manufacturer / Packer / Importer | Name and complete physical address including postal PIN code |
| **Rule 6(1)(b)** | Common / Generic Commodity Name | Clear, prominent generic naming of the packaged food |
| **Rule 6(1)(c) & Rule 13** | Net Quantity & Standard SI Units | Metric SI units only (`g`, `kg`, `ml`, `l`/`L`, `N`). Rejects non-standard symbols (`gms`, `gm`, `ML`, `ltr`) |
| **Rule 6(1)(d)** | Month & Year of Mfg / Packing | Legible manufacturing date (e.g., `04/2026` or `April 2026`) |
| **Rule 6(1)(da)** | Maximum Retail Price (MRP) | Format: `MRP Rs. XX.XX (incl. of all taxes)` or `₹ XX.XX (inclusive of all taxes)` |
| **Rule 6(1)(e)** | Consumer Care Grievance Redressal | Both an active customer telephone helpline AND an official email address |
| **Rule 6(1)(n)** | Country of Origin | Explicit declaration of country of origin (mandatory for domestic and imported goods) |

---

## 🚀 Key Features

1. **Executive Dashboard**:
   - Live KPI summary counters: Total scanned, Compliant, Non-Compliant, Needs Review.
   - **Chart.js Doughnut Chart**: Proportion of compliant vs non-compliant packages.
   - **Chart.js Horizontal Bar Chart**: Top statutory declaration violations across the surveillance pool.
   - Quick-access table of recent product inspections.

2. **Optical Character Recognition (OCR) Product Scanner**:
   - Drag-and-drop or file upload for product packaging label photographs.
   - **Tesseract OCR integration** with Pillow-based image enhancement (contrast scaling, noise reduction, grayscale conversion).
   - **One-Click Quick Test Sample Presets**:
     - *Compliant Whole Wheat Atta* (Passes all 7 statutory declarations)
     - *Non-Compliant Potato Chips* (Missing tax clause, consumer care, and origin)
     - *Needs Review Chilli Powder* (Uses non-standard abbreviation `gms` instead of `g`, incomplete street address)
   - Extracted text inspection editor (allows review and manual correction of OCR readings).
   - Automatic entity extraction for Product Name, Net Qty, MRP, Mfg Date, Manufacturer, Consumer Care, and Country of Origin.
   - Rule-by-rule statutory checklist and legal recommendations.
   - **"Save to Records"** feature that updates the dataset and dashboard in real-time.

3. **Product History & Surveillance Database**:
   - Searchable across product name, manufacturer name, ID, or violation type.
   - Filterable by compliance status (`COMPLIANT`, `NON-COMPLIANT`, `NEEDS REVIEW`) and product category.
   - Pagination controls.
   - **"Export Filtered CSV"** button for surveillance officers.

4. **Official Inspection Audit Sheet & Report**:
   - Clean printable formal certificate with Department of Consumer Affairs styling.
   - Formatted for A4 printing via standard `Ctrl+P` or **Print / Save as PDF** button (`window.print()`).
   - Includes inspector signature blocks, QR reference, and statutory disclaimer.

5. **Synthetic Dataset (1,150+ Records)**:
   - Programmatically generated dataset with realistic packaging data across 10 food categories.
   - *Disclaimer: Generated for demonstration and prototype testing; does not represent real market surveillance proceedings.*

---

## 📁 Project Structure

```
legal_metrology_checker/
├── app.py                      # Flask backend, OCR pipeline & compliance rule engine
├── requirements.txt            # Python dependencies
├── generate_dataset.py         # Synthetic dataset generator script (1,150+ records)
├── legal_metrology_dataset.csv # Surveillance dataset (1,150+ pre-generated records)
├── test_app.py                 # Automated unit and integration test suite
├── templates/
│   └── index.html              # Clean SIH dashboard, scanner, and audit report UI
├── static/
│   ├── style.css               # Modern responsive styling and @media print layout
│   ├── script.js              # Chart.js visualisations, dropzone, OCR runner, search
│   └── samples/                # Pre-rendered sample packaging labels for testing
└── uploads/                    # Directory for user-uploaded packaging images
```

---

## ⚙️ Prerequisites & Installation

### 1. Python Environment
Make sure Python 3.9+ is installed on your machine.

Open PowerShell or Terminal and navigate to the project directory:
```bash
cd "legal_metrology_checker"
```

Create and activate a virtual environment (recommended):
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

---

### 2. (Optional but Recommended) Tesseract OCR Installation

The application includes automatic Tesseract OCR detection across system PATH and default Windows installation folders. If Tesseract binary is not installed, the app automatically switches to **Hybrid Assisted Mode**, allowing you to test with the 1-click sample presets or paste/edit label text without crashing.

To enable full local image OCR on custom packaging photos:

#### On Windows:
1. Download the Windows installer from [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer and install to the default location: `C:\Program Files\Tesseract-OCR`.
3. Add `C:\Program Files\Tesseract-OCR` to your Windows system `PATH` environment variable.

Alternatively via `winget`:
```powershell
winget install UB-Mannheim.TesseractOCR
```

#### On Ubuntu / Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### On macOS (Homebrew):
```bash
brew install tesseract
```

---

## 🏃 Running the Application

### 1. (Optional) Re-generate Dataset
The repository already includes `legal_metrology_dataset.csv` with 1,150 records. If you ever want to re-generate the dataset:
```bash
python generate_dataset.py
```

### 2. Run Automated Verification Tests
```bash
python test_app.py
```

### 3. Start the Flask Server
```bash
python app.py
```

Output will display:
```
Starting Legal Metrology Packaged Commodity Compliance Checker on http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Quick Demonstration Steps for Hackathon Judges

1. **View the Dashboard**:
   - Observe live total scans (1,150+), compliance percentages, and the **Chart.js** Doughnut and Horizontal Bar charts.

2. **Test the Product Scanner**:
   - Click the **"Product Scanner"** tab.
   - Click **"Compliant Atta"** under *Quick Test Sample Presets*. Notice how all 7 mandatory declarations are extracted and marked green **COMPLIANT**.
   - Click **"Non-Compliant Snack"** preset. Notice how the missing tax clause and missing consumer care triggers a red **NON-COMPLIANT** banner with specific rule citations.
   - Click **"Needs Review Spice"** preset. Notice how the non-standard unit `gms` is flagged for manual review with a yellow **NEEDS REVIEW** badge.
   - Click **"Save to Records"** to dynamically register the scan into the database.

3. **Inspect Product History**:
   - Switch to **"Product History"** tab.
   - Filter by status or type in the live search box (e.g. `Mustard Oil` or `Kashmiri`).
   - Click **"Audit"** on any row to open the formal **Department of Consumer Affairs Compliance Certificate**.
   - Click **"Export Filtered CSV"** to download the current surveillance registry.

4. **Print / Export Report**:
   - From the Audit modal, click **"Print / Save as PDF"** to view the clean printable inspection sheet.

---

## 📜 Legal Disclaimer
This software is an AI and rules-assisted decision support prototype developed for academic and hackathon evaluation. The bundled dataset `legal_metrology_dataset.csv` is completely synthetic and generated for demonstration purposes. It does not represent actual market surveillance inspections or enforcement actions against any commercial entity.
