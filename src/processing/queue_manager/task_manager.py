# src/processing/queue_manager/task_manager.py
"""
작업 추가 및 관리
"""

import queue
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import logging

from .base import TaskType, TaskPriority, Task, TaskResult


class TaskManager:
    """작업 관리자"""
    
    def __init__(self, 
                 task_queue: queue.PriorityQueue,
                 pending_tasks: Dict[str, Task],
                 active_tasks: Dict[str, Task],
                 completed_tasks: Dict[str, TaskResult],
                 lock: threading.RLock,
                 logger: Optional[logging.Logger] = None):
        """
        작업 관리자 초기화
        
        Args:
            task_queue: 작업 큐
            pending_tasks: 대기 중인 작업
            active_tasks: 처리 중인 작업
            completed_tasks: 완료된 작업
            lock: 스레드 락
            logger: 로거
        """
        self.task_queue = task_queue
        self.pending_tasks = pending_tasks
        self.active_tasks = active_tasks
        self.completed_tasks = completed_tasks
        self.lock = lock
        self.logger = logger or logging.getLogger(__name__)
        
        # 통계
        self.total_tasks = 0
    
    def add_task(self, 
                task_type: TaskType,
                data: Dict[str, Any],
                priority: TaskPriority = TaskPriority.NORMAL,
                callback: Optional[Callable] = None) -> str:
        """
        작업 추가
        
        Args:
            task_type: 작업 유형
            data: 작업 데이터
            priority: 우선순위
            callback: 완료 콜백
            
        Returns:
            str: 작업 ID
        """
        # 작업 ID 생성
        task_id = self._generate_task_id(task_type)
        
        # 작업 생성
        task = Task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            data=data,
            callback=callback
        )
        
        with self.lock:
            # 대기 목록에 추가
            self.pending_tasks[task_id] = task
            self.total_tasks += 1
        
        # 큐에 추가
        self.task_queue.put(task)
        
        self.logger.debug(f"작업 추가: {task_id} ({task_type.value})")
        return task_id
    
    def add_file_processing_task(self,
                               file_path: Path,
                               profile: str = "default",
                               auto_fix: bool = False,
                               priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """
        파일 처리 작업 추가 (편의 메서드)
        
        Args:
            file_path: PDF 파일 경로
            profile: 프로파일 이름
            auto_fix: 자동 수정 여부
            priority: 우선순위
            
        Returns:
            str: 작업 ID
        """
        data = {
            'file_path': str(file_path),
            'profile': profile,
            'auto_fix': auto_fix
        }
        
        return self.add_task(
            TaskType.PROCESS_FILE,
            data,
            priority
        )
    
    def add_batch_processing_task(self,
                                file_paths: List[Path],
                                profile: str = "default",
                                priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """
        배치 처리 작업 추가
        
        Args:
            file_paths: PDF 파일 경로 목록
            profile: 프로파일 이름
            priority: 우선순위
            
        Returns:
            str: 작업 ID
        """
        data = {
            'file_paths': [str(p) for p in file_paths],
            'profile': profile
        }
        
        return self.add_task(
            TaskType.BATCH_PROCESS,
            data,
            priority
        )
    
    def cancel_task(self, task_id: str) -> bool:
        """
        작업 취소
        
        Args:
            task_id: 작업 ID
            
        Returns:
            bool: 취소 성공 여부
        """
        with self.lock:
            # 대기 중인 작업만 취소 가능
            if task_id in self.pending_tasks:
                task = self.pending_tasks[task_id]
                del self.pending_tasks[task_id]
                
                # 취소 결과 생성
                task_result = TaskResult(
                    task_id=task_id,
                    task_type=task.task_type,
                    success=False,
                    result=None,
                    error="작업이 취소되었습니다"
                )
                
                # 완료 목록에 추가
                self.completed_tasks[task_id] = task_result
                
                self.logger.info(f"작업 취소됨: {task_id}")
                return True
            
            return False
    
    def _generate_task_id(self, task_type: TaskType) -> str:
        """작업 ID 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        return f"{task_type.value}_{timestamp}"
    
    def get_total_tasks(self) -> int:
        """전체 작업 수 반환"""
        return self.total_tasks