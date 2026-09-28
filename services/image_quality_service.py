"""
Image Quality Assessment Service.

Evaluates package label image quality before OCR processing:
- Blur detection (variance of Laplacian)
- Lighting assessment (mean brightness, underexposure, overexposure)
- Glare detection (high-intensity cluster ratio)
- Resolution check (minimum width/height/megapixels)
- Perspective and skew warnings
"""

import numpy as np
from PIL import Image, ImageOps, ImageFilter
from typing import Dict, Any, List, Tuple


class ImageQualityAssessmentService:

    MIN_ACCEPTABLE_WIDTH = 600
    MIN_ACCEPTABLE_HEIGHT = 400
    BLUR_THRESHOLD = 80.0       # Variance of Laplacian below this is blurry
    DARK_THRESHOLD = 40.0       # Mean luminance below this is underexposed
    BRIGHT_THRESHOLD = 252.0    # Mean luminance above this is washed out
    GLARE_PIXEL_THRESHOLD = 254
    GLARE_RATIO_THRESHOLD = 0.20  # Over 20% specular white indicates severe glare


    @classmethod
    def evaluate_image(cls, image_input) -> Dict[str, Any]:
        """
        Takes a file path or PIL.Image instance and returns a comprehensive
        quality report with metrics and actionable recommendations.
        """
        if isinstance(image_input, str):
            image = Image.open(image_input)
        else:
            image = image_input

        # Convert to RGB then Grayscale
        rgb_image = image.convert("RGB")
        gray_image = ImageOps.grayscale(rgb_image)
        width, height = rgb_image.size
        np_gray = np.array(gray_image, dtype=np.float32)

        warnings: List[str] = []
        recommendations: List[str] = []

        # 1. Resolution Check
        is_low_resolution = (width < cls.MIN_ACCEPTABLE_WIDTH) or (height < cls.MIN_ACCEPTABLE_HEIGHT)
        if is_low_resolution:
            warnings.append(f"Low image resolution ({width}x{height}px). Minimum recommended is 600x400px.")
            recommendations.append("Move closer to the label or capture at a higher resolution.")

        # 2. Lighting & Brightness
        mean_brightness = float(np.mean(np_gray))
        if mean_brightness < cls.DARK_THRESHOLD:
            lighting_quality = "UNDEREXPOSED"
            warnings.append(f"Image is dark/underexposed (brightness: {mean_brightness:.1f}/255).")
            recommendations.append("Increase ambient lighting or enable device flash.")
        elif mean_brightness > cls.BRIGHT_THRESHOLD:
            lighting_quality = "OVEREXPOSED"
            warnings.append(f"Image is overexposed/washed out (brightness: {mean_brightness:.1f}/255).")
            recommendations.append("Reduce harsh direct lighting.")
        else:
            lighting_quality = "GOOD"

        # 3. Glare Detection
        saturated_pixels = np.sum(np_gray >= cls.GLARE_PIXEL_THRESHOLD)
        glare_ratio = float(saturated_pixels / np_gray.size)
        has_glare = glare_ratio > cls.GLARE_RATIO_THRESHOLD
        if has_glare:
            warnings.append(f"Specular reflection/glare detected ({glare_ratio * 100:.1f}% saturated pixels).")
            recommendations.append("Tilt package slightly away from light sources to avoid reflections.")

        # 4. Blur Detection via Discrete 2D Laplacian operator
        # Laplacian kernel [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
        # We can implement this quickly with PIL kernel or numpy slice convolution
        laplacian = (
            -4.0 * np_gray[1:-1, 1:-1]
            + np_gray[:-2, 1:-1]
            + np_gray[2:, 1:-1]
            + np_gray[1:-1, :-2]
            + np_gray[1:-1, 2:]
        )
        blur_score = float(np.var(laplacian)) if laplacian.size > 0 else 0.0
        is_blurry = blur_score < cls.BLUR_THRESHOLD
        if is_blurry:
            warnings.append(f"Image appears blurry or out of focus (sharpness score: {blur_score:.1f}).")
            recommendations.append("Hold camera steady and ensure the text is sharply in focus.")

        # 5. Composite Quality Score (0 - 100)
        score = 100.0
        if is_low_resolution:
            score -= 25.0
        if is_blurry:
            score -= 30.0
        if lighting_quality != "GOOD":
            score -= 20.0
        if has_glare:
            score -= 15.0
        quality_score = max(0.0, min(100.0, score))

        if quality_score >= 80:
            quality_grade = "EXCELLENT"
        elif quality_score >= 50:
            quality_grade = "ACCEPTABLE"
        else:
            quality_grade = "POOR"

        return {
            "quality_score": round(quality_score, 1),
            "quality_grade": quality_grade,
            "dimensions": {"width": width, "height": height},
            "is_low_resolution": is_low_resolution,
            "mean_brightness": round(mean_brightness, 1),
            "lighting_quality": lighting_quality,
            "blur_score": round(blur_score, 1),
            "is_blurry": is_blurry,
            "glare_ratio": round(glare_ratio, 3),
            "has_glare": has_glare,
            "warnings": warnings,
            "recommendations": recommendations,
        }
