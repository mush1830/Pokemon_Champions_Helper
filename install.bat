@echo off
chcp 65001 >nul
title PokeOCR 설치
echo.
echo ======================================
echo   PokeOCR 설치 프로그램
echo ======================================
echo.

:: ── 1. Python 확인 ──────────────────────
echo [1/4] Python 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo       Python이 없습니다. 설치 중... (winget 사용)
        winget install -e --id Python.Python.3.11 ^
            --accept-source-agreements ^
            --accept-package-agreements ^
            --silent
        if %errorlevel% neq 0 (
            echo.
            echo [오류] 자동 설치 실패.
            echo       https://www.python.org/downloads/ 에서 직접 설치 후
            echo       이 파일을 다시 실행하세요.
            pause
            exit /b 1
        )
        echo       Python 설치 완료.
        echo.
        echo [중요] 이 창을 닫고 install.bat 을 다시 실행하세요.
        echo        (PATH 적용을 위해 재실행 필요)
        pause
        exit /b 0
    ) else (
        set PYTHON=py
    )
) else (
    set PYTHON=python
)
echo       완료.

:: ── 2. pip 업그레이드 ───────────────────
echo [2/4] pip 업그레이드 중...
%PYTHON% -m pip install --upgrade pip --quiet
echo       완료.

:: ── 3. PyTorch (CUDA 12.8) ──────────────
echo [3/4] PyTorch CUDA 설치 중... (최대 10분 소요)
%PYTHON% -m pip install torch ^
    --index-url https://download.pytorch.org/whl/cu128 ^
    --quiet
if %errorlevel% neq 0 (
    echo [경고] CUDA PyTorch 설치 실패. CPU 버전으로 대체합니다.
    %PYTHON% -m pip install torch --quiet
)
echo       완료.

:: ── 4. 나머지 패키지 ────────────────────
echo [4/4] 나머지 패키지 설치 중...
%PYTHON% -m pip install ^
    "chandra-ocr[hf]" ^
    mss ^
    Pillow ^
    opencv-python ^
    rapidfuzz ^
    keyboard ^
    requests ^
    beautifulsoup4 ^
    selenium ^
    webdriver-manager ^
    --quiet
echo       완료.

:: ── 완료 ────────────────────────────────
echo.
echo ======================================
echo   설치 완료!
echo   run.bat 을 더블클릭하면 실행됩니다.
echo   (첫 실행시 AI 모델 다운로드 - 약 5GB)
echo ======================================
echo.
pause
