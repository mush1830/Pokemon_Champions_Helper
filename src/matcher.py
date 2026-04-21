from typing import Optional
from rapidfuzz.distance import Levenshtein

_INITIALS = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
_VOWELS   = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
_FINALS   = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"


def _to_jamo(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            code -= 0xAC00
            out.append(_INITIALS[code // 588])
            out.append(_VOWELS[(code % 588) // 28])
            f = _FINALS[code % 28]
            if f != " ":
                out.append(f)
        else:
            out.append(ch)
    return "".join(out)


def _jamo_sim(j1: str, j2: str) -> float:
    dist = Levenshtein.distance(j1, j2)
    return 1 - dist / max(len(j1), len(j2), 1)


class PokemonMatcher:
    def __init__(self, name_list: list[str]):
        self.name_list = name_list
        self._jamo_map = {name: _to_jamo(name) for name in name_list}

    def find_best_match(self, raw_text: str, threshold: float = 0.5) -> Optional[str]:
        if not raw_text or not self.name_list:
            return None

        if raw_text in self.name_list:
            return raw_text

        for word in raw_text.split():
            if word in self.name_list:
                return word

        queries = list(dict.fromkeys([raw_text] + raw_text.split()))
        jamo_queries = [_to_jamo(q) for q in queries]

        best_score = 0.0
        best_name = None
        for name, jamo_name in self._jamo_map.items():
            for jq in jamo_queries:
                score = _jamo_sim(jq, jamo_name)
                if score >= threshold and score > best_score:
                    best_score = score
                    best_name = name

        return best_name
