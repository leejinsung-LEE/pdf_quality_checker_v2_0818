@echo off
REM PDF Quality Checker v2.0 - 전체 성능 테스트
REM 1시간 메모리 테스트 + UI 응답 시간 테스트

echo ========================================
echo   PDF Quality Checker v2.0
echo   전체 성능 테스트 (약 70분)
echo ========================================
echo.
echo 주의: 이 테스트는 약 1시간 10분이 소요됩니다.
echo.

set /p confirm=계속하시겠습니까? (Y/N): 
if /i not "%confirm%"=="Y" (
    echo 테스트를 취소합니다.
    pause
    exit /b 0
)

REM Python 경로 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되지 않았거나 PATH에 없습니다.
    pause
    exit /b 1
)

REM 시작 시간 기록
echo.
echo 테스트 시작: %date% %time%
echo.

REM 메모리 테스트 (60분)
echo [1/2] 메모리 누수 테스트 (60분)...
echo ----------------------------------------
echo 테스트 중... (Ctrl+C로 중단 가능)
python tests\performance\test_memory_leak.py --duration 60
if errorlevel 1 (
    echo 메모리 테스트 실패 또는 중단됨
    set /p continue=UI 테스트를 계속하시겠습니까? (Y/N): 
    if /i not "%continue%"=="Y" (
        pause
        exit /b 1
    )
)

echo.
echo [2/2] UI 응답 시간 테스트...
echo ----------------------------------------
python tests\performance\test_ui_response.py
if errorlevel 1 (
    echo UI 테스트 실패
)

REM 종료 시간 기록
echo.
echo 테스트 종료: %date% %time%
echo.

echo ========================================
echo   테스트 완료!
echo ========================================
echo.
echo 보고서 위치: docs\reports\
echo.

REM 보고서 열기 옵션
set /p open=보고서 폴더를 열시겠습니까? (Y/N): 
if /i "%open%"=="Y" (
    explorer docs\reports
)

echo.
pause