import json
from pathlib import Path
from typing import Optional


class PokemonDataManager:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.data: dict = self._load()

    def _load(self) -> dict:
        if not self.data_path.exists():
            print(f"[경고] 데이터 파일 없음: {self.data_path}")
            return {}
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_names(self) -> list[str]:
        return list(self.data.keys())

    def get_pokemon(self, name: str) -> Optional[dict]:
        return self.data.get(name)

    def get_speed(self, name: str) -> Optional[int]:
        entry = self.get_pokemon(name)
        return entry.get("speed") if entry else None

    def get_types(self, name: str) -> Optional[list[str]]:
        entry = self.get_pokemon(name)
        return entry.get("types") if entry else None

    def get_megas(self, name: str) -> list[dict]:
        entry = self.get_pokemon(name)
        return entry.get("megas", []) if entry else []

    def total(self) -> int:
        return len(self.data)
