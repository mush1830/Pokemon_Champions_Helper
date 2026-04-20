import ctypes
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.logic import ComparisonResult

WINDOW_TITLE = "PokeOCR"
BG = "#0d1117"
COLOR_TITLE = "#58a6ff"
COLOR_MY = "#3fb950"
COLOR_OPP = "#f78166"
COLOR_RESULT = "#e3b341"
COLOR_STATUS = "#8b949e"
FONT = "Malgun Gothic"


class OverlayWindow:
    def __init__(self, config: dict):
        self.config = config
        self.root = tk.Tk()
        self._build_window()
        self._build_ui()

    def _build_window(self):
        self.root.title(WINDOW_TITLE)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", self.config.get("opacity", 0.88))

        x = self.config.get("x", 10)
        y = self.config.get("y", 10)
        w = self.config.get("width", 340)
        h = self.config.get("height", 190)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg=BG)

        # Allow dragging the overlay
        self.root.bind("<ButtonPress-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag)

    def _build_ui(self):
        pad = {"padx": 10}

        tk.Label(
            self.root, text="PokeOCR  Speed Check",
            bg=BG, fg=COLOR_TITLE,
            font=(FONT, 10, "bold")
        ).pack(pady=(8, 2), **pad, anchor="w")

        tk.Frame(self.root, bg="#30363d", height=1).pack(fill="x", padx=8)

        self.my_label = tk.Label(
            self.root, text="내 포켓몬: -",
            bg=BG, fg=COLOR_MY, font=(FONT, 10), anchor="w"
        )
        self.my_label.pack(pady=(6, 0), **pad, fill="x")

        self.opp_label = tk.Label(
            self.root, text="상대 포켓몬: -",
            bg=BG, fg=COLOR_OPP, font=(FONT, 10), anchor="w"
        )
        self.opp_label.pack(pady=(2, 0), **pad, fill="x")

        tk.Frame(self.root, bg="#30363d", height=1).pack(fill="x", padx=8, pady=6)

        self.result_label = tk.Label(
            self.root, text="선공: -",
            bg=BG, fg=COLOR_RESULT, font=(FONT, 12, "bold"), anchor="w"
        )
        self.result_label.pack(**pad, fill="x")

        self.ocr_label = tk.Label(
            self.root, text="OCR: -",
            bg=BG, fg="#484f58", font=(FONT, 7), anchor="w"
        )
        self.ocr_label.pack(**pad, fill="x")

        self.status_label = tk.Label(
            self.root, text="초기화 중...",
            bg=BG, fg=COLOR_STATUS, font=(FONT, 8), anchor="w"
        )
        self.status_label.pack(side="bottom", pady=(0, 6), **pad, fill="x")

    def _on_drag_start(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _apply_click_through(self):
        if not self.config.get("click_through", True):
            return
        try:
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            hwnd = ctypes.windll.user32.FindWindowW(None, WINDOW_TITLE)
            if hwnd:
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(
                    hwnd, GWL_EXSTYLE,
                    style | WS_EX_LAYERED | WS_EX_TRANSPARENT
                )
        except Exception as e:
            print(f"[경고] 클릭 스루 설정 실패: {e}")

    def update(self, result: "ComparisonResult"):
        def _update():
            my_spd = result.my_speed if result.my_speed is not None else "?"
            opp_spd = result.opp_speed if result.opp_speed is not None else "?"

            self.my_label.config(
                text=f"내 포켓몬: {result.my_name or '인식 실패'} (Spd {my_spd})"
            )
            self.opp_label.config(
                text=f"상대 포켓몬: {result.opp_name or '인식 실패'} (Spd {opp_spd})"
            )

            if result.faster == "my":
                txt = f"선공: {result.my_name}  (내가 빠름)"
                clr = COLOR_MY
            elif result.faster == "opponent":
                txt = f"선공: {result.opp_name}  (상대가 빠름)"
                clr = COLOR_OPP
            elif result.faster == "tie":
                txt = "동속  (선공 동일)"
                clr = COLOR_RESULT
            else:
                txt = "선공: 알 수 없음"
                clr = COLOR_STATUS

            self.result_label.config(text=txt, fg=clr)

            ocr_info = (
                f"OCR: [{result.my_raw_ocr[:15]}] / [{result.opp_raw_ocr[:15]}]"
            )
            self.ocr_label.config(text=ocr_info)

        self.root.after(0, _update)

    def set_status(self, text: str):
        self.root.after(0, lambda: self.status_label.config(text=text))

    def run(self):
        self.root.after(200, self._apply_click_through)
        self.root.mainloop()
