# System Architecture & Design Specification

## Overview
The **Legal Metrology Compliance Checker & Food Counterfeit Risk Intelligence System** is an enterprise-grade regulatory surveillance platform designed to evaluate packaged food commodities against India's **Legal Metrology (Packaged Commodities) Rules, 2011 (PCR, 2011)** while simultaneously assessing **Food Counterfeit Risk** through multi-signal computer vision and text verification.

---

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    Client["Client Browser / Mobile / Surveillance Auditor"] -->|HTTP / REST| AppFactory["Flask Application Factory (create_app)"]
    
    subgraph Security & Middleware
        AppFactory --> SecHeaders["Security Headers (nosniff, SAMEORIGIN, CSP)"]
        AppFactory --> RateLimiter["Sliding-Window Rate Limiter (30 req/min)"]
        AppFactory --> ErrorHandlers["Central Error Handlers (400, 404, 413, 500)"]
    end

    subgraph Route Layer (Blueprints)
        AppFactory --> WebBP["Web Routes (/)"]
        AppFactory --> ScanBP["Scan Routes (/api/scan, /api/scans, /api/save)"]
        AppFactory --> ProdBP["Product Routes (/api/products)"]
        AppFactory --> StatsBP["Analytics Routes (/api/stats)"]
        AppFactory --> RulesBP["Rules Routes (/api/rules)"]
    end

    subgraph Service & Intelligence Layer
        ScanBP --> Orchestrator["Analysis Orchestrator"]
        Orchestrator --> ImgQuality["Image Quality Service (Blur, Lighting, Glare)"]
        Orchestrator --> OCREngine["OCR Service (Tesseract & Word Confidence)"]
        Orchestrator --> Extractor["Entity Extraction Service"]
        Orchestrator --> Normalizer["Declaration Normalization Service"]
        
        subgraph Stream 1: Legal Metrology
            Orchestrator --> CompEngine["Compliance Rule Engine (RuleRegistry)"]
            CompEngine --> R6a["Rule 6(1)(a) - Manufacturer"]
            CompEngine --> R6b["Rule 6(1)(b) - Product Name"]
            CompEngine --> R6c["Rule 6(1)(c) - Net Quantity"]
            CompEngine --> R6d["Rule 6(1)(d) - Mfg Date"]
            CompEngine --> R6da["Rule 6(1)(da) - MRP & Taxes"]
            CompEngine --> R6e["Rule 6(1)(e) - Consumer Care"]
            CompEngine --> R6n["Rule 6(1)(n) - Country of Origin"]
        end

        subgraph Stream 2: Counterfeit Risk Intelligence
            Orchestrator --> CFEngine["Food Counterfeit Risk Engine"]
            CFEngine --> ProdID["Product Identification Service"]
            CFEngine --> TypoCheck["Brand Squatting / Typo Detector"]
            CFEngine --> MfrCheck["Authorized Producer Verifier"]
            CFEngine --> BarcodeCheck["GS1 GTIN-13 Barcode Verifier"]
            CFEngine --> LayoutCheck["Packaging Layout PDP Analyzer"]
        end
    end

    subgraph Persistence Layer
        ScanBP --> ProdRepo["Product Repository"]
        ProdRepo --> DBRepo["Database Repository (SQLite)"]
        DBRepo --> SQLiteDB[("food_compliance.db (products & scans)")]
        DBRepo -.-> CSVDataset[("legal_metrology_dataset.csv (Dual Sync)")]
        CFEngine --> RefRepo["Reference Product Repository"]
        RefRepo --> RefDB[("reference_products.json")]
    end
```

---

## 2. Layered Architecture Principles

The codebase adheres strictly to a clean, decoupled layered architecture:

1. **Presentation / Route Layer (`routes/`)**:
   - Thin Flask Blueprints (`web_routes.py`, `scan_routes.py`, `product_routes.py`, `analytics_routes.py`, `rules_routes.py`).
   - Handles HTTP request parsing, MIME/magic byte validation, and JSON response serialization.

2. **Core Domain Models (`models/`)**:
   - Strongly-typed domain structures (`ComplianceStatus`, `CounterfeitRisk`, `RuleEvaluation`, `NormalizedNetQuantity`, `NormalizedMRP`, `NormalizedDate`, `ScannedProductRecord`).

3. **Orchestration & Business Intelligence (`services/`)**:
   - `AnalysisOrchestrator`: Sequences image quality pre-check, OCR, extraction, normalization, legal evaluation, and counterfeit risk analysis.
   - `ImageQualityService`: Assesses Laplacian blur variance, luminance, and specular glare ratio.
   - `OCRService`: Pluggable abstraction (`BaseOCREngine`, `TesseractOCREngine`) deriving genuine word-level OCR confidence.
   - `RuleRegistry`: Modular rule execution dynamically evaluating statutory provisions.
   - `FoodCounterfeitRiskEngine`: Combines multi-signal risk vectors into calibrated risk scores and tiers.

4. **Persistence & Data Access Layer (`repositories/`)**:
   - `DatabaseRepository`: Embedded SQLite engine (`food_compliance.db`) providing relational ACID storage for scanned products and audit trails.
   - Synchronized with `legal_metrology_dataset.csv` for 100% backward compatibility.
   - `ReferenceProductRepository`: Verified knowledge base for genuine brand specifications, variants, barcodes, and authorized producer units.

5. **Security & Utilities Layer (`utils/`)**:
   - Magic byte validation (`validate_image_signature`).
   - In-memory sliding window rate limiting (`scan_rate_limiter`).
   - Image pre-processing filters (`image_preprocessing.py`).
