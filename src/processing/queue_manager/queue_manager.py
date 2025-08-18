# src/processing/queue_manager/queue_manager.py
"""
메인 큐 관리자 클래스
"""

import queue
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import logging

from .base import TaskType, TaskPriority, Task, TaskResult
from .task_manager import TaskManager
from .task_tracker import TaskTracker
from .statistics import QueueStatistics
from .worker_manager import WorkerManager


class QueueManager:
    """
    작업 큐 관리자
    
    UI와 백그라운드 처리 시스템 간의 작업을 관리합니다.
    """
    
    def __init__(self, 
                 logger: Optional[logging.Logger] = None,
                 auto_start_workers: bool = True,
                 num_workers: Optional[int] = None):
        """
        큐 관리자 초기화
        
        Args:
            logger: 로거
            auto_start_workers: 워커 자동 시작 여부
            num_workers: 워커 수 (None이면 CPU 코어 기반 자동 설정)
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 큐
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.result_queue: queue.Queue = queue.Queue()
        
        # 작업 추적
        self.pending_tasks: Dict[str, Task] = {}
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        
        # 스레드 안전성
        self.lock = threading.RLock()
        
        # 모듈 초기화
        self.task_manager = TaskManager(
            self.task_queue,
            self.pending_tasks,
            self.active_tasks,
            self.completed_tasks,
            self.lock,
            self.logger
        )
        
        self.task_tracker = TaskTracker(
            self.task_queue,
            self.result_queue,
            self.pending_tasks,
            self.active_tasks,
            self.completed_tasks,
            self.lock,
            self.logger
        )
        
        self.statistics_manager = QueueStatistics(
            self.pending_tasks,
            self.active_tasks,
            self.completed_tasks,
            self.lock,
            self.logger
        )
        
        self.worker_manager = WorkerManager(
            self,
            num_workers,
            auto_start_workers,
            self.logger
        )
        
        # 통계 동기화
        self.total_tasks = 0
        self.completed_count = 0
        self.error_count = 0
        
        # 콜백 (호환성용)
        self.on_task_complete: Optional[Callable] = None
        self.on_task_error: Optional[Callable] = None
        
        # 호환성을 위한 속성
        self.num_workers = self.worker_manager.num_workers  # 실제 설정된 워커 수
        self.worker_pool = None  # worker_manager가 관리
    
    # === TaskManager 메서드 위임 ===
    
    def add_task(self, 
                task_type: TaskType,
                data: Dict[str, Any],
                priority: TaskPriority = TaskPriority.NORMAL,
                callback: Optional[Callable] = None) -> str:
        """작업 추가"""
        task_id = self.task_manager.add_task(task_type, data, priority, callback)
        self.statistics_manager.update_total_tasks()
        self.total_tasks += 1
        return task_id
    
    def add_file_processing_task(self,
                               file_path: Path,
                               profile: str = "default",
                               auto_fix: bool = False,
                               priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """파일 처리 작업 추가"""
        task_id = self.task_manager.add_file_processing_task(
            file_path, profile, auto_fix, priority
        )
        self.statistics_manager.update_total_tasks()
        self.total_tasks += 1
        return task_id
    
    def add_batch_processing_task(self,
                                file_paths: List[Path],
                                profile: str = "default",
                                priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """배치 처리 작업 추가"""
        task_id = self.task_manager.add_batch_processing_task(
            file_paths, profile, priority
        )
        self.statistics_manager.update_total_tasks()
        self.total_tasks += 1
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        success = self.task_manager.cancel_task(task_id)
        if success:
            # 취소도 완료로 간주
            self.complete_task(
                task_id,
                success=False,
                result=None,
                error="작업이 취소되었습니다"
            )
        return success
    
    # === TaskTracker 메서드 위임 ===
    
    def get_next_task(self, timeout: Optional[float] = None) -> Optional[Task]:
        """다음 작업 가져오기"""
        return self.task_tracker.get_next_task(timeout)
    
    def complete_task(self, 
                     task_id: str,
                     success: bool,
                     result: Any,
                     error: Optional[str] = None,
                     processing_time: float = 0.0):
        """작업 완료 처리"""
        self.task_tracker.complete_task(
            task_id, success, result, error, processing_time
        )
        
        # 통계 동기화
        self.statistics_manager.update_completed(success)
        self.completed_count = self.task_tracker.completed_count
        self.error_count = self.task_tracker.error_count
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """작업 상태 조회"""
        return self.task_tracker.get_task_status(task_id)
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """작업 결과 조회"""
        return self.task_tracker.get_task_result(task_id)
    
    def wait_for_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """작업 결과 대기"""
        return self.task_tracker.wait_for_result(task_id, timeout)
    
    def set_callbacks(self,
                     on_task_complete: Optional[Callable] = None,
                     on_task_error: Optional[Callable] = None):
        """콜백 설정 (TaskTracker로 위임)"""
        self.on_task_complete = on_task_complete
        self.on_task_error = on_task_error
        self.task_tracker.set_callbacks(on_task_complete, on_task_error)
    
    # === Statistics 메서드 위임 ===
    
    def get_pending_count(self) -> int:
        """대기 중인 작업 수"""
        return self.statistics_manager.get_pending_count()
    
    def get_active_count(self) -> int:
        """처리 중인 작업 수"""
        return self.statistics_manager.get_active_count()
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보"""
        return self.statistics_manager.get_statistics()
    
    def clear_completed(self, older_than: Optional[datetime] = None):
        """완료된 작업 정리"""
        self.statistics_manager.clear_completed(older_than)
    
    # === WorkerManager 메서드 위임 ===
    
    def start_workers(self):
        """워커 풀 시작"""
        self.worker_manager.start_workers()
        self.worker_pool = self.worker_manager.worker_pool  # 호환성
    
    def stop_workers(self, timeout: float = 10.0):
        """워커 풀 중지"""
        self.worker_manager.stop_workers(timeout)
        self.worker_pool = None  # 호환성
    
    def get_worker_status(self) -> Optional[Dict[str, Any]]:
        """워커 풀 상태 조회"""
        return self.worker_manager.get_worker_status()
    
    # === 호환성을 위한 private 메서드 ===
    
    def _generate_task_id(self, task_type: TaskType) -> str:
        """작업 ID 생성 (호환성용)"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        return f"{task_type.value}_{timestamp}"