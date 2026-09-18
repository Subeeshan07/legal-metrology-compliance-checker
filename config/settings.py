"""
Central application configuration.

Environment variables may override development defaults so that
machine-specific settings do not need to be hard-coded in application code.
"""

import os
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _get_int_env(name, default):
    """Return an integer environment variable or its default value."""
    value = os.getenv(name)

    if value is None or value.strip() == "":
        return default

    try:
        return int(value)
    except ValueError:
        return default


def resolve_path(value, default_relative_path):
    """
    Resolve a configured filesystem path.

    Relative paths are interpreted relative to the project root.
    Absolute paths are preserved.
    """
    configured = value or default_relative_path
    path = Path(configured).expanduser()

    if not path.is_absolute():
        path = BASE_DIR / path

    return str(path.resolve())


def detect_tesseract_command():
    """
    Determine which Tesseract executable should be used.

    Priority:
    1. TESSERACT_CMD environment variable
    2. Executable available through PATH
    3. Common Windows installation locations
    4. Common Unix installation locations
    """
    configured = os.getenv("TESSERACT_CMD", "").strip()

    if configured:
        return str(Path(configured).expanduser())

    path_command = shutil.which("tesseract")
    if path_command:
        return path_command

    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(
            r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        ),
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    return None


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-only-secret-key",
    )

    UPLOAD_FOLDER = resolve_path(
        os.getenv("UPLOAD_FOLDER"),
        "uploads",
    )

    SAMPLES_FOLDER = resolve_path(
        os.getenv("SAMPLES_FOLDER"),
        os.path.join("static", "samples"),
    )

    DATASET_PATH = resolve_path(
        os.getenv("DATASET_PATH"),
        "legal_metrology_dataset.csv",
    )

    MAX_CONTENT_LENGTH_MB = _get_int_env(
        "MAX_CONTENT_LENGTH_MB",
        16,
    )

    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH_MB * 1024 * 1024

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    TESSERACT_CMD = detect_tesseract_command()

    DEBUG = os.getenv(
        "FLASK_DEBUG",
        "0",
    ).lower() in {"1", "true", "yes", "on"}
