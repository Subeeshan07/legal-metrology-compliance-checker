"""
OCR service for packaged-product label images.

This module owns Tesseract availability detection and OCR execution.
Image preprocessing itself remains in utils.image_utils so that image
operations are reusable independently of the OCR engine.
"""

import logging

from config.settings import Config
from utils.image_utils import preprocess_image_for_ocr


logger = logging.getLogger(__name__)


try:
    import pytesseract
except ImportError:
    pytesseract = None


class OCRService:
    """
    Service responsible for Tesseract OCR operations.

    Responsibilities:
    - Configure the Tesseract executable.
    - Verify Tesseract availability.
    - Preprocess images for OCR.
    - Execute OCR.
    - Return OCR text and metadata.

    This service deliberately does not perform:
    - entity extraction
    - compliance checking
    - HTTP request handling
    """

    def __init__(self, tesseract_cmd=None):
        self.tesseract_cmd = (
            tesseract_cmd
            if tesseract_cmd is not None
            else Config.TESSERACT_CMD
        )

        self.available = False

        self._configure_tesseract()

    def _configure_tesseract(self):
        """Configure pytesseract with the resolved executable path."""
        if pytesseract is None:
            return

        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def check_availability(self):
        """
        Check whether the Tesseract executable can be invoked.

        Returns:
            bool: True when Tesseract is available, otherwise False.
        """
        if pytesseract is None:
            self.available = False

            logger.warning(
                "pytesseract package is not installed. "
                "OCR is unavailable."
            )

            return False

        self._configure_tesseract()

        try:
            pytesseract.get_tesseract_version()

            self.available = True

            logger.info(
                "Tesseract OCR verified and active at: %s",
                pytesseract.pytesseract.tesseract_cmd,
            )

            return True

        except Exception as exc:
            self.available = False

            logger.warning(
                "Tesseract OCR is unavailable: %s",
                exc,
            )

            return False

    def extract_text(self, image_path):
        """
        Extract text from a product-label image.

        Returns:
            dict:
                {
                    "success": bool,
                    "text": str,
                    "source": str,
                    "error": str | None
                }
        """
        if not self.available and not self.check_availability():
            return {
                "success": False,
                "text": "",
                "source": "OCR unavailable",
                "error": "Tesseract OCR is not available.",
            }

        try:
            processed_image = preprocess_image_for_ocr(image_path)

            text = pytesseract.image_to_string(
                processed_image,
                config="--psm 6",
            )

            return {
                "success": True,
                "text": text.strip(),
                "source": (
                    "Local Tesseract OCR "
                    f"({pytesseract.pytesseract.tesseract_cmd})"
                ),
                "error": None,
            }

        except Exception as exc:
            logger.exception(
                "OCR failed for image: %s",
                image_path,
            )

            return {
                "success": False,
                "text": "",
                "source": "OCR failed",
                "error": str(exc),
            }


ocr_service = OCRService()


def check_tesseract_available():
    """
    Backward-compatible wrapper around OCRService availability checking.

    Existing modules and tests may continue importing this function while
    the application is incrementally refactored.
    """
    return ocr_service.check_availability()


def perform_ocr_on_image(image_path):
    """
    Backward-compatible OCR wrapper.

    Returns:
        tuple[str, str]:
            OCR text and OCR source description.
    """
    result = ocr_service.extract_text(image_path)

    return result["text"], result["source"]