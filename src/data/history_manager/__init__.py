# -*- coding: utf-8 -*-
"""
작업 이력 관리 시스템 모듈

이 모듈은 PDF 처리 이력을 SQLite 데이터베이스에 저장하고 관리합니다:
- CRUD 작업
- 검색 및 필터링
- 통계 계산
- 데이터 내보내기
- 유지보수 작업
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .models import ProcessStatus, ProcessHistory
from .database import DatabaseManager
from .crud_operations import CRUDOperations
from .search_engine import SearchEngine
from .statistics import StatisticsManager
from .export_handler import ExportHandler


class HistoryManager:
    """작업 이력 관리자 - 통합 인터페이스"""
    
    def __init__(self, db_path: Optional[Path] = None, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 핵심 구성요소 초기화
        self.db_manager = DatabaseManager(db_path, self.logger)
        self.crud = CRUDOperations(self.db_manager, self.logger)
        self.search = SearchEngine(self.db_manager, self.logger)
        self.statistics = StatisticsManager(self.db_manager, self.logger)
        self.export = ExportHandler(self.db_manager, self.search, self.logger)
        
        # 기존 속성 유지 (호환성)
        self.db_path = self.db_manager.db_path
    
    # CRUD 작업 위임
    def add_history(self, history: ProcessHistory) -> int:
        """처리 이력 추가"""
        history_id = self.crud.add_history(history)
        # 통계 업데이트
        self.statistics.update_daily_statistics(history)
        return history_id
    
    def update_history(self, history_id: int, **kwargs) -> bool:
        """처리 이력 업데이트"""
        return self.crud.update_history(history_id, **kwargs)
    
    def get_history(self, history_id: int) -> Optional[ProcessHistory]:
        """특정 이력 조회"""
        return self.crud.get_history(history_id)
    
    def get_recent_history(self, limit: int = 100, 
                          status: Optional[str] = None,
                          process_type: Optional[str] = None) -> List[ProcessHistory]:
        """최근 이력 조회"""
        return self.crud.get_recent_history(limit, status, process_type)
    
    # 검색 작업 위임
    def search_history(self, 
                       file_name: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       min_quality_score: Optional[float] = None,
                       max_quality_score: Optional[float] = None) -> List[ProcessHistory]:
        """이력 검색"""
        return self.search.search_history(
            file_name=file_name,
            start_date=start_date,
            end_date=end_date,
            min_quality_score=min_quality_score,
            max_quality_score=max_quality_score
        )
    
    # 통계 작업 위임
    def get_statistics(self, 
                       period: str = "day",
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """통계 조회"""
        return self.statistics.get_statistics(period, start_date, end_date)
    
    def _update_daily_statistics(self, cursor, history: ProcessHistory):
        """일일 통계 업데이트 (내부 호환성)"""
        self.statistics.update_daily_statistics(history)
    
    # 내보내기 및 유지보수 작업 위임
    def export_history(self, output_path: Path, 
                       format: str = "csv",
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> bool:
        """이력 내보내기"""
        return self.export.export_history(output_path, format, start_date, end_date)
    
    def cleanup_old_history(self, days: int = 90) -> int:
        """오래된 이력 정리"""
        return self.export.cleanup_old_history(days)


# 공개 API
__all__ = [
    'ProcessStatus',
    'ProcessHistory',
    'HistoryManager',
    'DatabaseManager',
    'CRUDOperations',
    'SearchEngine',
    'StatisticsManager',
    'ExportHandler',
    'get_history_manager',  # 싱글톤 함수
]


@lru_cache(maxsize=1)
def get_history_manager() -> HistoryManager:
    """
    히스토리 매니저 싱글톤 인스턴스 반환 (스레드 안전)
    
    LRU 캐시를 사용하여 싱글톤 패턴을 구현합니다.
    Python 내장 기능으로 스레드 안전성이 보장됩니다.
    
    Returns:
        HistoryManager: 싱글톤 인스턴스
        
    Example:
        >>> manager = get_history_manager()
        >>> history = ProcessHistory(file_name="test.pdf", ...)
        >>> history_id = manager.add_history(history)
    """
    return HistoryManager()