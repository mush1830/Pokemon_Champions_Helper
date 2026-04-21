@echo off
chcp 65001 >nul
title PokeOCR - ROI 설정
cd /d "%~dp0"

echo =============================================
echo   ROI 설정 시작
echo.
echo   OBS에서 전투 화면이 보이는지 확인하세요.
echo   실행 후 5초 안에 OBS 화면으로 전환하세요.
echo =============================================
echo.
pause

python scripts/roi_selector.py 2>nul || py scripts/roi_selector.py

if %errorlevel% == 0 (
    echo. > .roi_configured
    echo.
    echo ROI 설정이 저장되었습니다.
    echo run.bat 을 실행하면 프로그램이 시작됩니다.
) else (
    echo.
    echo [오류] ROI 설정 중 문제가 발생했습니다. 다시 시도하세요.
)
pause
