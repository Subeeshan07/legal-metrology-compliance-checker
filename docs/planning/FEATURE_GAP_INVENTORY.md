\# Feature \& Gap Inventory



\*\*Project:\*\* Legal Metrology Packaged Commodity Compliance Checker  

\*\*Task:\*\* 0.2 — Existing Feature and Gap Inventory  

\*\*Baseline:\*\* `v0.1-prototype`  

\*\*Purpose:\*\* Identify what the current prototype already provides, what is partial,

and what must be implemented to evolve it into a robust AI-assisted compliance

platform.



---



\## 1. Current Prototype Capabilities



\### Backend

\- Flask-based web application.

\- Product label image upload.

\- Tesseract OCR integration.

\- Basic image preprocessing using Pillow.

\- Manual correction of OCR-extracted text.

\- Rule-based compliance checking.

\- Entity extraction from label text.

\- CSV-based inspection record storage.

\- Dashboard/statistics APIs.

\- Search and filtering.

\- CSV export.

\- Audit/report generation.



\### Compliance Checks

The current prototype evaluates declarations including:



1\. Manufacturer / packer / importer details.

2\. Common or generic commodity name.

3\. Net quantity and units.

4\. Manufacturing / packing date.

5\. Maximum Retail Price (MRP).

6\. Consumer-care information.

7\. Country of origin.



\### Frontend

\- Dashboard.

\- Product scanner.

\- Drag-and-drop/file upload.

\- Sample product presets.

\- Extracted-text editor.

\- Compliance result display.

\- Product history.

\- Search/filter controls.

\- Audit/report view.

\- Printable report.



\### Dataset

\- Synthetic Legal Metrology dataset.

\- Multiple packaged-food categories.

\- Compliance statuses.

\- Sample product label images.



\### Testing

\- Existing automated application tests.

\- Tests for several backend and compliance behaviours.



---



\# 2. Gap Classification



Each identified item is classified as:



\- \*\*Implemented\*\* — sufficiently present in the prototype.

\- \*\*Partial\*\* — functionality exists but requires improvement.

\- \*\*Missing\*\* — functionality needs to be developed.

\- \*\*Technical Debt\*\* — implementation should be restructured or hardened.



---



\# 3. Software Architecture Gaps



\## 3.1 Monolithic Backend



\*\*Status:\*\* Technical Debt



A large portion of the backend, OCR pipeline, extraction logic, compliance rules,

data access, and API handling currently lives in `app.py`.



\### Required Improvement



Refactor into modules such as:



\- `routes/`

\- `services/`

\- `ocr/`

\- `compliance/`

\- `models/`

\- `repositories/`

\- `utils/`



\### Goal



Separate responsibilities and make individual components independently testable.



---



\## 3.2 Configuration Management



\*\*Status:\*\* Partial



Runtime configuration should not depend on machine-specific assumptions.



\### Required Improvement



Introduce:



\- environment-based configuration;

\- development/test/production configuration;

\- configurable upload limits;

\- configurable OCR settings;

\- configurable storage paths;

\- secure secret handling.



---



\# 4. OCR and Computer Vision Gaps



\## 4.1 OCR Engine



\*\*Status:\*\* Partial



Tesseract OCR provides the initial extraction mechanism.



\### Problems



Real packaging may contain:



\- curved surfaces;

\- reflective wrappers;

\- low-resolution photographs;

\- rotated text;

\- decorative fonts;

\- multilingual labels;

\- complex backgrounds;

\- multiple text regions.



\### Required Improvement



Build an OCR abstraction layer so alternative OCR engines can be evaluated without

rewriting the application.



Potential approaches include:



\- Tesseract;

\- EasyOCR;

\- PaddleOCR;

\- cloud/document OCR where appropriate.



---



\## 4.2 Image Quality Validation



\*\*Status:\*\* Missing



The system should determine whether an uploaded image is suitable for analysis.



\### Required Checks



\- blur;

\- resolution;

\- orientation;

\- excessive darkness/brightness;

\- glare;

\- unreadable regions.



Poor images should trigger a rescan recommendation rather than an unreliable

compliance result.



---



\## 4.3 Image Preprocessing Pipeline



\*\*Status:\*\* Partial



Basic preprocessing exists.



\### Required Improvement



Create a reusable preprocessing pipeline supporting:



\- resizing;

\- denoising;

\- grayscale conversion;

\- contrast enhancement;

\- adaptive thresholding;

\- rotation correction;

\- perspective correction where useful.



---



\# 5. Information Extraction Gaps



\## 5.1 Regex-Heavy Extraction



\*\*Status:\*\* Partial



The prototype extracts several entities from OCR text using deterministic rules.



\### Required Improvement



Create a structured extraction layer for:



\- manufacturer;

\- packer;

\- importer;

\- address;

\- PIN code;

\- product/common name;

\- net quantity;

\- MRP;

\- manufacturing/packing date;

\- phone number;

\- email;

\- country of origin.



The extractor should preserve both:



1\. normalized value;

2\. original evidence text.



---



\## 5.2 Extraction Confidence



\*\*Status:\*\* Missing



Every extracted field should include confidence/evidence information.



Example:



```json

{

&nbsp; "field": "net\_quantity",

&nbsp; "value": "500 g",

&nbsp; "confidence": 0.93,

&nbsp; "evidence": "Net Qty: 500 g"

}

