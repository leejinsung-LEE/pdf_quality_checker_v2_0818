# src/processing/queue_manager/statistics.py
"""
작업 큐 통계 관리
"""

import threading
from typing import Dict, Optional, Any
from datetime import datetime
import logging

from .base import Task, TaskResult


class QueueStatistics:
    """큐 통계 관리자"""
    
    def __init__(self,
                 pending_tasks: Dict[str, Task],
                 active_tasks: Dict[str, Task],
                 completed_tasks: Dict[str, TaskResult],
                 lock: threading.RLock,
                 logger: Optional[logging.Logger] = None):
        """
        통계 관리자 초기화
        
        Args:
            pending_tasks: 대기 중인 작업
            active_tasks: 처리 중인 작업
            completed_tasks: 완료된 작업
            lock: 스레드 락
            logger: 로거
        """
        self.pending_tasks = pending_tasks
        self.active_tasks = active_tasks
        self.completed_tasks = completed_tasks
        self.lock = lock
        self.logger = logger or logging.getLogger(__name__)
        
        # 통계 카운터
        self.total_tasks = 0
        self.completed_count = 0
        self.error_count = 0
    
    def get_pending_count(self) -> int:
        """대기 중인 작업 수"""
        with self.lock:
            return len(self.pending_tasks)
    
    def get_active_count(self) -> int:
        """처리 중인 작업 수"""
        with self.lock:
            return len(self.active_tasks)
    
    def get_completed_count(self) -> int:
        """완료된 작업 수"""
        with self.lock:
            return self.completed_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보"""
        with self.lock:
            success_count = self.completed_count - self.error_count
            success_rate = 0.0
            
            if self.completed_count > 0:
                success_rate = (success_count / self.completed_count) * 100
            
            return {
                'total_tasks': self.total_tasks,
                'pending': len(self.pending_tasks),
                'active': len(self.active_tasks),
                'completed': self.completed_count,
                'errors': self.error_count,
                'success_rate': success_rate
            }
    
    def clear_completed(self, older_than: Optional[datetime] = None):
        """
        완료된 작업 정리
        
        Args:
            older_than: 이 시간 이전의 작업만 정리
        """
        with self.lock:
            if older_than:
                # 특정 시간 이전 작업만 제거
                to_remove = [
                    task_id for task_id, result in self.completed_tasks.items()
                    if result.completed_at < older_than
                ]
                for task_id in to_remove:
                    del self.completed_tasks[task_id]
                
                removed_count = len(to_remove)
                if removed_count > 0:
                    self.logger.info(f"{removed_count}개 완료 작업 정리됨")
            else:
                # 모두 제거
                count = len(self.completed_tasks)
                self.completed_tasks.clear()
                if count > 0:
                    self.logger.info(f"{count}개 완료 작업 정리됨")
    
    def update_total_tasks(self, increment: int = 1):
        """전체 작업 수 업데이트"""
        with self.lock:
            self.total_tasks += increment
    
    def update_completed(self, success: bool):
        """완료 통계 업데이트"""
        with self.lock:
            self.completed_count += 1
            if not success:
                self.error_count += 1
    
    def reset_statistics(self):
        """통계 초기화"""
        with self.lock:
            self.total_tasks = 0
            self.completed_count = 0
            self.error_count = 0
            self.logger.info("통계 초기화됨")