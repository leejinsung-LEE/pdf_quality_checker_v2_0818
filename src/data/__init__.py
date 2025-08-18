# src/data/__init__.py
"""
데이터 관리 모듈

PDF 처리 이력과 관련 데이터를 관리합니다.
"""

from .data_manager import DataManager, get_data_manager
from .models import HistoryEntry, ProcessingStatus
from .backup_manager import BackupManager, get_backup_manager

__all__ = [
    'DataManager',
    'get_data_manager',
    'HistoryEntry',
    'ProcessingStatus',
    'BackupManager',
    'get_backup_manager'
]