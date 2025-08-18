# src/processing/queue_manager/base.py
"""
작업 큐 관리 시스템의 기본 데이터 구조
"""

from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskType(Enum):
    """작업 유형"""
    PROCESS_FILE = "process_file"
    BATCH_PROCESS = "batch_process"
    ANALYZE_ONLY = "analyze_only"
    CHECK_QUALITY = "check_quality"
    GENERATE_REPORT = "generate_report"
    AUTO_FIX = "auto_fix"


class TaskPriority(Enum):
    """작업 우선순위"""
    URGENT = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    
    def __lt__(self, other):
        return self.value < other.value


@dataclass
class Task:
    """작업 정의"""
    task_id: str
    task_type: TaskType
    priority: TaskPriority
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    callback: Optional[Callable] = None
    
    def __lt__(self, other):
        """우선순위 비교"""
        return self.priority < other.priority


@dataclass
class TaskResult:
    """작업 결과"""
    task_id: str
    task_type: TaskType
    success: bool
    result: Any
    error: Optional[str] = None
    processing_time: float = 0.0
    completed_at: datetime = field(default_factory=datetime.now)