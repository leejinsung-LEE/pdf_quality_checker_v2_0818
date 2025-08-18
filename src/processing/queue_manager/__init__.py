# src/processing/queue_manager/__init__.py
"""
작업 큐 관리 시스템 모듈

기존 코드와의 호환성을 위한 래퍼를 제공합니다.
"""

from typing import Optional

from .base import TaskType, TaskPriority, Task, TaskResult
from .task_manager import TaskManager
from .task_tracker import TaskTracker
from .statistics import QueueStatistics
from .worker_manager import WorkerManager
from .queue_manager import QueueManager

# 전역 큐 관리자 인스턴스
from functools import lru_cache


@lru_cache(maxsize=1)
def get_queue_manager() -> QueueManager:
    """전역 큐 관리자 인스턴스 반환 (스레드 안전)
    
    LRU 캐시를 사용하여 싱글톤 패턴을 구현합니다.
    Python 내장 기능으로 스레드 안전성이 보장됩니다.
    
    Returns:
        QueueManager: 싱글톤 인스턴스
    """
    return QueueManager()


__all__ = [
    'TaskType',
    'TaskPriority',
    'Task',
    'TaskResult',
    'TaskManager',
    'TaskTracker',
    'QueueStatistics',
    'WorkerManager',
    'QueueManager',
    'get_queue_manager'
]