# Legal Metrology Compliance Methodology

## Regulatory Framework
This platform executes algorithmic verification against mandatory declarations under the **Legal Metrology Act, 2009** and the **Legal Metrology (Packaged Commodities) Rules, 2011 (PCR, 2011)** promulgated by the Department of Consumer Affairs, Government of India.

---

## Statutory Rules Evaluated

### 1. Rule 6(1)(a) — Manufacturer, Packer, or Importer Details
- **Mandate:** Every packaged commodity must state the complete legal entity name and physical address of the manufacturer, packer, or importer.
- **Verification Routine:**
  - Evaluates presence of company identifier (`Ltd`, `Pvt Ltd`, `LLP`, `Industries`, `Enterprises`).
  - Verifies physical location indicators (Road, Street, Phase, MIDC, Industrial Area) and 6-digit postal PIN code.
  - Flags incomplete or ambiguous abbreviations as `NEEDS REVIEW`. Absence is classified as `NON-COMPLIANT`.

### 2. Rule 6(1)(b) — Generic / Common Name of Commodity
- **Mandate:** The container must clearly display the generic or common commercial name of the commodity on the Principal Display Panel (PDP).
- **Verification Routine:**
  - Matches commodity against standard food categorization dictionaries (Atta, Rice, Spices, Edible Oil, Confectionery, Tea).

### 3. Rule 6(1)(c) & Rule 13 — Net Quantity & Standard Measurement Units
- **Mandate:** Net weight or measure must be declared in standard SI metric units (`g`, `kg`, `ml`, `l`, `m`).
- **Verification Routine:**
  - Checks for non-standard colloquial abbreviations (e.g. `gm`, `gms`, `kilo`, `ltr`, `mls`).
  - Converts and normalizes quantities into structured metric values (e.g. `250 g` -> `250.0 g`).
  - Non-standard units trigger `NEEDS REVIEW` with a corrective citation to Rule 13.

### 4. Rule 6(1)(d) — Date of Manufacture / Packing
- **Mandate:** The month and year in which the commodity is manufactured, packed, or pre-packed must be clearly declared (`MM/YYYY` or month name and year).
- **Verification Routine:**
  - Parses dates from diverse declarations (`Mfg Date`, `PKD`, `Packed during 06/2026`).
  - Validates that date is not set in an impossible future year and conforms with the two/four digit statutory syntax.

### 5. Rule 6(1)(da) — Maximum Retail Price (MRP) & Tax Clause
- **Mandate:** The retail sale price must state the Maximum Retail Price in Indian Rupees accompanied by the mandatory phrase **"Inclusive of all taxes"** or **"(Incl. of all taxes)"**.
- **Verification Routine:**
  - Extracts numeric currency values.
  - Strictly asserts the presence of the inclusive tax disclaimer. Missing tax disclaimer triggers an explicit `NON-COMPLIANT` statutory violation under Section 36.

### 6. Rule 6(1)(e) — Consumer Care Grievance Redressal
- **Mandate:** Every package must provide the name, physical address, telephone number, and email address of the consumer grievance redressal officer.
- **Verification Routine:**
  - Asserts email address regex (`[\w\.-]+@[\w\.-]+\.\w+`).
  - Asserts telephone/toll-free helpline number regex (`1800-XXX-XXXX` or 10-digit number).
  - Missing email or phone triggers `NEEDS REVIEW` or statutory violation.

### 7. Rule 6(1)(n) — Country of Origin
- **Mandate:** Mandatory declaration of the country of origin for imported and domestic commodities alike.
- **Verification Routine:**
  - Detects explicit origin statements (`Made in India`, `Country of Origin: India`).
