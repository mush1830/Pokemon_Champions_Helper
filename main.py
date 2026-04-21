import json
import signal
import sys
import threading
from pathlib import Path

import keyboard

from src.capture import ScreenCapture
from src.data_manager import PokemonDataManager
from src.logic import SpeedComparator
from src.matcher import PokemonMatcher
from src.ocr import OCREngine
from src.overlay import OverlayWindow


def load_config() -> dict:
    path = Path("config.json")
    if not path.exists():
        print("[경고] config.json 없음. 기본값 사용.")
        return _default_config()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _default_config() -> dict:
    return {
        "hotkey": "F9",
        "my_pokemon_roi": {"monitor": 1, "top": 600, "left": 50, "width": 350, "height": 60},
        "opponent_pokemon_roi": {"monitor": 1, "top": 100, "left": 900, "width": 350, "height": 60},
        "overlay": {"x": 10, "y": 10, "width": 340, "height": 190, "opacity": 0.88, "click_through": True},
        "ocr": {"language": ["ko"], "preprocessing": True},
    }


def main():
    config = load_config()

    capture = ScreenCapture()
    data_manager = PokemonDataManager("data/pokemon_data.json")
    matcher = PokemonMatcher(data_manager.get_all_names())
    comparator = SpeedComparator(data_manager)
    overlay = OverlayWindow(config["overlay"])

    print(f"[정보] 포켓몬 데이터 {data_manager.total()}개 로드됨")

    ocr_engine: list[OCREngine | None] = [None]
    is_scanning = threading.Event()
    ocr_ready = threading.Event()

    def init_ocr():
        overlay.set_status("OCR 엔진 초기화 중... (첫 실행시 모델 다운로드)")
        overlay.set_scan_enabled(False)
        try:
            ocr_engine[0] = OCREngine(config["ocr"])
            ocr_ready.set()
            overlay.set_scan_enabled(True)
            overlay.set_status("준비 완료  |  Ctrl+Shift+Q 종료")
            print("[정보] OCR 초기화 완료.")
        except Exception as e:
            overlay.set_status(f"OCR 초기화 오류: {e}")
            print(f"[오류] OCR 초기화 실패: {e}")

    def process_and_update():
        try:
            overlay.set_status("화면 캡처 중...")
            my_img = capture.capture_roi(config["my_pokemon_roi"])
            opp_img = capture.capture_roi(config["opponent_pokemon_roi"])

            overlay.set_status("OCR 실행 중...")
            my_raw = ocr_engine[0].recognize(my_img, label="my")
            opp_raw = ocr_engine[0].recognize(opp_img, label="opp")
            print(f"[OCR] 내: '{my_raw}'  /  상대: '{opp_raw}'")

            my_name = matcher.find_best_match(my_raw)
            opp_name = matcher.find_best_match(opp_raw)
            print(f"[매칭] 내: {my_name}  /  상대: {opp_name}")

            result = comparator.compare(my_name, opp_name, my_raw, opp_raw)
            overlay.update(result)
            overlay.set_status("완료  |  Ctrl+Shift+Q 종료")
        except Exception as e:
            err_type = type(e).__name__
            overlay.set_status(f"오류 [{err_type}]: {e}")
            print(f"[오류] 처리 중 예외 ({err_type}): {e}")
        finally:
            is_scanning.clear()
            overlay.set_scan_enabled(True)

    SCAN_TIMEOUT = 30

    def on_scan():
        if not ocr_ready.is_set() or is_scanning.is_set():
            return
        is_scanning.set()
        overlay.set_scan_enabled(False)

        def on_timeout():
            if is_scanning.is_set():
                is_scanning.clear()
                overlay.set_scan_enabled(True)
                overlay.set_status("스캔 시간 초과 (30초) — 다시 시도하세요")
                print("[경고] 스캔 30초 초과로 자동 취소됨")

        timer = threading.Timer(SCAN_TIMEOUT, on_timeout)
        timer.daemon = True
        timer.start()

        def run():
            try:
                process_and_update()
            finally:
                timer.cancel()

        threading.Thread(target=run, daemon=True).start()

    overlay.set_scan_callback(on_scan)
    keyboard.add_hotkey("ctrl+shift+q", overlay.root.destroy)

    # Ctrl+C 정상 동작
    signal.signal(signal.SIGINT, lambda *_: overlay.root.after(0, overlay.root.destroy))

    threading.Thread(target=init_ocr, daemon=True).start()
    overlay.run()


if __name__ == "__main__":
    main()
