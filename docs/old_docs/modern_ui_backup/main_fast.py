#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Quality Checker v2.0 - 빠른 실행 버전

외부 도구 확인을 건너뛰고 빠르게 실행하는 버전
"""

import sys
import os
import io
import locale
from pathlib import Path
import logging
from datetime import datetime

# UTF-8 인코딩 강제 설정 (Windows 호환)
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
else:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        pass

# 프로젝트 루트를 Python 경로에 추가
if getattr(sys, 'frozen', False):
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

sys.path.insert(0, str(application_path))

# 필수 패키지 확인
try:
    import customtkinter
    import tkinterdnd2
    import pikepdf
    import fitz
    from PIL import Image
except ImportError as e:
    print(f"필수 패키지가 설치되지 않았습니다: {e}")
    print("\n다음 명령으로 설치하세요:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# 애플리케이션 import
from src.config import Config
from src.utils.logger import setup_logger
from src.config.ui_config import get_ui_config_manager
from src.ui.selector import show_ui_selector


def quick_check_requirements():
    """필수 디렉토리만 빠르게 생성 (도구 확인 건너뜀)"""
    directories = [
        Path("data"),
        Path("data/profiles"),
        Path("data/history"),
        Path("logs"),
        Path("reports"),
        Path("output"),
        Path("completed")
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
    
    print("Quick start mode - skipping external tools check")


def setup_exception_handler():
    """전역 예외 처리기 설정"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logging.critical(
            "처리되지 않은 예외",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception


def main():
    """메인 함수"""
    print("""
=========================================
     PDF Quality Checker v2.0
     Print Quality Auto Checker
     [FAST MODE]
========================================= 
""")
    
    # 로깅 설정
    log_file = Path("logs") / f"pdf_checker_{datetime.now().strftime('%Y%m%d')}.log"
    logger = setup_logger(log_file)
    logger.info("PDF Quality Checker v2.0 started (FAST MODE)")
    
    # 빠른 요구사항 확인 (외부 도구 체크 생략)
    quick_check_requirements()
    
    # 예외 처리기 설정
    setup_exception_handler()
    
    # UI 모드 결정
    ui_config = get_ui_config_manager()
    
    # UI 선택 다이얼로그 표시 여부 확인
    if ui_config.should_show_selector() or '--select' in sys.argv:
        ui_mode = show_ui_selector()
        if not ui_mode:
            print("\nUI mode selection cancelled.")
            sys.exit(0)
    else:
        ui_mode = ui_config.get_ui_mode()
    
    print(f"\nStarting with {ui_mode.upper()} UI mode...")
    logger.info(f"UI mode selected: {ui_mode}")
    
    # UI 모드별 실행
    app = None
    try:
        if ui_mode == "modern":
            try:
                from src.ui.modern import ModernApp
                print("Loading Modern UI...")
                app = ModernApp()
                app.run()
            except ImportError as e:
                logger.warning(f"Modern UI not available: {e}")
                if ui_config.config.auto_fallback:
                    print("Modern UI not available, falling back to Classic UI...")
                    ui_mode = "classic"
                else:
                    print("Modern UI is not installed. Please install with: pip install flet")
                    sys.exit(1)
        
        if ui_mode == "classic" or app is None:
            from src.ui.windows import MainWindow
            print("Loading Classic UI...")
            app = MainWindow()
            app.mainloop()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\nError occurred: {e}")
        print("Please check the log file for details.")
        
        if ui_config.config.auto_fallback and ui_mode == "modern":
            print("\nAttempting to fallback to Classic UI...")
            try:
                from src.ui.windows import MainWindow
                app = MainWindow()
                app.mainloop()
            except Exception as fallback_error:
                logger.error(f"Fallback failed: {fallback_error}")
                sys.exit(1)
        else:
            sys.exit(1)
    
    finally:
        logger.info("PDF Quality Checker terminated")
        print("\nProgram terminated.")


if __name__ == "__main__":
    main()