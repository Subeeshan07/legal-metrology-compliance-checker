"""
Reusable image-processing utilities.

The functions in this module contain image-specific technical logic
and do not depend on Flask or application routes.
"""

from PIL import Image, ImageEnhance


DEFAULT_MIN_OCR_WIDTH = 1000
DEFAULT_CONTRAST_FACTOR = 1.8
DEFAULT_SHARPNESS_FACTOR = 1.5


def preprocess_image_for_ocr(
    image_path,
    min_width=DEFAULT_MIN_OCR_WIDTH,
    contrast_factor=DEFAULT_CONTRAST_FACTOR,
    sharpness_factor=DEFAULT_SHARPNESS_FACTOR,
):
    """
    Preprocess an image to improve OCR readability.

    Processing pipeline:

    1. Open image.
    2. Convert RGBA/palette images to RGB.
    3. Upscale images narrower than the minimum OCR width.
    4. Convert image to grayscale.
    5. Enhance contrast.
    6. Enhance sharpness.

    Returns:
        PIL.Image.Image:
            The processed grayscale image.
    """
    image = Image.open(image_path)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    width, height = image.size

    if width < min_width:
        scale_factor = min_width / width

        image = image.resize(
            (
                int(width * scale_factor),
                int(height * scale_factor),
            ),
            Image.Resampling.LANCZOS,
        )

    grayscale = image.convert("L")

    contrast_enhancer = ImageEnhance.Contrast(grayscale)
    enhanced = contrast_enhancer.enhance(contrast_factor)

    sharpness_enhancer = ImageEnhance.Sharpness(enhanced)
    processed = sharpness_enhancer.enhance(sharpness_factor)

    return processed