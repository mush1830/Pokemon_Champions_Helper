설치 및 실행 순서
1. 패키지 설치

pip install -r requirements.txt
2. 전체 포켓몬 데이터 수집 (권장, ~10분 소요)

python scripts/fetch_pokeapi.py
# 또는 1~3세대만 빠르게:
python scripts/fetch_pokeapi.py --max 386
3. ROI 영역 설정 (처음 1회)

python scripts/roi_selector.py
OBS 화면에서 내 포켓몬 이름 위치와 상대 포켓몬 이름 위치를 드래그로 지정.

4. 실행

python main.py
F9 누를 때마다 스캔 → 오버레이 갱신. Ctrl+Shift+Q 로 종료.

주요 설계 포인트
모듈	전략
OCR	EasyOCR 한글 모드 + Adaptive Threshold + 2x 업스케일
이름 매칭	rapidfuzz.WRatio fuzzy 매칭, 단어별 개별 시도도 병행
오버레이	tkinter overrideredirect + -topmost + Win32 클릭스루
스레딩	OCR는 백그라운드 스레드, UI 갱신은 root.after(0, ...) 로 안전 처리
