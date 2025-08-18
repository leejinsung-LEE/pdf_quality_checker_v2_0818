# -*- coding: utf-8 -*-
"""
작업 이력 관리 시스템 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 history_manager/ 디렉토리의 모듈로 분리되었습니다.
"""

# 모든 공개 API를 재노출
from .history_manager import (
    ProcessStatus,
    ProcessHistory,
    HistoryManager,
    get_history_manager
)

# 추가 모듈 접근 (필요시)
from .history_manager.database import DatabaseManager
from .history_manager.crud_operations import CRUDOperations
from .history_manager.search_engine import SearchEngine
from .history_manager.statistics import StatisticsManager
from .history_manager.export_handler import ExportHandler

__all__ = [
    'ProcessStatus',
    'ProcessHistory',
    'HistoryManager',
    'get_history_manager',
    # 추가 모듈 (선택적)
    'DatabaseManager',
    'CRUDOperations',
    'SearchEngine',
    'StatisticsManager',
    'ExportHandler',
]

# 하위 호환성 메시지
def __getattr__(name):
    """동적 속성 접근 처리"""
    import warnings
    warnings.warn(
        f"'{name}'에 대한 직접 접근은 deprecated 되었습니다. "
        f"'from data.history_manager import {name}'를 사용하세요.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 모듈에서 속성 찾기
    from . import history_manager
    if hasattr(history_manager, name):
        return getattr(history_manager, name)
    
    raise AttributeError(f"module 'data.history_manager' has no attribute '{name}'")