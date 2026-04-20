import json
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
        try:
            ocr_engine[0] = OCREngine(config["ocr"])
            ocr_ready.set()
            overlay.set_status(f"준비 완료  |  단축키: {config['hotkey']}  |  Ctrl+Shift+Q 종료")
            print(f"[정보] OCR 초기화 완료. 단축키 [{config['hotkey']}] 로 스캔하세요.")
        except Exception as e:
            overlay.set_status(f"OCR 초기화 오류: {e}")
            print(f"[오류] OCR 초기화 실패: {e}")

    def process_and_update():
        try:
            overlay.set_status("화면 캡처 중...")
            my_img = capture.capture_roi(config["my_pokemon_roi"])
            opp_img = capture.capture_roi(config["opponent_pokemon_roi"])

            overlay.set_status("OCR 실행 중...")
            my_raw = ocr_engine[0].recognize(my_img)
            opp_raw = ocr_engine[0].recognize(opp_img)
            print(f"[OCR] 내: '{my_raw}'  /  상대: '{opp_raw}'")

            my_name = matcher.find_best_match(my_raw)
            opp_name = matcher.find_best_match(opp_raw)
            print(f"[매칭] 내: {my_name}  /  상대: {opp_name}")

            result = comparator.compare(my_name, opp_name, my_raw, opp_raw)
            overlay.update(result)
            overlay.set_status(f"완료  |  단축키: {config['hotkey']}")
        except Exception as e:
            overlay.set_status(f"오류: {e}")
            print(f"[오류] 처리 중 예외: {e}")
        finally:
            is_scanning.clear()

    def on_hotkey():
        if not ocr_ready.is_set() or is_scanning.is_set():
            return
        is_scanning.set()
        threading.Thread(target=process_and_update, daemon=True).start()

    keyboard.add_hotkey(config["hotkey"], on_hotkey)
    keyboard.add_hotkey("ctrl+shift+q", lambda: sys.exit(0))

    threading.Thread(target=init_ocr, daemon=True).start()
    overlay.run()


if __name__ == "__main__":
    main()
