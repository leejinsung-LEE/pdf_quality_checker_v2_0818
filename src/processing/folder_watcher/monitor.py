# src/processing/folder_watcher/monitor.py
"""
폴더 감시 모니터링 로직
"""

import time
import threading
import logging
from pathlib import Path
from typing import Dict, Set, Callable, Optional
from datetime import datetime

try:
    from watchdog.observers import Observer
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    Observer = None

from .base import FolderConfig
from .event_handler import PDFEventHandler


class FolderMonitor:
    """폴더 감시 모니터"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        모니터 초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        self.is_watching = False
        self.observers: Dict[str, Observer] = {}
        
        # 폴링 모드 설정
        self.use_polling = not HAS_WATCHDOG
        self.polling_thread: Optional[threading.Thread] = None
        self.polling_interval = 2.0  # 초
        
        # 처리된 파일 추적 (폴링 모드용)
        self.processed_files: Dict[str, Set[Path]] = {}
    
    def start_watching(self, folder_configs: Dict[str, FolderConfig], 
                      callback: Callable) -> bool:
        """
        모든 폴더 감시 시작
        
        Args:
            folder_configs: 폴더 설정들
            callback: PDF 발견 시 호출할 콜백
            
        Returns:
            시작 성공 여부
        """
        if self.is_watching:
            self.logger.warning("이미 감시 중입니다")
            return False
        
        self.is_watching = True
        
        # 폴링 모드 또는 watchdog 모드
        if self.use_polling:
            self._start_polling(folder_configs, callback)
        else:
            for config in folder_configs.values():
                if config.enabled:
                    self._start_watching_folder(config, callback)
        
        active_count = sum(1 for c in folder_configs.values() if c.enabled)
        self.logger.info(f"{active_count}개 폴더 감시 시작 (모드: {'폴링' if self.use_polling else 'watchdog'})")
        return True
    
    def stop_watching(self):
        """모든 폴더 감시 중지"""
        if not self.is_watching:
            return
        
        self.is_watching = False
        
        # 폴링 스레드 중지
        if self.polling_thread:
            self.polling_thread.join(timeout=5)
            self.polling_thread = None
        
        # Observer 중지
        for observer in self.observers.values():
            observer.stop()
            observer.join()
        self.observers.clear()
        
        self.logger.info("폴더 감시 중지됨")
    
    def _start_watching_folder(self, config: FolderConfig, callback: Callable):
        """개별 폴더 감시 시작 (watchdog)"""
        if self.use_polling or not config.enabled:
            return
        
        path_str = str(config.path)
        
        # 이벤트 핸들러 생성
        event_handler = PDFEventHandler(config, callback)
        
        # Observer 생성
        observer = Observer()
        observer.schedule(
            event_handler, 
            path_str, 
            recursive=config.recursive
        )
        observer.start()
        
        self.observers[path_str] = observer
        self.logger.debug(f"폴더 감시 시작: {config.path}")
    
    def _start_polling(self, folder_configs: Dict[str, FolderConfig], 
                      callback: Callable):
        """폴링 모드 시작"""
        # 처리된 파일 초기화
        self.processed_files = {
            str(config.path): set() 
            for config in folder_configs.values()
        }
        
        def polling_loop():
            while self.is_watching:
                for path_str, config in folder_configs.items():
                    if not config.enabled:
                        continue
                    
                    try:
                        # PDF 파일 검색
                        pdf_files = []
                        for pattern in config.file_patterns:
                            if config.recursive:
                                pdf_files.extend(config.path.rglob(pattern))
                            else:
                                pdf_files.extend(config.path.glob(pattern))
                        
                        # 새 파일 찾기
                        new_files = [
                            f for f in pdf_files 
                            if f not in self.processed_files[path_str]
                        ]
                        
                        for pdf_file in new_files:
                            if self._is_file_ready_polling(pdf_file):
                                callback(pdf_file, config)
                                self.processed_files[path_str].add(pdf_file)
                        
                    except Exception as e:
                        self.logger.error(f"폴링 중 오류 ({path_str}): {e}")
                
                # 폴링 간격 대기
                time.sleep(self.polling_interval)
        
        self.polling_thread = threading.Thread(target=polling_loop, daemon=True)
        self.polling_thread.start()
    
    def _is_file_ready_polling(self, file_path: Path) -> bool:
        """파일 준비 상태 확인 (폴링용)"""
        try:
            # 파일 크기 확인
            size1 = file_path.stat().st_size
            if size1 == 0:
                return False
            
            time.sleep(0.5)
            size2 = file_path.stat().st_size
            
            return size1 == size2
        except:
            return False
    
    def add_folder_observer(self, config: FolderConfig, callback: Callable) -> bool:
        """
        단일 폴더에 대한 감시 추가
        
        Args:
            config: 폴더 설정
            callback: PDF 발견 시 호출할 콜백
            
        Returns:
            추가 성공 여부
        """
        if not self.is_watching or self.use_polling:
            return False
        
        path_str = str(config.path)
        
        # 이미 감시 중인지 확인
        if path_str in self.observers:
            return False
        
        self._start_watching_folder(config, callback)
        return True
    
    def remove_folder_observer(self, path: Path) -> bool:
        """
        단일 폴더에 대한 감시 제거
        
        Args:
            path: 폴더 경로
            
        Returns:
            제거 성공 여부
        """
        path_str = str(path.absolute())
        
        if path_str not in self.observers:
            return False
        
        observer = self.observers[path_str]
        observer.stop()
        observer.join()
        del self.observers[path_str]
        
        return True
    
    def get_status(self) -> Dict[str, any]:
        """감시 상태 조회"""
        return {
            'is_watching': self.is_watching,
            'mode': 'polling' if self.use_polling else 'watchdog',
            'active_observers': len(self.observers),
            'polling_interval': self.polling_interval if self.use_polling else None
        }