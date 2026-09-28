"""
Reusable file-related utilities and security validation.

This module contains technical file helpers that are independent
of Flask routes and application business logic.
"""

import os
import time
import logging
from pathlib import Path
from typing import Union, BinaryIO

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
    "bmp",
    "tiff",
}


def get_file_extension(filename: str) -> str:
    """
    Return the lowercase extension of a filename without the leading dot.
    """
    if not filename:
        return ""

    suffix = Path(filename).suffix
    if not suffix:
        return ""

    return suffix.lstrip(".").lower()


def allowed_file(filename: str, allowed_extensions=None) -> bool:
    """
    Determine whether a filename has an allowed image extension.
    """
    if not filename:
        return False

    extensions = (
        ALLOWED_IMAGE_EXTENSIONS
        if allowed_extensions is None
        else {ext.lower().lstrip(".") for ext in allowed_extensions}
    )

    extension = get_file_extension(filename)
    return bool(extension) and extension in extensions


def validate_image_signature(file_or_path: Union[str, BinaryIO, bytes]) -> bool:
    """
    Validates magic bytes / file signature to verify that the uploaded
    file is a genuine image format and not an executable / script masquerading as an image.
    """
    header = b""
    if isinstance(file_or_path, (str, Path)):
        if not os.path.isfile(file_or_path):
            return False
        with open(file_or_path, "rb") as f:
            header = f.read(16)
    elif hasattr(file_or_path, "read"):
        current_pos = file_or_path.tell() if hasattr(file_or_path, "tell") else 0
        header = file_or_path.read(16)
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(current_pos)
    elif isinstance(file_or_path, bytes):
        header = file_or_path[:16]

    if not header:
        return False

    # Signatures:
    # PNG: \x89PNG\r\n\x1a\n
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    # JPEG: \xff\xd8\xff
    if header.startswith(b"\xff\xd8\xff"):
        return True
    # WEBP: RIFF....WEBP
    if header.startswith(b"RIFF") and b"WEBP" in header[:16]:
        return True
    # BMP: BM
    if header.startswith(b"BM"):
        return True
    # TIFF: II*\x00 or MM\x00*
    if header.startswith(b"II*\x00") or header.startswith(b"MM\x00*"):
        return True

    return False


def cleanup_expired_uploads(folder_path: str, max_age_seconds: int = 86400) -> int:
    """
    Prunes transient uploaded files older than max_age_seconds.
    Returns the count of deleted files.
    """
    if not os.path.isdir(folder_path):
        return 0

    removed_count = 0
    now = time.time()
    try:
        for entry in os.scandir(folder_path):
            if entry.is_file():
                age = now - entry.stat().st_mtime
                if age > max_age_seconds:
                    try:
                        os.remove(entry.path)
                        removed_count += 1
                    except Exception as err:
                        logger.warning(f"Could not remove old upload {entry.path}: {err}")
    except Exception as e:
        logger.error(f"Error during upload folder cleanup: {e}")

    return removed_count