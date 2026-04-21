from pathlib import Path

import torch
from PIL import Image
from chandra.model.hf import generate_hf
from chandra.model.schema import BatchInputItem
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

DEBUG_DIR = Path("debug")
MODEL_ID = "datalab-to/chandra-ocr-2"
PROMPT = "이 이미지에 표시된 포켓몬 이름만 답해줘. 이름 텍스트만 출력하고 다른 말은 하지 마."


class OCREngine:
    def __init__(self, ocr_config: dict):
        self.debug = ocr_config.get("debug", False)

        print("[OCR] Chandra 모델 로딩 중... (4-bit 양자화, GPU)")

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        self.model = AutoModelForImageTextToText.from_pretrained(
            MODEL_ID,
            quantization_config=bnb_config,
            device_map="auto",
        )
        self.model.eval()
        self.model.processor = AutoProcessor.from_pretrained(MODEL_ID)
        self.model.processor.tokenizer.padding_side = "left"

    def recognize(self, img: Image.Image, label: str = "img") -> str:
        if self.debug:
            DEBUG_DIR.mkdir(exist_ok=True)
            img.save(DEBUG_DIR / f"{label}_00_raw.png")

        batch = [BatchInputItem(image=img, prompt=PROMPT)]
        with torch.no_grad():
            result = generate_hf(batch, self.model)[0]

        text = result.raw.strip()

        if self.debug:
            print(f"  [{label}] Chandra OCR → '{text}'")

        return text
