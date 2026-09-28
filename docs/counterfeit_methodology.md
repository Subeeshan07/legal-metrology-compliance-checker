# Food Counterfeit Risk Intelligence Methodology

## Motivation & Core Principle
A genuine product packaging may occasionally exhibit minor regulatory non-compliance (e.g., omitting "incl. of all taxes" on MRP), while a sophisticated counterfeit package may flawlessly replicate statutory wording.

Therefore, this platform enforces a **strict decoupling of outcomes**:
- **Outcome 1: Legal Metrology Compliance** (`COMPLIANT`, `NEEDS REVIEW`, `NON-COMPLIANT`)
- **Outcome 2: Food Counterfeit Risk** (`LOW`, `MEDIUM`, `HIGH`)

---

## Multi-Signal Risk Detection Architecture

The `FoodCounterfeitRiskEngine` synthesizes multiple independent verification signals:

### 1. Brand Squatting & Typo Inspection
- **Objective:** Detects visual typos, optical character duplications, and trademark squatting (e.g. `Himalyan` instead of `Himalayan`, `Amool` instead of `Amul`, `Pristeen` instead of `Pristine`).
- **Algorithm:**
  - Tokenized fuzzy distance & exact word-boundary regex (`\b{typo}\b`).
  - Detection of a known squatting pattern adds **+40.0%** to the cumulative risk score.

### 2. Authorized Manufacturer Verification
- **Objective:** Cross-references the declared manufacturing entity and facility address against verified genuine producer registries.
- **Algorithm:**
  - If a brand is identified, the engine checks whether the declared manufacturer matches authorized packager profiles.
  - An unauthorized manufacturer for a recognized brand adds **+20.0%** to the risk score.

### 3. GS1 GTIN-13 Barcode Verification
- **Objective:** Validates whether the 13-digit EAN-13 / GTIN-13 barcode adheres to official GS1 specifications and matches the identified brand.
- **Algorithm:**
  - **Modulo 10 Checksum Algorithm**:
    $$\text{Checksum} = \left(10 - \left(\sum_{i=1}^{12} d_i \times w_i \pmod{10}\right)\right) \pmod{10}$$
    where weights $w_i$ alternate between 1 and 3.
  - Invalid checksum: **+40.0%** risk score.
  - Checksum valid but unregistered to brand: **+25.0%** risk score.
  - Exact match to brand variant: **Positive genuine signal**.

### 4. Price & Variant Anomaly Detection
- **Objective:** Identifies predatory discount counterfeiting or severe retail price deviations.
- **Algorithm:**
  - Compares normalized declared MRP against registered genuine MSRP ranges for the matched package net weight.
  - Severe deviation (>30% below registered baseline): **+20.0%** risk score.

### 5. Principal Display Panel (PDP) Layout Consistency
- **Objective:** Assesses spatial distribution and element balance on the packaging.
- **Algorithm:**
  - Evaluates spatial distribution across quadrants to ensure brand name, net quantity, and certification marks are positioned according to packaging standards.
  - Anomalous distribution adds **+15.0%** risk score.

---

## Risk Tier Classification
| Risk Tier | Score Range | Operational Meaning | Action Recommendation |
|---|---|---|---|
| **LOW** | $0\% - 24\%$ | Packaging specifications and markings align with genuine reference data. | Release for retail distribution. |
| **MEDIUM** | $25\% - 49\%$ | Minor anomalies (e.g. unverified packer unit or barcode ambiguity). | Secondary inspection or physical batch audit. |
| **HIGH** | $50\% - 100\%$ | High probability of fraudulent packaging (brand squatting, fake barcode). | Immediate quarantine and report to enforcement officers. |
