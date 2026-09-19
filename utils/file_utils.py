"""
Reusable file-related utilities.

This module contains technical file helpers that are independent
of Flask routes and application business logic.
"""

from pathlib import Path


ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
    "bmp",
    "tiff",
}


def get_file_extension(filename):
    """
    Return the lowercase extension of a filename without the leading dot.

    Examples:
        product.JPG -> jpg
        label.png   -> png
        noextension -> ""
    """
    if not filename:
        return ""

    suffix = Path(filename).suffix

    if not suffix:
        return ""

    return suffix.lstrip(".").lower()


def allowed_file(filename, allowed_extensions=None):
    """
    Determine whether a filename has an allowed image extension.

    A custom extension collection may be supplied for reuse in other
    upload contexts.
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