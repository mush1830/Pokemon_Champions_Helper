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
from pathlib import Path

import cv2
import mss
import numpy as np
from PIL import Image


def capture_screen(monitor: int = 1) -> np.ndarray:
    with mss.mss() as sct:
        info = sct.monitors[monitor]
        shot = sct.grab(info)
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def select_roi_interactive(img_bgr: np.ndarray, title: str) -> dict | None:
    clone = img_bgr.copy()
    state = {"p1": None, "p2": None, "dragging": False}

    def on_mouse(event, x, y, flags, _):
        if event == cv2.EVENT_LBUTTONDOWN:
            state["p1"] = (x, y)
            state["dragging"] = True
        elif event == cv2.EVENT_MOUSEMOVE and state["dragging"]:
            temp = clone.copy()
            cv2.rectangle(temp, state["p1"], (x, y), (0, 255, 80), 2)
            cv2.imshow(title, temp)
        elif event == cv2.EVENT_LBUTTONUP:
            state["p2"] = (x, y)
            state["dragging"] = False
            temp = clone.copy()
            cv2.rectangle(temp, state["p1"], state["p2"], (0, 255, 80), 2)
            cv2.imshow(title, temp)

    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(title, on_mouse)
    cv2.imshow(title, clone)
    print(f"\n[{title}]")
    print("  드래그로 영역 선택 → Enter 확정 / R 재선택 / ESC 취소")

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key == 13 and state["p1"] and state["p2"]:  # Enter
            break
        elif key == ord("r"):
            state.update({"p1": None, "p2": None, "dragging": False})
            cv2.imshow(title, clone)
        elif key == 27:  # ESC
            cv2.destroyWindow(title)
            return None

    cv2.destroyWindow(title)

    x1 = min(state["p1"][0], state["p2"][0])
    y1 = min(state["p1"][1], state["p2"][1])
    x2 = max(state["p1"][0], state["p2"][0])
    y2 = max(state["p1"][1], state["p2"][1])

    return {"left": x1, "top": y1, "width": max(x2 - x1, 1), "height": max(y2 - y1, 1)}


def main():
    print("=== PokeOCR ROI 선택 도구 ===")
    print("전체 화면을 캡처합니다...")

    full = capture_screen(monitor=1)
    h, w = full.shape[:2]

    # 화면이 크면 50%로 축소 표시
    scale = min(1.0, 1600 / w)
    display = cv2.resize(full, (int(w * scale), int(h * scale))) if scale < 1.0 else full

    print(f"화면 크기: {w}x{h}  (표시 배율: {scale:.0%})")

    my_roi_s = select_roi_interactive(display, "내 포켓몬 이름 영역 선택")
    if my_roi_s is None:
        print("취소됨.")
        return

    opp_roi_s = select_roi_interactive(display, "상대 포켓몬 이름 영역 선택")
    if opp_roi_s is None:
        print("취소됨.")
        return

    def rescale(roi: dict) -> dict:
        return {
            "monitor": 1,
            "left": int(roi["left"] / scale),
            "top": int(roi["top"] / scale),
            "width": int(roi["width"] / scale),
            "height": int(roi["height"] / scale),
        }

    my_roi = rescale(my_roi_s)
    opp_roi = rescale(opp_roi_s)

    config_path = Path("config.json")
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    config["my_pokemon_roi"] = my_roi
    config["opponent_pokemon_roi"] = opp_roi

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("\nconfig.json 저장 완료:")
    print(f"  내 포켓몬 ROI:  {my_roi}")
    print(f"  상대 포켓몬 ROI: {opp_roi}")


if __name__ == "__main__":
    main()
