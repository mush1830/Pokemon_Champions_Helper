TYPE_KO = {
    "normal": "노말", "fire": "불꽃", "water": "물", "electric": "전기",
    "grass": "풀", "ice": "얼음", "fighting": "격투", "poison": "독",
    "ground": "땅", "flying": "비행", "psychic": "에스퍼", "bug": "벌레",
    "rock": "바위", "ghost": "고스트", "dragon": "드래곤", "dark": "악",
    "steel": "강철", "fairy": "페어리",
}

_SUPER: dict[str, list[str]] = {
    "normal":   [],
    "fire":     ["grass", "ice", "bug", "steel"],
    "water":    ["fire", "ground", "rock"],
    "electric": ["water", "flying"],
    "grass":    ["water", "ground", "rock"],
    "ice":      ["grass", "ground", "flying", "dragon"],
    "fighting": ["normal", "ice", "rock", "dark", "steel"],
    "poison":   ["grass", "fairy"],
    "ground":   ["fire", "electric", "poison", "rock", "steel"],
    "flying":   ["grass", "fighting", "bug"],
    "psychic":  ["fighting", "poison"],
    "bug":      ["grass", "psychic", "dark"],
    "rock":     ["fire", "ice", "flying", "bug"],
    "ghost":    ["psychic", "ghost"],
    "dragon":   ["dragon"],
    "dark":     ["psychic", "ghost"],
    "steel":    ["ice", "rock", "fairy"],
    "fairy":    ["fighting", "dragon", "dark"],
}

_RESIST: dict[str, list[str]] = {
    "normal":   ["rock", "steel"],
    "fire":     ["fire", "water", "rock", "dragon"],
    "water":    ["water", "grass", "dragon"],
    "electric": ["electric", "grass", "dragon"],
    "grass":    ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"],
    "ice":      ["ice"],
    "fighting": ["poison", "bug", "psychic", "flying", "fairy"],
    "poison":   ["poison", "ground", "rock", "ghost"],
    "ground":   ["grass", "bug"],
    "flying":   ["electric", "rock", "steel"],
    "psychic":  ["psychic", "steel"],
    "bug":      ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"],
    "rock":     ["fighting", "ground", "steel"],
    "ghost":    ["dark"],
    "dragon":   ["steel"],
    "dark":     ["fighting", "dark", "fairy"],
    "steel":    ["fire", "water", "electric", "steel"],
    "fairy":    ["fire", "poison", "steel"],
}

_IMMUNE: dict[str, list[str]] = {
    "normal":   ["ghost"],
    "electric": ["ground"],
    "fighting": ["ghost"],
    "poison":   ["steel"],
    "ground":   ["flying"],
    "psychic":  ["dark"],
    "ghost":    ["normal"],
    "dragon":   ["fairy"],
}


def _eff(attacker: str, defender: str) -> float:
    if defender in _IMMUNE.get(attacker, []):
        return 0.0
    if defender in _SUPER.get(attacker, []):
        return 2.0
    if defender in _RESIST.get(attacker, []):
        return 0.5
    return 1.0


def format_weaknesses(types: list[str]) -> str:
    """2x/4x 약점 타입을 한글로 반환. 예: '불꽃×4  격투  땅'"""
    weak = []
    for attacker in TYPE_KO:
        mult = 1.0
        for defender in types:
            mult *= _eff(attacker, defender)
        if mult >= 2.0:
            weak.append((TYPE_KO[attacker], mult))
    weak.sort(key=lambda x: -x[1])
    if not weak:
        return "없음"
    parts = [f"{name}×4" if m >= 4.0 else name for name, m in weak]
    return "  ".join(parts)
