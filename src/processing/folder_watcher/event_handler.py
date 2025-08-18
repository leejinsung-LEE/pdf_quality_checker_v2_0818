# src/processing/folder_watcher/event_handler.py
"""
파일 시스템 이벤트 처리
"""

import time
from pathlib import Path
from typing import Callable, Set
import logging

# watchdog 라이브러리 사용 시도
try:
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    FileSystemEventHandler = object

from .base import FolderConfig


class PDFEventHandler(FileSystemEventHandler):
    """PDF 파일 이벤트 핸들러 (watchdog용)"""
    
    def __init__(self, folder_config: FolderConfig, callback: Callable):
        """
        이벤트 핸들러 초기화
        
        Args:
            folder_config: 폴더 설정
            callback: PDF 발견 시 호출할 콜백
        """
        super().__init__()
        self.folder_config = folder_config
        self.callback = callback
        self.processing_files: Set[str] = set()
        self.logger = logging.getLogger(__name__)
    
    def on_created(self, event):
        """파일 생성 이벤트"""
        if not event.is_directory:
            self._handle_file(event.src_path)
    
    def on_modified(self, event):
        """파일 수정 이벤트"""
        if not event.is_directory:
            self._handle_file(event.src_path)
    
    def _handle_file(self, file_path: str):
        """파일 처리"""
        path = Path(file_path)
        
        # PDF 파일인지 확인
        if not any(path.match(pattern) for pattern in self.folder_config.file_patterns):
            return
        
        # 이미 처리 중인지 확인
        if file_path in self.processing_files:
            return
        
        # 파일이 준비되었는지 확인
        if not self._is_file_ready(path):
            return
        
        # 처리 시작
        self.processing_files.add(file_path)
        try:
            self.callback(path, self.folder_config)
        finally:
            self.processing_files.discard(file_path)
    
    def _is_file_ready(self, file_path: Path) -> bool:
        """파일 준비 상태 확인"""
        try:
            # 파일 크기 확인
            initial_size = file_path.stat().st_size
            if initial_size == 0:
                return False
            
            # 0.5초 대기
            time.sleep(0.5)
            
            # 크기 변화 확인
            final_size = file_path.stat().st_size
            return initial_size == final_size
        except:
            return False