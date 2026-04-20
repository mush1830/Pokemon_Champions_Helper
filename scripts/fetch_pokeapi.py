"""
PokéAPI를 이용해 한글 포켓몬 이름 + 스피드 종족값을 수집하여
data/pokemon_data.json 에 저장하는 스크립트.

사용법:
    python scripts/fetch_pokeapi.py
    python scripts/fetch_pokeapi.py --max 151   # 1세대만
"""

import argparse
import json
import time
from pathlib import Path

import requests

API_BASE = "https://pokeapi.co/api/v2"
OUTPUT = Path("data/pokemon_data.json")
TOTAL_POKEMON = 1025  # Gen 1~9


def get_json(url: str, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1.5)
            else:
                print(f"  [실패] {url} - {e}")
    return None


def fetch_all(max_pokemon: int) -> dict:
    pokemon_data: dict = {}

    for i in range(1, max_pokemon + 1):
        # 기본 스탯 조회
        poke = get_json(f"{API_BASE}/pokemon/{i}")
        if not poke:
            continue

        speed = None
        for stat in poke["stats"]:
            if stat["stat"]["name"] == "speed":
                speed = stat["base_stat"]
                break

        # 한글 이름 조회
        species = get_json(poke["species"]["url"])
        if not species:
            continue

        kor_name = None
        for entry in species["names"]:
            if entry["language"]["name"] == "ko":
                kor_name = entry["name"]
                break

        if kor_name and speed is not None:
            pokemon_data[kor_name] = {
                "speed": speed,
                "national_no": i,
            }

        if i % 50 == 0 or i == max_pokemon:
            print(f"  진행: {i}/{max_pokemon}  ({len(pokemon_data)}개 수집)")

        # API 부하 방지
        time.sleep(0.05)

    return pokemon_data


def main():
    parser = argparse.ArgumentParser(description="PokéAPI 데이터 수집기")
    parser.add_argument(
        "--max", type=int, default=TOTAL_POKEMON,
        help=f"수집할 최대 포켓몬 번호 (기본: {TOTAL_POKEMON})"
    )
    parser.add_argument(
        "--merge", action="store_true",
        help="기존 데이터에 병합 (기본: 덮어쓰기)"
    )
    args = parser.parse_args()

    print(f"포켓몬 데이터 수집 시작 (1~{args.max}번)")
    print("완료까지 수분이 걸릴 수 있습니다...\n")

    new_data = fetch_all(args.max)

    if args.merge and OUTPUT.exists():
        with open(OUTPUT, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing.update(new_data)
        new_data = existing
        print(f"\n기존 데이터에 병합됨")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {len(new_data)}개 포켓몬 저장 → {OUTPUT}")


if __name__ == "__main__":
    main()
