@echo off
chcp 65001 >nul
title PokeOCR 삭제

echo ======================================
echo   PokeOCR 삭제 프로그램
echo ======================================
echo.
echo 다음 항목이 삭제됩니다:
echo   - AI 모델 캐시 (~10GB)
echo   - 설치된 패키지 (~5GB)
echo.
echo 정말 삭제하시겠습니까?
echo 계속하려면 아무 키나, 취소하려면 창을 닫으세요.
pause >nul

:: ── AI 모델 캐시 삭제 ───────────────────
echo.
echo [1/2] AI 모델 캐시 삭제 중...
set HF_CACHE=%USERPROFILE%\.cache\huggingface\hub
if exist "%HF_CACHE%\models--datalab-to--chandra-ocr-2" (
    rmdir /s /q "%HF_CACHE%\models--datalab-to--chandra-ocr-2"
    echo       완료. (~10GB 확보)
) else (
    echo       모델 캐시 없음. 건너뜀.
)

:: ── pip 패키지 삭제 ─────────────────────
echo [2/2] 패키지 삭제 중...
python -m pip uninstall -y ^
    torch chandra-ocr transformers ^
    mss Pillow opencv-python rapidfuzz ^
    keyboard requests beautifulsoup4 ^
    selenium webdriver-manager ^
    bitsandbytes accelerate >nul 2>&1

echo       완료.

echo.
echo ======================================
echo   삭제 완료!
echo   이 폴더(PokeOCR)는 직접 삭제하세요.
echo ======================================
echo.
pause
