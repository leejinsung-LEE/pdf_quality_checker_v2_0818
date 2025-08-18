# src/utils/logger.py
"""
로깅 유틸리티

애플리케이션 전체의 로깅을 관리합니다.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    log_file: Optional[Path] = None,
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    로거 설정
    
    Args:
        log_file: 로그 파일 경로
        log_level: 로그 레벨
        max_bytes: 최대 파일 크기
        backup_count: 백업 파일 개수
        
    Returns:
        logging.Logger: 설정된 로거
    """
    # 루트 로거 가져오기
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 포맷터
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러 (UTF-8 인코딩 설정)
    import sys
    import io
    # Windows 환경에서 UTF-8 출력 강제
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러
    if log_file:
        try:
            # 로그 디렉토리 생성
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 로테이팅 파일 핸들러
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.error(f"로그 파일 설정 실패: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거 가져오기
    
    Args:
        name: 로거 이름 (보통 __name__)
        
    Returns:
        logging.Logger: 로거 인스턴스
    """
    return logging.getLogger(name)