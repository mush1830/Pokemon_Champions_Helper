"""
pikalytics.com/pokedex?l=kor 를 Selenium으로 크롤링하여
data/pokemon_data.json 에 저장하는 스크립트.

사용법:
    python scripts/crawl_pikalytics.py

주의: pikalytics는 JS 렌더링 페이지입니다. Chrome이 설치되어 있어야 합니다.
CSS 선택자는 사이트 업데이트에 따라 변경될 수 있습니다.
안정적인 대안: scripts/fetch_pokeapi.py 사용 권장
"""

import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

TARGET_URL = "https://www.pikalytics.com/pokedex?l=kor"
OUTPUT = Path("data/pokemon_data.json")

# 스탯 순서: HP, 공격, 방어, 특공, 특방, 스피드 (인덱스 5)
SPEED_STAT_INDEX = 5


def build_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )


def scroll_to_bottom(driver: webdriver.Chrome):
    """무한 스크롤 페이지를 끝까지 내림"""
    prev_height = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height


def parse_pokemon(driver: webdriver.Chrome) -> dict:
    pokemon_data: dict = {}

    # 여러 선택자를 순서대로 시도
    item_selectors = [
        ".pokedex-list-pokemon",
        ".pokemon-card",
        "[class*='pokedex-item']",
        "[class*='pokemon-item']",
    ]
    name_selectors = [
        ".pokemon-name",
        "[class*='name']",
        "h2", "h3",
    ]
    stat_selectors = [
        ".base-stat",
        "[class*='stat']",
        "td",
    ]

    items = []
    for sel in item_selectors:
        items = driver.find_elements(By.CSS_SELECTOR, sel)
        if items:
            print(f"  아이템 선택자 적용: {sel} ({len(items)}개)")
            break

    if not items:
        print("[경고] 포켓몬 목록 요소를 찾지 못했습니다.")
        print("  개발자 도구로 올바른 CSS 선택자를 확인하세요.")
        return pokemon_data

    for item in items:
        try:
            name = None
            for ns in name_selectors:
                els = item.find_elements(By.CSS_SELECTOR, ns)
                if els:
                    name = els[0].text.strip()
                    if name:
                        break

            stats = []
            for ss in stat_selectors:
                els = item.find_elements(By.CSS_SELECTOR, ss)
                if len(els) >= 6:
                    stats = els
                    break

            if name and len(stats) > SPEED_STAT_INDEX:
                speed_text = stats[SPEED_STAT_INDEX].text.strip()
                speed = int("".join(filter(str.isdigit, speed_text)))
                pokemon_data[name] = {"speed": speed}

        except Exception:
            continue

    return pokemon_data


def main():
    print("pikalytics.com 크롤링 시작...")
    driver = build_driver()

    try:
        driver.get(TARGET_URL)
        print("페이지 로딩 중...")

        # 최대 30초 대기
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)

        print("스크롤 중...")
        scroll_to_bottom(driver)

        print("데이터 파싱 중...")
        data = parse_pokemon(driver)

    finally:
        driver.quit()

    if not data:
        print("\n[실패] 데이터를 가져오지 못했습니다.")
        print("scripts/fetch_pokeapi.py 를 대신 사용하세요.")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        with open(OUTPUT, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing.update(data)
        data = existing

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {len(data)}개 포켓몬 저장 → {OUTPUT}")


if __name__ == "__main__":
    main()
