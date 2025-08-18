@echo off
REM PDF Quality Checker v2.0 - 빠른 성능 테스트
REM 5분 메모리 테스트 + UI 응답 시간 테스트

echo ========================================
echo   PDF Quality Checker v2.0
echo   빠른 성능 테스트 (약 15분)
echo ========================================
echo.

REM Python 경로 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되지 않았거나 PATH에 없습니다.
    pause
    exit /b 1
)

REM 메모리 테스트 (5분)
echo [1/2] 메모리 누수 테스트 (5분)...
echo ----------------------------------------
python tests\performance\test_memory_leak.py --quick
if errorlevel 1 (
    echo 메모리 테스트 실패
    pause
    exit /b 1
)

echo.
echo [2/2] UI 응답 시간 테스트...
echo ----------------------------------------
python tests\performance\test_ui_response.py
if errorlevel 1 (
    echo UI 테스트 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo   테스트 완료!
echo ========================================
echo.
echo 보고서 위치: docs\reports\
echo.
echo 최신 보고서 확인:
dir docs\reports\*.md /o-d /b | head -2

echo.
pause