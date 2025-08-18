# -*- coding: utf-8 -*-
"""
배치 스케줄러 모듈

특정 시간에 자동으로 배치 작업을 실행하는 스케줄링 시스템
"""

from functools import lru_cache

from .models import ScheduleTask, ScheduleFrequency, ScheduleStatus
from .manager import BatchScheduler
from .scheduler import SchedulerEngine
from .executor import TaskExecutor

# 공개 API
__all__ = [
    'BatchScheduler',
    'ScheduleTask',
    'ScheduleFrequency',
    'ScheduleStatus',
    'get_batch_scheduler',
    'reset_scheduler',
    'SchedulerEngine',
    'TaskExecutor'
]


@lru_cache(maxsize=1)
def get_batch_scheduler() -> BatchScheduler:
    """
    배치 스케줄러 싱글톤 인스턴스 반환 (스레드 안전)
    
    Returns:
        BatchScheduler 싱글톤 인스턴스
    """
    return BatchScheduler()


def reset_scheduler():
    """
    스케줄러 인스턴스 초기화 (테스트용)
    
    주의: 이 함수는 테스트 목적으로만 사용해야 합니다.
    """
    # 현재 인스턴스가 있다면 종료
    try:
        scheduler = get_batch_scheduler()
        if scheduler.is_running:
            scheduler.stop()
    except:
        pass
    
    # 캐시 초기화
    get_batch_scheduler.cache_clear()