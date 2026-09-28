# REST API Reference

The Legal Metrology & Counterfeit Intelligence platform exposes clean, standardized REST endpoints for automated surveillance, batch scanning, and dashboard reporting.

---

## 1. Unified Scan & Evaluation

### `POST /api/scan`
Executes the full automated analysis pipeline across image quality, OCR, declaration normalization, legal compliance verification, and counterfeit risk detection.

**Headers:**
- `Content-Type: multipart/form-data` or `application/x-www-form-urlencoded`

**Request Body Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `label_image` | File | Optional* | High-resolution image of the packaged commodity (PNG, JPG, WEBP). |
| `sample_id` | String | Optional* | Preset sample test ID (`compliant`, `non_compliant`, `needs_review`). |
| `manual_text` | String | Optional* | Direct raw label declarations text. |
| `barcode` | String | Optional | 13-digit GS1 GTIN / EAN barcode extracted or scanned. |

*\*At least one of `label_image`, `sample_id`, or `manual_text` must be supplied.*

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "scan_id": "SCAN-A1B2C3D4",
  "image_url": "/uploads/scan_12345.png",
  "ocr_text": "HIMALAYAN CHAKKI FRESH ATTA\nNet Quantity: 5 kg...",
  "ocr_confidence": "94.2%",
  "extracted_entities": {
    "product_name": "HIMALAYAN CHAKKI FRESH ATTA",
    "net_quantity": "5 kg",
    "mrp": "Rs. 245.00 (Incl. of all taxes)",
    "mfg_date": "05/2026",
    "manufacturer": "Pristine Foods & Agro Ltd, Bengaluru - 560058",
    "consumer_care": "care@pristine.com | 1800-220-4400",
    "country_of_origin": "India"
  },
  "compliance": {
    "overall_status": "COMPLIANT",
    "violations": [],
    "violations_summary": "None (Fully Compliant with Rule 6)",
    "checks": [ ... ]
  },
  "counterfeit_risk": {
    "risk_tier": "LOW",
    "risk_score": 10.0,
    "identified_product": {
      "matched": true,
      "brand": "Himalayan",
      "product_name": "Himalayan Chakki Fresh Atta"
    },
    "risk_factors": [],
    "positive_signals": [ ... ],
    "recommendation": "LOW RISK: Packaging specifications align with genuine reference data."
  },
  "image_quality": {
    "quality_grade": "EXCELLENT",
    "resolution": [1080, 1080],
    "blur_laplacian": 340.5,
    "is_blurry": false,
    "luminance_mean": 178.2,
    "is_poor_lighting": false,
    "glare_percentage": 0.4,
    "has_glare": false
  },
  "unified_report": { ... }
}
```

---

## 2. Scan History & Auditing

### `GET /api/scans`
Retrieves paginated scan audits stored in the SQLite persistence database.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | Integer | `50` | Maximum records to return. |
| `offset` | Integer | `0` | Offset for pagination. |
| `search` | String | None | Filter by scan_id, product_id, or status. |

---

## 3. Product Catalog & Registry

### `GET /api/products`
Retrieves filtered and paginated surveillance records from the product repository.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | Integer | `100` | Number of records to return. |
| `offset` | Integer | `0` | Offset for pagination. |
| `search` | String | None | Search query across name, manufacturer, ID, or violations. |
| `status` | String | `ALL` | Filter: `COMPLIANT`, `NON-COMPLIANT`, `NEEDS REVIEW`. |
| `category` | String | `ALL` | Filter by commodity category. |

---

## 4. Analytics & Dashboard Metrics

### `GET /api/stats`
Returns aggregated compliance metrics, status distribution, and top statutory violations for dashboard charts.

---

## 5. Statutory Rules

### `GET /api/rules`
Exposes the structured inventory of Legal Metrology (Packaged Commodities) Rules, 2011 evaluated by the engine.

---

## 6. System Health & Readiness

### `GET /health`
Returns operational health status, database connection state, and OCR engine availability.

**Response (`200 OK`):**
```json
{
  "status": "UP",
  "service": "Legal Metrology Compliance & Counterfeit Risk Checker",
  "ocr_engine": "ACTIVE",
  "database": "SQLITE_READY",
  "timestamp": "2026-09-28 14:30:00"
}
```
