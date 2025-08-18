# -*- coding: utf-8 -*-
"""
스케줄링 엔진

schedule 라이브러리를 활용한 작업 스케줄 관리
"""

import schedule
import threading
import time
import logging
from datetime import datetime
from typing import Dict, Callable, Optional, List, Any

from .models import ScheduleTask, ScheduleFrequency


class SchedulerEngine:
    """
    스케줄링 엔진
    
    schedule 라이브러리를 활용하여 작업 스케줄을 관리하고 실행
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """초기화"""
        self.logger = logger or logging.getLogger(__name__)
        
        # 스케줄러 스레드 관리
        self.scheduler_thread: Optional[threading.Thread] = None
        self.is_running = False
        self._stop_event = threading.Event()
        
        # 작업 실행 콜백
        self.execute_callback: Optional[Callable[[str], None]] = None
        
        # 스케줄된 작업 추적
        self.scheduled_tasks: Dict[str, Any] = {}
    
    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            self.logger.warning("스케줄러가 이미 실행 중입니다")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # 스케줄러 스레드 시작
        self.scheduler_thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="SchedulerEngine"
        )
        self.scheduler_thread.start()
        
        self.logger.info("스케줄링 엔진 시작")
    
    def stop(self):
        """스케줄러 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        # 모든 스케줄 취소
        schedule.clear()
        self.scheduled_tasks.clear()
        
        # 스레드 종료 대기
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("스케줄링 엔진 중지")
    
    def _run_loop(self):
        """스케줄러 실행 루프"""
        while not self._stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(30)  # 30초마다 체크
            except Exception as e:
                self.logger.error(f"스케줄러 루프 오류: {e}")
    
    def schedule_task(self, task: ScheduleTask) -> bool:
        """
        작업 스케줄링
        
        Args:
            task: 스케줄 작업
            
        Returns:
            스케줄링 성공 여부
        """
        if not task.enabled:
            return False
        
        try:
            job = self._create_job(task)
            
            if job:
                self.scheduled_tasks[task.id] = job
                
                # 다음 실행 시간 업데이트
                if hasattr(job, 'next_run') and job.next_run:
                    task.next_run = job.next_run.isoformat()
                
                self.logger.debug(
                    f"작업 스케줄링 완료: {task.name} "
                    f"(다음 실행: {task.next_run})"
                )
                return True
            
        except Exception as e:
            self.logger.error(f"작업 스케줄링 실패 {task.name}: {e}")
        
        return False
    
    def _create_job(self, task: ScheduleTask):
        """
        스케줄 작업 생성
        
        Args:
            task: 스케줄 작업
            
        Returns:
            schedule.Job 인스턴스
        """
        job = None
        
        if task.frequency == ScheduleFrequency.ONCE:
            # 한 번만 실행
            job = schedule.every().day.at(task.time).do(
                self._execute_wrapper, task.id
            )
            
        elif task.frequency == ScheduleFrequency.DAILY:
            # 매일
            job = schedule.every().day.at(task.time).do(
                self._execute_wrapper, task.id
            )
            
        elif task.frequency == ScheduleFrequency.WEEKLY:
            # 매주 특정 요일
            if task.weekday is not None:
                weekdays = [
                    'monday', 'tuesday', 'wednesday', 'thursday',
                    'friday', 'saturday', 'sunday'
                ]
                if 0 <= task.weekday < len(weekdays):
                    weekday = weekdays[task.weekday]
                    job = getattr(schedule.every(), weekday).at(task.time).do(
                        self._execute_wrapper, task.id
                    )
                    
        elif task.frequency == ScheduleFrequency.MONTHLY:
            # 매월 (근사치 - 4주마다)
            job = schedule.every(4).weeks.at(task.time).do(
                self._execute_wrapper, task.id
            )
            
        elif task.frequency == ScheduleFrequency.HOURLY:
            # 매시간
            job = schedule.every().hour.do(
                self._execute_wrapper, task.id
            )
        
        return job
    
    def _execute_wrapper(self, task_id: str):
        """작업 실행 래퍼"""
        if self.execute_callback:
            try:
                self.execute_callback(task_id)
            except Exception as e:
                self.logger.error(f"작업 실행 중 오류 (ID: {task_id}): {e}")
    
    def unschedule_task(self, task_id: str) -> bool:
        """
        작업 스케줄 취소
        
        Args:
            task_id: 작업 ID
            
        Returns:
            취소 성공 여부
        """
        if task_id in self.scheduled_tasks:
            # schedule 라이브러리의 한계로 전체를 다시 스케줄링
            # (특정 작업만 취소하는 API가 없음)
            current_tasks = list(self.scheduled_tasks.items())
            
            # 모든 스케줄 취소
            schedule.clear()
            self.scheduled_tasks.clear()
            
            # 취소할 작업 제외하고 다시 스케줄링
            for tid, job in current_tasks:
                if tid != task_id:
                    self.scheduled_tasks[tid] = job
                    # 작업을 다시 스케줄에 추가
                    schedule.jobs.append(job)
            
            self.logger.debug(f"작업 스케줄 취소: {task_id}")
            return True
        
        return False
    
    def reschedule_all(self, tasks: Dict[str, ScheduleTask]):
        """
        모든 작업 재스케줄링
        
        Args:
            tasks: 모든 스케줄 작업
        """
        # 기존 스케줄 모두 취소
        schedule.clear()
        self.scheduled_tasks.clear()
        
        # 활성화된 작업들 스케줄링
        for task in tasks.values():
            if task.enabled:
                self.schedule_task(task)
    
    def get_next_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        다음 실행 예정 작업 목록
        
        Args:
            limit: 최대 개수
            
        Returns:
            다음 실행 예정 작업 정보
        """
        next_runs = []
        
        for job in schedule.jobs[:limit]:
            if hasattr(job, 'next_run') and job.next_run:
                next_runs.append({
                    'next_run': job.next_run.isoformat(),
                    'job': str(job)
                })
        
        return next_runs
    
    @property
    def job_count(self) -> int:
        """스케줄된 작업 개수"""
        return len(schedule.jobs)