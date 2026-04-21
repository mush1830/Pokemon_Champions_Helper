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
        self._scan_callback = None
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
        w = self.config.get("width", 510)
        h = self.config.get("height", 360)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg=BG)

        self.root.bind("<ButtonPress-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag)

        self._menu = tk.Menu(self.root, tearoff=0)
        self._menu.add_command(label="종료", command=self.root.destroy)
        self.root.bind("<ButtonPress-3>", lambda e: self._menu.tk_popup(e.x_root, e.y_root))

    def _build_ui(self):
        pad = {"padx": 14}

        # 타이틀 행
        title_row = tk.Frame(self.root, bg=BG)
        title_row.pack(fill="x", pady=(10, 4))

        tk.Label(
            title_row, text="PokeOCR  Speed Check",
            bg=BG, fg=COLOR_TITLE,
            font=(FONT, 13, "bold")
        ).pack(side="left", padx=14)

        tk.Button(
            title_row, text="✕",
            bg="#3a1a1a", fg="#ff5555",
            activebackground="#ff5555", activeforeground="white",
            font=(FONT, 11, "bold"),
            relief="flat", bd=0, padx=8, pady=0,
            cursor="hand2",
            command=self.root.destroy,
        ).pack(side="right", padx=8)

        tk.Frame(self.root, bg="#30363d", height=1).pack(fill="x", padx=10)

        # 상대 포켓몬 (먼저)
        self.opp_label = tk.Label(
            self.root, text="상대 포켓몬: -",
            bg=BG, fg=COLOR_OPP, font=(FONT, 14, "bold"), anchor="w"
        )
        self.opp_label.pack(pady=(10, 0), **pad, fill="x")

        self.opp_weak_label = tk.Label(
            self.root, text="  약점: -",
            bg=BG, fg="#8b949e", font=(FONT, 12), anchor="w",
            wraplength=480, justify="left"
        )
        self.opp_weak_label.pack(pady=(2, 0), **pad, fill="x")

        tk.Frame(self.root, bg="#21262d", height=1).pack(fill="x", padx=10, pady=8)

        # 내 포켓몬
        self.my_label = tk.Label(
            self.root, text="내 포켓몬: -",
            bg=BG, fg=COLOR_MY, font=(FONT, 14, "bold"), anchor="w"
        )
        self.my_label.pack(pady=(0, 0), **pad, fill="x")

        self.my_weak_label = tk.Label(
            self.root, text="  약점: -",
            bg=BG, fg="#8b949e", font=(FONT, 12), anchor="w",
            wraplength=480, justify="left"
        )
        self.my_weak_label.pack(pady=(2, 0), **pad, fill="x")

        tk.Frame(self.root, bg="#30363d", height=1).pack(fill="x", padx=10, pady=8)

        self.result_label = tk.Label(
            self.root, text="선공: -",
            bg=BG, fg=COLOR_RESULT, font=(FONT, 16, "bold"), anchor="w"
        )
        self.result_label.pack(**pad, fill="x")

        self.ocr_label = tk.Label(
            self.root, text="OCR: -",
            bg=BG, fg="#484f58", font=(FONT, 9), anchor="w"
        )
        self.ocr_label.pack(**pad, fill="x")

        self.scan_btn = tk.Button(
            self.root, text="확인",
            bg="#1f6feb", fg="white",
            activebackground="#388bfd", activeforeground="white",
            disabledforeground="#555555",
            font=(FONT, 13, "bold"),
            relief="flat", bd=0, pady=7,
            cursor="hand2",
            command=self._on_scan_click,
        )
        self.scan_btn.pack(fill="x", padx=10, pady=(8, 4))

        self.status_label = tk.Label(
            self.root, text="초기화 중...",
            bg=BG, fg=COLOR_STATUS, font=(FONT, 10), anchor="w"
        )
        self.status_label.pack(side="bottom", pady=(0, 8), **pad, fill="x")

    def set_scan_callback(self, fn):
        self._scan_callback = fn

    def _on_scan_click(self):
        if self._scan_callback:
            self._scan_callback()

    def set_scan_enabled(self, enabled: bool):
        def _update():
            if enabled:
                self.scan_btn.config(state="normal", text="확인", bg="#1f6feb")
            else:
                self.scan_btn.config(state="disabled", text="스캔 중...", bg="#2a2a3a")
        self.root.after(0, _update)

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

    @staticmethod
    def _fmt_speed(speed, megas: list) -> str:
        base = str(speed) if speed is not None else "?"
        if not megas:
            return base
        parts = [base]
        for m in megas:
            slug = m["slug"]
            if slug.endswith("-mega-x"):
                label = "메가X"
            elif slug.endswith("-mega-y"):
                label = "메가Y"
            else:
                label = "메가"
            parts.append(f"{label} {m['speed']}")
        return " / ".join(parts)

    def update(self, result: "ComparisonResult"):
        def _update():
            my_spd_txt = self._fmt_speed(result.my_speed, result.my_megas)
            opp_spd_txt = self._fmt_speed(result.opp_speed, result.opp_megas)

            self.opp_label.config(
                text=f"상대 포켓몬: {result.opp_name or '인식 실패'} (Spd {opp_spd_txt})"
            )
            self.opp_weak_label.config(text=f"  약점: {result.opp_weaknesses}")
            self.my_label.config(
                text=f"내 포켓몬: {result.my_name or '인식 실패'} (Spd {my_spd_txt})"
            )
            self.my_weak_label.config(text=f"  약점: {result.my_weaknesses}")

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
            self.ocr_label.config(
                text=f"OCR: [{result.my_raw_ocr[:15]}] / [{result.opp_raw_ocr[:15]}]"
            )

        self.root.after(0, _update)

    def set_status(self, text: str):
        self.root.after(0, lambda: self.status_label.config(text=text))

    def run(self):
        self.root.after(200, self._apply_click_through)
        self.root.mainloop()
