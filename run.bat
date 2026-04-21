@echo off
chcp 65001 >nul
title PokeOCR
cd /d "%~dp0"

:: Python 명령어 결정
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python이 설치되지 않았습니다. install.bat 을 먼저 실행하세요.
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

:: 포켓몬 데이터가 없으면 자동 수집
if not exist "data\pokemon_data.json" (
    echo 포켓몬 데이터가 없습니다. 수집을 시작합니다...
    echo 완료까지 수분이 걸릴 수 있습니다.
    echo.
    %PYTHON% scripts/fetch_pokeapi.py
)

:: ROI 미설정 안내
if not exist ".roi_configured" (
    echo =============================================
    echo   [안내] 화면 영역(ROI) 설정이 필요합니다.
    echo.
    echo   OBS에서 전투 화면을 띄운 후,
    echo   이 창을 닫고 roi_setup.bat 을 실행하세요.
    echo.
    echo   이미 설정했다면 아무 키나 눌러 계속하세요.
    echo =============================================
    pause
)

%PYTHON% main.py
pause
