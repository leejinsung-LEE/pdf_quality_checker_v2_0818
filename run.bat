@echo off
echo =========================================
echo   PDF Quality Checker v2.0
echo   Classic UI (CustomTkinter)
echo =========================================
echo.
echo 실행 옵션:
echo   1. 일반 실행 (외부 도구 확인 포함)
echo   2. 빠른 실행 (외부 도구 확인 생략)
echo.
set /p choice="선택 (1 또는 2): "

if "%choice%"=="1" (
    python main.py
) else if "%choice%"=="2" (
    python main.py --fast
) else (
    echo 잘못된 선택입니다.
    pause
    exit /b 1
)

pause