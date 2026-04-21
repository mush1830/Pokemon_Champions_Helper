"""
ROI 선택 도구 - 마우스 드래그로 포켓몬 이름 영역을 지정하고
config.json에 저장합니다.

사용법:
    python scripts/roi_selector.py

조작:
    - 마우스 드래그: 영역 선택
    - Enter: 선택 확정
    - R: 다시 선택
    - ESC: 취소
"""

import json
import time
from pathlib import Path

import cv2
import mss
import numpy as np
from PIL import Image, ImageDraw, ImageFont

COUNTDOWN_SECONDS = 5
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
INSTRUCTION_TEXT = "드래그로 영역 선택   |   Enter: 확정   |   R: 재선택   |   ESC: 취소"


def capture_screen(monitor: int = 1) -> np.ndarray:
    with mss.mss() as sct:
        info = sct.monitors[monitor]
        shot = sct.grab(info)
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def draw_korean(img_bgr: np.ndarray, text: str, pos: tuple,
                size: int = 22, color: tuple = (255, 255, 255)) -> np.ndarray:
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil)
    try:
        font = ImageFont.truetype(FONT_PATH, size)
    except Exception:
        font = ImageFont.load_default()
    draw.text(pos, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def bake_overlay(img_bgr: np.ndarray, label: str, box_color: tuple) -> np.ndarray:
    """상단 라벨 바 + 하단 조작 안내 바를 이미지에 고정으로 합성"""
    h, w = img_bgr.shape[:2]
    base = img_bgr.copy()

    # 상단 라벨 바 (반투명 검정)
    top_bar = base.copy()
    cv2.rectangle(top_bar, (0, 0), (w, 46), (0, 0, 0), -1)
    cv2.addWeighted(top_bar, 0.65, base, 0.35, 0, base)

    # 하단 조작 안내 바 (반투명 검정)
    bot_bar = base.copy()
    cv2.rectangle(bot_bar, (0, h - 46), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(bot_bar, 0.65, base, 0.35, 0, base)

    # 라벨 텍스트 색상 (ROI 색과 동일)
    r, g, b = box_color[2], box_color[1], box_color[0]  # BGR → RGB
    base = draw_korean(base, label,        (10,  10), size=22, color=(r, g, b))
    base = draw_korean(base, INSTRUCTION_TEXT, (10, h - 38), size=18, color=(255, 255, 255))

    return base


def select_roi_interactive(img_bgr: np.ndarray, label: str,
                           box_color: tuple = (0, 255, 80)) -> dict | None:
    WIN = "PokeOCR ROI Selector"   # cv2 윈도우 타이틀은 ASCII만 지원
    base = bake_overlay(img_bgr, label, box_color)
    state = {"p1": None, "p2": None, "dragging": False}

    def on_mouse(event, x, y, flags, _):
        if event == cv2.EVENT_LBUTTONDOWN:
            state["p1"] = (x, y)
            state["dragging"] = True
        elif event == cv2.EVENT_MOUSEMOVE and state["dragging"]:
            temp = base.copy()
            cv2.rectangle(temp, state["p1"], (x, y), box_color, 2)
            cv2.imshow(WIN, temp)
        elif event == cv2.EVENT_LBUTTONUP:
            state["p2"] = (x, y)
            state["dragging"] = False
            temp = base.copy()
            cv2.rectangle(temp, state["p1"], state["p2"], box_color, 2)
            cv2.imshow(WIN, temp)

    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WIN, on_mouse)
    cv2.imshow(WIN, base)

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key == 13 and state["p1"] and state["p2"]:  # Enter
            break
        elif key == ord("r"):
            state.update({"p1": None, "p2": None, "dragging": False})
            cv2.imshow(WIN, base)
        elif key == 27:  # ESC
            cv2.destroyWindow(WIN)
            return None

    cv2.destroyWindow(WIN)

    x1 = min(state["p1"][0], state["p2"][0])
    y1 = min(state["p1"][1], state["p2"][1])
    x2 = max(state["p1"][0], state["p2"][0])
    y2 = max(state["p1"][1], state["p2"][1])
    return {"left": x1, "top": y1, "width": max(x2 - x1, 1), "height": max(y2 - y1, 1)}


def countdown(seconds: int):
    print(f"\n지금 OBS(게임 화면)로 전환하세요!")
    for i in range(seconds, 0, -1):
        print(f"  {i}초 후 캡처...", end="\r")
        time.sleep(1)
    print("  캡처!              ")


def main():
    print("=== PokeOCR ROI 선택 도구 ===")
    countdown(COUNTDOWN_SECONDS)
    print("전체 화면 캡처 중...")

    full = capture_screen(monitor=1)
    h, w = full.shape[:2]

    scale = min(1.0, 1600 / w)
    display = cv2.resize(full, (int(w * scale), int(h * scale))) if scale < 1.0 else full
    print(f"화면 크기: {w}x{h}  (표시 배율: {scale:.0%})\n")

    # 내 포켓몬 → 초록, 상대 포켓몬 → 빨강
    my_roi_s = select_roi_interactive(
        display,
        label="내 포켓몬 이름 영역 선택",
        box_color=(0, 255, 80),   # BGR 초록
    )
    if my_roi_s is None:
        print("취소됨.")
        return

    opp_roi_s = select_roi_interactive(
        display,
        label="상대 포켓몬 이름 영역 선택",
        box_color=(0, 60, 255),   # BGR 빨강
    )
    if opp_roi_s is None:
        print("취소됨.")
        return

    def rescale(roi: dict) -> dict:
        return {
            "monitor": 1,
            "left":   int(roi["left"]   / scale),
            "top":    int(roi["top"]    / scale),
            "width":  int(roi["width"]  / scale),
            "height": int(roi["height"] / scale),
        }

    my_roi  = rescale(my_roi_s)
    opp_roi = rescale(opp_roi_s)

    config_path = Path("config.json")
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    config["my_pokemon_roi"]       = my_roi
    config["opponent_pokemon_roi"] = opp_roi

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("config.json 저장 완료:")
    print(f"  내 포켓몬 ROI:   {my_roi}")
    print(f"  상대 포켓몬 ROI: {opp_roi}")


if __name__ == "__main__":
    main()
