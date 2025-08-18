# src/processing/folder_watcher.py
"""
폴더 감시 시스템 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 folder_watcher 모듈에 있습니다.
"""

# 모든 클래스와 함수를 모듈에서 가져오기
from .folder_watcher.base import FolderConfig
from .folder_watcher.event_handler import PDFEventHandler
from .folder_watcher.watcher import FolderWatcher

# watchdog 가용성 체크 (기존 코드 호환성)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    Observer = None
    FileSystemEventHandler = object

# 기존 코드와의 호환성을 위한 익스포트
__all__ = [
    'FolderConfig',
    'PDFEventHandler', 
    'FolderWatcher',
    'HAS_WATCHDOG'
]