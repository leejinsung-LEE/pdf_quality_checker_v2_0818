# -*- coding: utf-8 -*-
"""
백업 및 롤백 관리 시스템 - 호환성 래퍼

이 파일은 모듈화된 backup_manager 패키지에 대한 호환성 래퍼입니다.
기존 코드와의 호환성을 유지하면서 새로운 모듈 구조를 사용합니다.
"""

# 모듈화된 컴포넌트 임포트
from .backup_manager import (
    BackupManager,
    BackupInfo,
    get_backup_manager,
    reset_backup_manager
)

# 하위 호환성을 위한 추가 임포트
import threading

# 싱글톤 관련 변수 (하위 호환성)
_backup_manager_instance = None
_backup_manager_lock = threading.Lock()

# 공개 API
__all__ = [
    'BackupManager',
    'BackupInfo',
    'get_backup_manager'
]

# 하위 호환성 유지를 위한 메시지
import logging
logger = logging.getLogger(__name__)
logger.debug("backup_manager.py가 모듈화되었습니다. backup_manager/ 패키지를 사용합니다.")