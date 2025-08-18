# -*- coding: utf-8 -*-
"""
백업 관리 모듈

PDF 파일의 백업, 롤백, 정리 기능을 제공합니다.
"""

from functools import lru_cache
from typing import Optional

from .manager import BackupManager
from .models import (
    BackupInfo,
    BackupMetadata,
    BackupStatistics,
    RollbackRecord
)
from .storage import BackupStorage
from .compression import BackupCompressor
from .cleanup import BackupCleaner
from .rollback import BackupRollback


@lru_cache(maxsize=1)
def get_backup_manager(**kwargs) -> BackupManager:
    """
    백업 매니저 싱글톤 인스턴스 반환 (스레드 안전)
    
    LRU 캐시를 사용하여 싱글톤 패턴을 구현합니다.
    Python 내장 기능으로 스레드 안전성이 보장됩니다.
    
    Args:
        **kwargs: BackupManager 초기화 매개변수
        
    Returns:
        BackupManager: 백업 매니저 인스턴스
    """
    return BackupManager(**kwargs)


def reset_backup_manager():
    """백업 매니저 인스턴스 리셋 (테스트용)"""
    get_backup_manager.cache_clear()


# 공개 API
__all__ = [
    # 메인 클래스
    'BackupManager',
    'get_backup_manager',
    'reset_backup_manager',
    
    # 모델
    'BackupInfo',
    'BackupMetadata', 
    'BackupStatistics',
    'RollbackRecord',
    
    # 컴포넌트
    'BackupStorage',
    'BackupCompressor',
    'BackupCleaner',
    'BackupRollback'
]