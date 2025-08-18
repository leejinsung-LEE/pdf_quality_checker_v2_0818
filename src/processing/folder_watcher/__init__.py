# src/processing/folder_watcher/__init__.py
"""
폴더 감시 시스템 모듈

기존 코드와의 호환성을 위한 래퍼를 제공합니다.
"""

from .base import FolderConfig
from .event_handler import PDFEventHandler
from .config_manager import ConfigManager
from .monitor import FolderMonitor
from .watcher import FolderWatcher

# watchdog 가용성 체크 (기존 코드 호환성)
try:
    from watchdog.observers import Observer
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    Observer = None

__all__ = [
    'FolderConfig',
    'PDFEventHandler',
    'ConfigManager',
    'FolderMonitor',
    'FolderWatcher',
    'HAS_WATCHDOG'
]