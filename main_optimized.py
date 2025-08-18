#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Quality Checker v2.0 - 최적화 버전

PDF 파일의 인쇄 품질을 자동으로 검사하고 문제점을 수정하는 프로그램
시작 속도 최적화 버전

Author: Your Name
Version: 2.0.1
"""

import sys
import os
import io
import locale
import atexit
import threading
import asyncio
from pathlib import Path
import logging
from datetime import datetime
import time

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
    except:
        pass

# 프로젝트 루트를 Python 경로에 추가
if getattr(sys, 'frozen', False):
    # 실행 파일로 패키징된 경우
    application_path = Path(sys.executable).parent
else:
    # 스크립트로 실행하는 경우
    application_path = Path(__file__).parent

sys.path.insert(0, str(application_path))

# 필수 패키지 확인 (빠른 import)
try:
    import customtkinter
    import tkinterdnd2
    # PDF 관련 라이브러리는 나중에 필요할 때 지연 로딩
except ImportError as e:
    print(f"필수 패키지가 설치되지 않았습니다: {e}")
    print("\n다음 명령으로 설치하세요:")
    print("pip install -r requirements.txt")
    sys.exit(1)


class LazyQueueManager:
    """지연 초기화되는 큐 관리자"""
    _instance = None
    _queue_manager = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """필요할 때만 큐 관리자 초기화"""
        if cls._queue_manager is None:
            with cls._lock:
                if cls._queue_manager is None:
                    from src.processing import get_queue_manager
                    cls._queue_manager = get_queue_manager()
                    # 워커는 첫 작업 시 시작
                    cls._queue_manager.start_workers()
        return cls._queue_manager


def check_requirements_async():
    """필수 요구사항 비동기 확인"""
    def check_in_background():
        try:
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
            
            # 외부 도구 확인 (백그라운드)
            if '--fast' not in sys.argv and '--no-check' not in sys.argv:
                from src.external import get_tool_manager
                tool_manager = get_tool_manager()
                
                # 상태를 로그에만 기록
                status = tool_manager.get_status_report()
                logger = logging.getLogger(__name__)
                
                for tool_name, info in status.items():
                    if info['available']:
                        logger.info(f"[OK] {tool_name}: {info['path']}")
                        if info.get('version'):
                            logger.info(f"  Version: {info['version']}")
                    else:
                        logger.info(f"[NOT FOUND] {tool_name}: not found")
                        
        except Exception as e:
            logging.error(f"백그라운드 체크 오류: {e}")
    
    # 백그라운드 스레드에서 실행
    thread = threading.Thread(target=check_in_background, daemon=True)
    thread.start()
    return thread


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
        queue_manager = LazyQueueManager._queue_manager
        if queue_manager:
            queue_manager.stop_workers(timeout=3.0)
    except:
        pass


def main():
    """최적화된 메인 함수"""
    start_time = time.time()
    
    # 빠른 시작 옵션 확인
    fast_mode = '--fast' in sys.argv or '--optimize' in sys.argv
    
    if fast_mode:
        print("""
=========================================
     PDF Quality Checker v2.0
     [⚡ OPTIMIZED START MODE]
========================================= 
""")
    else:
        print("""
=========================================
     PDF Quality Checker v2.0
     Print Quality Auto Checker
========================================= 
""")
    
    # 로깅 설정 (빠른 설정)
    from src.utils.logger import setup_logger
    logger = setup_logger(
        log_level=logging.INFO,
        log_file=Path("logs") / f"app_{datetime.now():%Y%m%d}.log"
    )
    
    logger.info("PDF Quality Checker v2.0 started")
    
    # 전역 예외 처리기
    setup_exception_handler()
    
    # 종료 시 정리
    atexit.register(cleanup_resources)
    
    # 백그라운드에서 요구사항 확인 시작
    bg_check_thread = check_requirements_async()
    
    # UI 즉시 표시 (필수 모듈만 임포트)
    from src.ui.windows import MainWindow
    
    # 애플리케이션 시작
    app = MainWindow()
    
    # 시작 시간 로깅
    startup_time = time.time() - start_time
    logger.info(f"시작 시간: {startup_time:.2f}초")
    
    # 백그라운드 체크가 완료되지 않았다면 UI에 표시
    if bg_check_thread.is_alive():
        app.show_status_message("외부 도구 확인 중...", duration=2000)
    
    # 메인 루프 실행
    try:
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("사용자가 프로그램을 중단했습니다")
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류: {e}")
    finally:
        cleanup_resources()
    
    logger.info("PDF Quality Checker v2.0 종료")


if __name__ == "__main__":
    # 테스트 모드 확인
    if '--test' in sys.argv:
        # 테스트 모드에서는 즉시 종료
        print("테스트 모드: 시작 성공")
        from src.utils.alarm_manager import AlarmManager
        alarm = AlarmManager()
        if alarm.test_notification():
            print("알림 시스템 테스트 성공")
        sys.exit(0)
    
    main()