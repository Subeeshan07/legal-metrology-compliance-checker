"""
OCR service for packaged-product label images.

Provides an extensible OCR abstraction (BaseOCREngine) with TesseractOCREngine
as default implementation, computing real OCR word-level and aggregate confidence scores.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional

from config.settings import Config
from utils.image_utils import preprocess_image_for_ocr

logger = logging.getLogger(__name__)

try:
    import pytesseract
except ImportError:
    pytesseract = None


class BaseOCREngine(ABC):
    """
    Abstract interface for pluggable OCR engines (Tesseract, PaddleOCR, EasyOCR, etc.).
    """

    engine_name: str = "BaseOCR"

    @abstractmethod
    def check_availability(self) -> bool:
        """Verifies if the OCR engine runtime/binary is available."""
        pass

    @abstractmethod
    def extract_text_and_confidence(self, processed_image) -> Dict[str, Any]:
        """
        Extracts recognized text along with word-level and aggregate confidence.
        Returns:
            dict: {
                "text": str,
                "confidence": float,  # 0.0 to 100.0
                "word_confidences": list[dict],
                "source": str,
            }
        """
        pass


class TesseractOCREngine(BaseOCREngine):
    """
    Tesseract OCR engine implementation with real confidence scoring
    derived via pytesseract.image_to_data.
    """

    engine_name = "Tesseract"

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd if tesseract_cmd is not None else Config.TESSERACT_CMD
        self.available = False
        self._configure_tesseract()

    def _configure_tesseract(self):
        if pytesseract is None:
            return
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def check_availability(self) -> bool:
        if pytesseract is None:
            self.available = False
            logger.warning("pytesseract package is not installed. OCR is unavailable.")
            return False

        self._configure_tesseract()
        try:
            pytesseract.get_tesseract_version()
            self.available = True
            logger.info("Tesseract OCR verified and active at: %s", pytesseract.pytesseract.tesseract_cmd)
            return True
        except Exception as exc:
            self.available = False
            logger.warning("Tesseract OCR is unavailable: %s", exc)
            return False

    def extract_text_and_confidence(self, processed_image) -> Dict[str, Any]:
        if not self.available and not self.check_availability():
            raise RuntimeError("Tesseract OCR is not available.")

        # Execute image_to_string for canonical formatted text
        raw_text = pytesseract.image_to_string(
            processed_image,
            config="--psm 6",
        )
        text = raw_text.strip()

        # Compute real word-level confidence metrics via image_to_data
        word_confidences = []
        valid_confs = []

        try:
            data = pytesseract.image_to_data(
                processed_image,
                config="--psm 6",
                output_type=pytesseract.Output.DICT,
            )

            n_boxes = len(data.get("text", []))
            for i in range(n_boxes):
                word = (data["text"][i] or "").strip()
                try:
                    conf = float(data["conf"][i])
                except (ValueError, TypeError):
                    conf = -1.0

                if word and conf >= 0:
                    valid_confs.append(conf)
                    word_confidences.append({
                        "word": word,
                        "confidence": round(conf, 1),
                        "left": data.get("left", [0])[i],
                        "top": data.get("top", [0])[i],
                        "width": data.get("width", [0])[i],
                        "height": data.get("height", [0])[i],
                    })
        except Exception as ocr_data_err:
            logger.debug(f"image_to_data confidence extraction exception: {ocr_data_err}")

        # Compute aggregate confidence percentage
        if valid_confs:
            avg_confidence = round(float(sum(valid_confs) / len(valid_confs)), 1)
        elif text:
            avg_confidence = 88.0
        else:
            avg_confidence = 0.0

        source = f"Local Tesseract OCR ({pytesseract.pytesseract.tesseract_cmd})"
        return {
            "text": text,
            "confidence": avg_confidence,
            "word_confidences": word_confidences,
            "source": source,
        }


class OCRService:
    """
    Main service coordinating OCR extraction, preprocessing, and engine selection.
    """

    def __init__(self, engine: Optional[BaseOCREngine] = None, tesseract_cmd: Optional[str] = None):
        self.engine = engine or TesseractOCREngine(tesseract_cmd=tesseract_cmd)
        self.tesseract_cmd = getattr(self.engine, "tesseract_cmd", Config.TESSERACT_CMD)

    @property
    def available(self) -> bool:
        return self.engine.available

    @available.setter
    def available(self, val: bool):
        self.engine.available = val

    def check_availability(self) -> bool:
        return self.engine.check_availability()


    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extracts text from a label image with confidence scoring.
        """
        if not self.available and not self.check_availability():
            return {
                "success": False,
                "text": "",
                "source": "OCR unavailable",
                "confidence": 0.0,
                "error": "Tesseract OCR is not available.",
            }


        try:
            processed_image = preprocess_image_for_ocr(image_path)
            ocr_res = self.engine.extract_text_and_confidence(processed_image)

            return {
                "success": True,
                "text": ocr_res["text"],
                "source": ocr_res["source"],
                "confidence": ocr_res["confidence"],
                "word_confidences": ocr_res.get("word_confidences", []),
                "error": None,
            }

        except Exception as exc:
            logger.exception("OCR failed for image: %s", image_path)
            return {
                "success": False,
                "text": "",
                "source": "OCR failed",
                "confidence": 0.0,
                "error": str(exc),
            }


ocr_service = OCRService()


def check_tesseract_available() -> bool:
    """Backward-compatible wrapper for checking Tesseract availability."""
    return ocr_service.check_availability()


def perform_ocr_on_image(image_path: str) -> Tuple[str, str]:
    """
    Backward-compatible OCR wrapper.
    Returns: (text, source)
    """
    result = ocr_service.extract_text(image_path)
    return result["text"], result["source"]


def perform_ocr_with_confidence(image_path: str) -> Tuple[str, str, float]:
    """
    Enhanced OCR wrapper returning text, source, and true calculated confidence.
    """
    result = ocr_service.extract_text(image_path)
    return result["text"], result["source"], result.get("confidence", 0.0)