"""
Advanced OCR Image Preprocessing Pipeline.

Provides image optimization stages for maximizing text readability:
- Dynamic resizing with aspect ratio preservation
- Grayscale conversion
- Contrast enhancement (Adaptive histogram & Autocontrast)
- Denoising & smoothing filter
- Otsu / Adaptive thresholding
"""

import numpy as np
from PIL import Image, ImageOps, ImageFilter


def convert_to_grayscale(image: Image.Image) -> Image.Image:
    """Converts any PIL image (RGB, RGBA, P) to Grayscale ('L')."""
    return ImageOps.grayscale(image.convert("RGB"))


def resize_for_ocr(image: Image.Image, target_min_width: int = 1200) -> Image.Image:
    """
    Scales up low-resolution images to improve OCR word accuracy,
    maintaining aspect ratio.
    """
    width, height = image.size
    if width < target_min_width:
        ratio = target_min_width / float(width)
        new_height = int(height * ratio)
        return image.resize((target_min_width, new_height), Image.Resampling.LANCZOS)
    return image


def enhance_contrast(image: Image.Image, cutoff: int = 2) -> Image.Image:
    """Enhances image dynamic range using automatic contrast normalization."""
    return ImageOps.autocontrast(image, cutoff=cutoff)


def apply_denoising(image: Image.Image) -> Image.Image:
    """Removes salt-and-pepper scan noise using a subtle median filter."""
    return image.filter(ImageFilter.MedianFilter(size=3))


def apply_otsu_threshold(image: Image.Image) -> Image.Image:
    """
    Calculates Otsu optimal threshold on grayscale image array
    and returns a clean, binarized black-and-white PIL image.
    """
    gray = convert_to_grayscale(image)
    np_img = np.array(gray, dtype=np.uint8)

    # Compute histogram
    hist, _ = np.histogram(np_img, bins=256, range=(0, 256))
    total = np_img.size

    current_max = 0.0
    threshold = 128
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0

    for i in range(256):
        w_b += hist[i]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break

        sum_b += i * hist[i]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f

        between_class_var = float(w_b) * float(w_f) * ((m_b - m_f) ** 2)
        if between_class_var > current_max:
            current_max = between_class_var
            threshold = i

    binarized = (np_img > threshold).astype(np.uint8) * 255
    return Image.fromarray(binarized, mode="L")


def preprocess_image_pipeline(
    image: Image.Image,
    target_min_width: int = 1200,
    binarize: bool = False,
) -> Image.Image:
    """
    Executes the full preprocessing pipeline:
    Rescaling -> Grayscale -> Autocontrast -> (Optional Otsu Thresholding).
    """
    processed = resize_for_ocr(image, target_min_width=target_min_width)
    processed = convert_to_grayscale(processed)
    processed = enhance_contrast(processed)
    if binarize:
        processed = apply_otsu_threshold(processed)
    return processed
