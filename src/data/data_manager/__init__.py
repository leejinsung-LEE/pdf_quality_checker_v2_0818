"""Data manager module - Public API"""

from functools import lru_cache

from .manager import DataManager
from .models import (
    HistoryFilter,
    CacheEntry,
    StatisticsData,
    SettingsSchema
)
from .persistence import PersistenceHandler
from .cache_manager import CacheManager
from .history_handler import HistoryHandler
from .statistics import StatisticsGenerator


@lru_cache(maxsize=1)
def get_data_manager() -> DataManager:
    """데이터 매니저 싱글톤 인스턴스 반환 (스레드 안전)"""
    return DataManager()


def reset_data_manager() -> None:
    """데이터 매니저 인스턴스 리셋 (테스트용)"""
    get_data_manager.cache_clear()


# Public exports
__all__ = [
    'DataManager',
    'get_data_manager',
    'reset_data_manager',
    'HistoryFilter',
    'CacheEntry',
    'StatisticsData',
    'SettingsSchema',
    'PersistenceHandler',
    'CacheManager',
    'HistoryHandler',
    'StatisticsGenerator'
]

# Version info
__version__ = '2.0.0'