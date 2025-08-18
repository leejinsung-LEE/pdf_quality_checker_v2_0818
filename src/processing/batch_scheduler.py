# -*- coding: utf-8 -*-
"""
배치 스케줄러 호환성 래퍼

기존 코드와의 호환성을 위한 래퍼 모듈
모든 기능은 batch_scheduler 패키지로 위임됩니다.
"""

# 모듈화된 패키지에서 모든 것을 임포트
from src.processing.batch_scheduler import (
    BatchScheduler,
    ScheduleTask,
    ScheduleFrequency,
    ScheduleStatus,
    get_batch_scheduler
)

# 기존 코드 호환성을 위한 re-export
__all__ = [
    'BatchScheduler',
    'ScheduleTask',
    'ScheduleFrequency',
    'ScheduleStatus',
    'get_batch_scheduler'
]