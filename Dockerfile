# Multi-stage production container for Legal Metrology & Counterfeit Intelligence
FROM python:3.11-slim AS base

# Install system dependencies & Tesseract OCR engine
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TESSERACT_CMD=/usr/bin/tesseract \
    PORT=5000 \
    FLASK_ENV=production

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure storage directories exist
RUN mkdir -p uploads data static/samples

# Create non-root system user for security
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

# Production WSGI server
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "--access-logfile=-", "--error-logfile=-", "wsgi:app"]
