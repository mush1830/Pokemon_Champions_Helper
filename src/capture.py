import mss
import mss.tools
from PIL import Image


class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()

    def capture_roi(self, roi_config: dict) -> Image.Image:
        monitor = {
            "top": roi_config["top"],
            "left": roi_config["left"],
            "width": roi_config["width"],
            "height": roi_config["height"],
            "mon": roi_config.get("monitor", 1),
        }
        screenshot = self.sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    def capture_monitor(self, monitor_index: int = 1) -> Image.Image:
        info = self.sct.monitors[monitor_index]
        screenshot = self.sct.grab(info)
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
