# src/processing/queue_manager/task_tracker.py
"""
작업 상태 추적 및 완료 처리
"""

import queue
import threading
import time
from typing import Dict, Optional, Callable, Any
import logging

from .base import Task, TaskResult


class TaskTracker:
    """작업 상태 추적기"""
    
    def __init__(self,
                 task_queue: queue.PriorityQueue,
                 result_queue: queue.Queue,
                 pending_tasks: Dict[str, Task],
                 active_tasks: Dict[str, Task],
                 completed_tasks: Dict[str, TaskResult],
                 lock: threading.RLock,
                 logger: Optional[logging.Logger] = None):
        """
        작업 추적기 초기화
        
        Args:
            task_queue: 작업 큐
            result_queue: 결과 큐
            pending_tasks: 대기 중인 작업
            active_tasks: 처리 중인 작업
            completed_tasks: 완료된 작업
            lock: 스레드 락
            logger: 로거
        """
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.pending_tasks = pending_tasks
        self.active_tasks = active_tasks
        self.completed_tasks = completed_tasks
        self.lock = lock
        self.logger = logger or logging.getLogger(__name__)
        
        # 콜백
        self.on_task_complete: Optional[Callable] = None
        self.on_task_error: Optional[Callable] = None
        
        # 통계 (statistics 모듈과 공유)
        self.completed_count = 0
        self.error_count = 0
    
    def get_next_task(self, timeout: Optional[float] = None) -> Optional[Task]:
        """
        다음 작업 가져오기
        
        Args:
            timeout: 대기 시간
            
        Returns:
            Task: 작업 또는 None
        """
        try:
            task = self.task_queue.get(timeout=timeout)
            
            with self.lock:
                # 대기 목록에서 활성 목록으로 이동
                if task.task_id in self.pending_tasks:
                    del self.pending_tasks[task.task_id]
                self.active_tasks[task.task_id] = task
            
            return task
            
        except queue.Empty:
            return None
    
    def complete_task(self, 
                     task_id: str,
                     success: bool,
                     result: Any,
                     error: Optional[str] = None,
                     processing_time: float = 0.0):
        """
        작업 완료 처리
        
        Args:
            task_id: 작업 ID
            success: 성공 여부
            result: 작업 결과
            error: 오류 메시지
            processing_time: 처리 시간
        """
        task = None
        
        with self.lock:
            # 활성 작업 확인
            task = self.active_tasks.get(task_id)
            if not task:
                self.logger.warning(f"알 수 없는 작업 완료: {task_id}")
                return
            
            # 활성 목록에서 제거
            del self.active_tasks[task_id]
            
            # 결과 생성
            task_result = TaskResult(
                task_id=task_id,
                task_type=task.task_type,
                success=success,
                result=result,
                error=error,
                processing_time=processing_time
            )
            
            # 완료 목록에 추가
            self.completed_tasks[task_id] = task_result
            
            # 통계 업데이트
            self.completed_count += 1
            if not success:
                self.error_count += 1
        
        # 결과 큐에 추가 (락 밖에서)
        self.result_queue.put(task_result)
        
        # 콜백 호출 (락 밖에서)
        if task and task.callback:
            try:
                task.callback(task_result)
            except Exception as e:
                self.logger.error(f"작업 콜백 오류: {e}")
        
        if success and self.on_task_complete:
            try:
                self.on_task_complete(task_id, result)
            except Exception as e:
                self.logger.error(f"완료 콜백 오류: {e}")
        elif not success and self.on_task_error:
            try:
                self.on_task_error(task_id, error)
            except Exception as e:
                self.logger.error(f"에러 콜백 오류: {e}")
        
        self.logger.debug(f"작업 완료: {task_id} (성공: {success})")
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        작업 상태 조회
        
        Args:
            task_id: 작업 ID
            
        Returns:
            str: 상태 ('pending', 'active', 'completed', None)
        """
        with self.lock:
            if task_id in self.pending_tasks:
                return 'pending'
            elif task_id in self.active_tasks:
                return 'active'
            elif task_id in self.completed_tasks:
                return 'completed'
            return None
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        작업 결과 조회
        
        Args:
            task_id: 작업 ID
            
        Returns:
            TaskResult: 작업 결과 또는 None
        """
        with self.lock:
            return self.completed_tasks.get(task_id)
    
    def wait_for_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """
        작업 결과 대기
        
        Args:
            task_id: 작업 ID
            timeout: 대기 시간
            
        Returns:
            TaskResult: 작업 결과 또는 None
        """
        start_time = time.time()
        
        while True:
            # 이미 완료되었는지 확인
            result = self.get_task_result(task_id)
            if result:
                return result
            
            # 타임아웃 확인
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            # 잠시 대기
            time.sleep(0.1)
    
    def set_callbacks(self,
                     on_task_complete: Optional[Callable] = None,
                     on_task_error: Optional[Callable] = None):
        """
        콜백 설정
        
        Args:
            on_task_complete: 작업 완료 콜백
            on_task_error: 작업 에러 콜백
        """
        self.on_task_complete = on_task_complete
        self.on_task_error = on_task_error