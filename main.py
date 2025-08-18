#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Quality Checker v2.0

PDF 파일의 인쇄 품질을 자동으로 검사하고 문제점을 수정하는 프로그램

Author: Your Name
Version: 2.0.0
"""

import sys
import os
import io
import locale
import atexit
from pathlib import Path
import logging
from datetime import datetime

# UTF-8 인코딩 강제 설정 (Windows 호환)
if sys.platform == 'win32':
    # 콘솔 코드 페이지를 UTF-8로 설정
    os.system('chcp 65001 > nul 2>&1')
    # 환경 변수 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # stdout/stderr를 UTF-8로 재설정
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
else:
    # Unix 계열에서도 UTF-8 확인
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except (locale.Error, OSError):
        # locale 설정 실패는 무시 (시스템에 따라 다를 수 있음)
        pass

# 프로젝트 루트를 Python 경로에 추가
if getattr(sys, 'frozen', False):
    # 실행 파일로 패키징된 경우
    application_path = Path(sys.executable).parent
else:
    # 스크립트로 실행하는 경우
    application_path = Path(__file__).parent

sys.path.insert(0, str(application_path))

# 필수 패키지 확인
try:
    import customtkinter
    import tkinterdnd2
    import pikepdf
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError as e:
    print(f"필수 패키지가 설치되지 않았습니다: {e}")
    print("\n다음 명령으로 설치하세요:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# 애플리케이션 import
from src.ui.windows import MainWindow
from src.config import Config
from src.utils.logger import setup_logger


def check_requirements():
    """필수 요구사항 확인"""
    # 데이터 디렉토리 생성
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
    
    # 빠른 모드가 아닌 경우에만 외부 도구 확인
    if '--fast' not in sys.argv:
        # 외부 도구 확인
        from src.external import get_tool_manager
        tool_manager = get_tool_manager()
        
        print("=== External Tools Status ===")
        status = tool_manager.get_status_report()
        
        for tool_name, info in status.items():
            if info['available']:
                print(f"[OK] {tool_name}: {info['path']}")
                if info.get('version'):
                    print(f"  Version: {info['version']}")
            else:
                print(f"[NOT FOUND] {tool_name}: not found")
        
        print("\nTip: Installing Ghostscript and Poppler tools enables more accurate analysis.")
        print("=" * 40)


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


def cleanup_resources():
    """프로그램 종료 시 리소스 정리"""
    try:
        from src.processing import get_queue_manager
        queue_manager = get_queue_manager()
        if queue_manager:
            # 이미 정리되었는지 확인
            if hasattr(queue_manager, '_workers_stopped'):
                return
            queue_manager.stop_workers(timeout=3.0)
            queue_manager._workers_stopped = True
    except ImportError:
        # 모듈 import 실패는 무시 (아직 로드되지 않은 경우)
        pass
    except Exception as e:
        # 다른 오류는 로깅
        logging.error(f"리소스 정리 중 오류: {e}")


def main():
    """메인 함수"""
    # 빠른 시작 옵션 확인
    fast_mode = '--fast' in sys.argv
    
    if fast_mode:
        print("""
=========================================
     PDF Quality Checker v2.0
     Print Quality Auto Checker
     [FAST MODE - Skipping tool checks]
========================================= 
""")
    else:
        print("""
=========================================
     PDF Quality Checker v2.0
     Print Quality Auto Checker
========================================= 
""")
    
    # 로깅 설정
    log_file = Path("logs") / f"pdf_checker_{datetime.now().strftime('%Y%m%d')}.log"
    logger = setup_logger(log_file)
    logger.info(f"PDF Quality Checker v2.0 started {'(FAST MODE)' if fast_mode else ''}")
    
    # 종료 시 리소스 정리 등록
    atexit.register(cleanup_resources)
    
    # 요구사항 확인
    check_requirements()
    
    # 예외 처리기 설정
    setup_exception_handler()
    
    try:
        # 메인 윈도우 실행
        print("\nStarting application...")
        app = MainWindow()
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\nError occurred: {e}")
        print("Please check the log file for details.")
        sys.exit(1)
    
    finally:
        # cleanup_resources가 이미 atexit로 등록되어 있으므로
        # 여기서는 로깅만 수행
        pass
        
        logger.info("PDF Quality Checker terminated")
        print("\nProgram terminated.")


if __name__ == "__main__":
    main()