# src/processing/queue_manager.py
"""
작업 큐 관리자 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 queue_manager 모듈에 있습니다.
"""

from typing import Optional

# 모든 클래스와 함수를 모듈에서 가져오기
from .queue_manager.base import TaskType, TaskPriority, Task, TaskResult
from .queue_manager.queue_manager import QueueManager

# 전역 큐 관리자 인스턴스 - 모듈에서 가져오기
from .queue_manager import get_queue_manager


# 기존 코드와의 호환성을 위한 익스포트
__all__ = [
    'TaskType',
    'TaskPriority',
    'Task',
    'TaskResult',
    'QueueManager',
    'get_queue_manager'
]