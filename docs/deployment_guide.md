# Deployment & Production Operations Guide

This guide covers production deployment options for the Legal Metrology & Counterfeit Intelligence platform.

---

## 1. Quick Start with Docker (Recommended)

### Prerequisites
- Docker Engine 24+ & Docker Compose

### Single Command Launch
```bash
docker compose up --build -d
```

Verify service status:
```bash
docker compose ps
curl http://localhost:5000/health
```

The service will be live on `http://localhost:5000` with Tesseract OCR engine, Gunicorn WSGI workers, and persistent SQLite storage.

---

## 2. Linux Production Deployment (Gunicorn)

### System Setup (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng python3-venv python3-pip
```

### Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running with Gunicorn
```bash
export SECRET_KEY="your-production-secret-key"
export LOG_LEVEL="INFO"
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 60 wsgi:app
```

---

## 3. Windows Production Deployment (Waitress)

### Prerequisites
- Python 3.10+
- Tesseract OCR for Windows installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Launch via Waitress
```powershell
.\.venv\Scripts\activate
waitress-serve --port=5000 wsgi:app
```

---

## 4. Environment Variables Configuration

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `development-only-...` | Cryptographic secret for sessions and CSRF protection. |
| `FLASK_DEBUG` | `0` | Set `0` in production to disable debug console. |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `MAX_CONTENT_LENGTH_MB` | `16` | Maximum file upload size in megabytes. |
| `DATABASE_PATH` | `data/food_compliance.db` | Persistent SQLite database file location. |
| `TESSERACT_CMD` | Auto-detected | Path to the Tesseract OCR executable. |

---

## 5. Reverse Proxy Configuration (Nginx)

```nginx
server {
    listen 80;
    server_name compliance.gov.in;
    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
