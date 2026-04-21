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


def _fetch_mega_forms(species: dict) -> list[dict]:
    """species varieties에서 메가진화 폼을 찾아 스피드/타입/이름 반환."""
    megas = []
    for variety in species.get("varieties", []):
        slug = variety["pokemon"]["name"]
        if "mega" not in slug:
            continue
        poke = get_json(variety["pokemon"]["url"])
        if not poke:
            continue
        speed = next((s["base_stat"] for s in poke["stats"] if s["stat"]["name"] == "speed"), None)
        types = [t["type"]["name"] for t in sorted(poke["types"], key=lambda x: x["slot"])]

        # 폼 엔드포인트에서 한글 이름 시도
        form = get_json(f"{API_BASE}/pokemon-form/{slug}/")
        ko_name = None
        if form:
            for n in form.get("names", []):
                if n["language"]["name"] == "ko":
                    ko_name = n["name"]
                    break

        if speed is not None:
            megas.append({"slug": slug, "ko_name": ko_name, "speed": speed, "types": types})
        time.sleep(0.05)
    return megas


def fetch_all(max_pokemon: int) -> dict:
    pokemon_data: dict = {}

    for i in range(1, max_pokemon + 1):
        poke = get_json(f"{API_BASE}/pokemon/{i}")
        if not poke:
            continue

        speed = next((s["base_stat"] for s in poke["stats"] if s["stat"]["name"] == "speed"), None)
        types = [t["type"]["name"] for t in sorted(poke["types"], key=lambda x: x["slot"])]

        species = get_json(poke["species"]["url"])
        if not species:
            continue

        kor_name = None
        for entry in species["names"]:
            if entry["language"]["name"] == "ko":
                kor_name = entry["name"]
                break

        if kor_name and speed is not None:
            entry = {"speed": speed, "national_no": i, "types": types}
            megas = _fetch_mega_forms(species)
            if megas:
                entry["megas"] = megas
            pokemon_data[kor_name] = entry

        if i % 50 == 0 or i == max_pokemon:
            print(f"  진행: {i}/{max_pokemon}  ({len(pokemon_data)}개 수집)")

        time.sleep(0.05)

    return pokemon_data


def add_megas_to_existing(data_path: Path) -> dict:
    """기존 데이터에 megas 필드만 추가."""
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data)
    for idx, (name, entry) in enumerate(data.items(), 1):
        no = entry.get("national_no")
        if not no:
            continue
        species = get_json(f"{API_BASE}/pokemon-species/{no}/")
        if species:
            megas = _fetch_mega_forms(species)
            if megas:
                entry["megas"] = megas
                print(f"  [{name}] 메가진화 {len(megas)}개 추가")
        if idx % 100 == 0 or idx == total:
            print(f"  진행: {idx}/{total}")
        time.sleep(0.05)

    return data


def add_types_to_existing(data_path: Path) -> dict:
    """기존 데이터에 types 필드만 추가."""
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data)
    for idx, (name, entry) in enumerate(data.items(), 1):
        no = entry.get("national_no")
        if not no:
            continue
        poke = get_json(f"{API_BASE}/pokemon/{no}")
        if poke:
            entry["types"] = [t["type"]["name"] for t in sorted(poke["types"], key=lambda x: x["slot"])]
        if idx % 50 == 0 or idx == total:
            print(f"  진행: {idx}/{total}")
        time.sleep(0.05)

    return data


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
    parser.add_argument(
        "--add-types", action="store_true",
        help="기존 데이터에 types 필드만 추가 (빠름)"
    )
    parser.add_argument(
        "--add-megas", action="store_true",
        help="기존 데이터에 메가진화 데이터만 추가"
    )
    args = parser.parse_args()

    if args.add_megas:
        if not OUTPUT.exists():
            print("[오류] 기존 데이터 없음.")
            return
        print("메가진화 데이터 추가 중...\n")
        new_data = add_megas_to_existing(OUTPUT)
    elif args.add_types:
        if not OUTPUT.exists():
            print("[오류] 기존 데이터 없음. 먼저 전체 수집을 실행하세요.")
            return
        print(f"타입 데이터 추가 중...\n")
        new_data = add_types_to_existing(OUTPUT)
    else:
        print(f"포켓몬 데이터 수집 시작 (1~{args.max}번)")
        print("완료까지 수분이 걸릴 수 있습니다...\n")
        new_data = fetch_all(args.max)

    if args.merge and not args.add_types and not args.add_megas and OUTPUT.exists():
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
