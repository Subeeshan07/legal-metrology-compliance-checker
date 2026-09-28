"""
Web interface routes for frontend views and static uploads/samples.
"""

from flask import Blueprint, render_template, send_from_directory
from config.settings import Config
from services.ocr_service import check_tesseract_available

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    tesseract_status = check_tesseract_available()
    return render_template("index.html", tesseract_available=tesseract_status)


@web_bp.route("/static/samples/<path:filename>")
def serve_samples(filename):
    return send_from_directory(Config.SAMPLES_FOLDER, filename)


@web_bp.route("/uploads/<path:filename>")
def serve_uploads(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
