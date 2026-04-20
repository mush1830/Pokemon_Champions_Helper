import numpy as np
import cv2
import easyocr
from PIL import Image


class OCREngine:
    def __init__(self, ocr_config: dict):
        languages = ocr_config.get("language", ["ko"])
        self.reader = easyocr.Reader(languages, gpu=False)
        self.preprocessing = ocr_config.get("preprocessing", True)

    def _preprocess(self, img: Image.Image) -> np.ndarray:
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # Upscale 2x for better OCR accuracy on small text
        scaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Adaptive threshold to handle varying backgrounds
        thresh = cv2.adaptiveThreshold(
            scaled, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, h=10)
        return denoised

    def recognize(self, img: Image.Image) -> str:
        if self.preprocessing:
            processed = self._preprocess(img)
        else:
            processed = np.array(img)

        results = self.reader.readtext(processed, detail=0, paragraph=True)
        return " ".join(results).strip()
