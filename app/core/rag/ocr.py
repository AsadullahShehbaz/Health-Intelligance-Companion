# app/core/rag/ocr.py
import base64
import io
import cv2
import numpy as np
from PIL import Image, ImageOps
import pytesseract

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def preprocess_image(pil_image: Image.Image) -> np.ndarray:
    """
    Preprocess image for optimal Tesseract OCR performance on lab reports and medical records:
    1. Fix orientation EXIF tag.
    2. Upscale low-DPI images.
    3. Grayscale conversion.
    4. Contrast enhancement using CLAHE.
    5. Adaptive thresholding and noise filtering.
    """
    # 1. Correct EXIF orientation (e.g. phone photos taken sideways)
    try:
        pil_image = ImageOps.exif_transpose(pil_image)
    except Exception:
        pass

    # Convert to RGB if palette/RGBA
    if pil_image.mode not in ("RGB", "L"):
        pil_image = pil_image.convert("RGB")

    # 2. Check resolution & upscale low DPI/small images
    width, height = pil_image.size
    min_dim = min(width, height)
    if min_dim < 1000:
        scale_factor = 2.0 if min_dim > 500 else 3.0
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info("Upscaled low-res image from (%d, %d) to (%d, %d)", width, height, new_width, new_height)

    # Convert PIL Image to OpenCV format (BGR / Grayscale)
    img_np = np.array(pil_image)
    if len(img_np.shape) == 3 and img_np.shape[2] == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    elif len(img_np.shape) == 3 and img_np.shape[2] == 4:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)
    else:
        gray = img_np

    # 3. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 4. Bilateral filter to smooth noise while preserving text edges
    filtered = cv2.bilateralFilter(enhanced, d=9, sigmaColor=75, sigmaSpace=75)

    # 5. Otsu Binarization / Thresholding
    _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh


def run_tesseract_with_fallbacks(cv_image: np.ndarray, raw_pil_image: Image.Image) -> str:
    """
    Attempts OCR with multiple PSM configurations to handle various medical report layouts.
    """
    # PSM 3: Fully automatic page segmentation (default)
    # PSM 6: Assume a single uniform block of text (great for tabular lab results)
    # PSM 11: Sparse text (find as much text as possible in scattered locations)
    psm_configs = ["--psm 3", "--psm 6", "--psm 11"]

    # First attempt on preprocessed binary image
    for config in psm_configs:
        text = pytesseract.image_to_string(cv_image, config=config).strip()
        if len(text) > 10:
            logger.info("OCR successful on preprocessed image with config='%s' | chars=%d", config, len(text))
            return text

    # Fallback attempt on raw PIL image if thresholding removed faint text/color fonts
    logger.info("Preprocessed OCR yielded low characters. Running fallback on raw image...")
    for config in psm_configs:
        text = pytesseract.image_to_string(raw_pil_image, config=config).strip()
        if len(text) > 10:
            logger.info("OCR successful on raw image fallback with config='%s' | chars=%d", config, len(text))
            return text

    return ""


def extract_text_from_base64(image_b64: str) -> str:
    if not image_b64:
        logger.info("OCR skipped — empty image_base64")
        return ""

    logger.info("▶ OCR extraction started | b64_len=%d", len(image_b64))

    try:
        # Sanitize Base64 string if data URL prefix exists (e.g. "data:image/png;base64,...")
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]

        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))
        logger.info("Image loaded | size=%s | mode=%s", image.size, image.mode)

        # Preprocess the image with OpenCV
        processed_img = preprocess_image(image)

        # Extract text using fallback execution pipeline
        result = run_tesseract_with_fallbacks(processed_img, image)

        logger.info("✓ OCR extraction completed | chars=%d", len(result))
        return result

    except Exception:
        logger.exception("OCR extraction failed")
        return ""