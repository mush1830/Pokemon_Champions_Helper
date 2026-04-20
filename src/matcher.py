from typing import Optional
from rapidfuzz import process, fuzz


class PokemonMatcher:
    def __init__(self, name_list: list[str]):
        self.name_list = name_list

    def find_best_match(self, raw_text: str, threshold: int = 55) -> Optional[str]:
        if not raw_text or not self.name_list:
            return None

        # Try exact match first
        if raw_text in self.name_list:
            return raw_text

        # Try partial word matches (OCR often includes extra chars)
        for word in raw_text.split():
            if word in self.name_list:
                return word

        # Fuzzy match over full raw text
        result = process.extractOne(
            raw_text,
            self.name_list,
            scorer=fuzz.WRatio,
            score_cutoff=threshold,
        )
        if result:
            return result[0]

        # Fuzzy match word-by-word for better partial recognition
        best_score = 0
        best_name = None
        for word in raw_text.split():
            r = process.extractOne(
                word,
                self.name_list,
                scorer=fuzz.WRatio,
                score_cutoff=threshold,
            )
            if r and r[1] > best_score:
                best_score = r[1]
                best_name = r[0]

        return best_name
