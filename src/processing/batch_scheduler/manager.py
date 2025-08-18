# -*- coding: utf-8 -*-
"""
배치 스케줄러 매니저

스케줄 작업 관리와 조정을 담당하는 메인 클래스
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List, Callable

from .models import ScheduleTask, ScheduleFrequency
from .scheduler import SchedulerEngine
from .executor import TaskExecutor


class BatchScheduler:
    """
    배치 스케줄러 메인 클래스
    
    스케줄 작업의 생명주기를 관리하고 각 구성 요소를 조정
    """
    
    def __init__(self,
                 batch_processor: Optional[Any] = None,
                 config_file: Optional[Path] = None,
                 logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            batch_processor: 배치 처리기
            config_file: 스케줄 설정 파일
            logger: 로거
        """
        self.batch_processor = batch_processor
        self.logger = logger or logging.getLogger(__name__)
        
        # 설정 파일
        if config_file is None:
            config_dir = Path("data/config")
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "schedules.json"
        self.config_file = config_file
        
        # 스케줄 작업들
        self.tasks: Dict[str, ScheduleTask] = {}
        
        # 구성 요소 초기화
        self.scheduler_engine = SchedulerEngine(logger=self.logger)
        self.task_executor = TaskExecutor(
            batch_processor=batch_processor,
            logger=self.logger
        )
        
        # 실행 콜백 연결
        self.scheduler_engine.execute_callback = self._execute_task
        
        # 외부 콜백
        self.on_task_start: Optional[Callable[[ScheduleTask], None]] = None
        self.on_task_complete: Optional[Callable[[ScheduleTask, bool], None]] = None
        self.on_task_error: Optional[Callable[[ScheduleTask, Exception], None]] = None
        
        # 콜백 전달
        self._setup_callbacks()
        
        # 설정 로드
        self.load_tasks()
    
    def _setup_callbacks(self):
        """콜백 설정"""
        self.task_executor.on_task_start = self.on_task_start
        self.task_executor.on_task_complete = self.on_task_complete
        self.task_executor.on_task_error = self.on_task_error
    
    def load_tasks(self) -> bool:
        """스케줄 작업 로드"""
        if not self.config_file.exists():
            self.logger.info("스케줄 설정 파일이 없습니다. 새로 생성합니다.")
            self.save_tasks()
            return True
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.tasks = {}
            for task_data in data.get('tasks', []):
                task = ScheduleTask.from_dict(task_data)
                self.tasks[task.id] = task
            
            self.logger.info(f"스케줄 작업 {len(self.tasks)}개 로드 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"스케줄 작업 로드 실패: {e}")
            return False
    
    def save_tasks(self) -> bool:
        """스케줄 작업 저장"""
        try:
            data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'tasks': [task.to_dict() for task in self.tasks.values()]
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug("스케줄 작업 저장 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"스케줄 작업 저장 실패: {e}")
            return False
    
    def add_task(self, task: ScheduleTask) -> bool:
        """스케줄 작업 추가"""
        if task.id in self.tasks:
            self.logger.warning(f"이미 존재하는 작업 ID: {task.id}")
            return False
        
        # 유효성 검사
        valid, error_msg = self.task_executor.validate_task(task)
        if not valid:
            self.logger.error(f"작업 유효성 검사 실패: {error_msg}")
            return False
        
        self.tasks[task.id] = task
        
        # 실행 중이면 스케줄 추가
        if self.scheduler_engine.is_running:
            self.scheduler_engine.schedule_task(task)
        
        self.save_tasks()
        self.logger.info(f"스케줄 작업 추가: {task.name}")
        return True
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """스케줄 작업 업데이트"""
        if task_id not in self.tasks:
            self.logger.warning(f"존재하지 않는 작업 ID: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        # 업데이트
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # 유효성 재검사
        valid, error_msg = self.task_executor.validate_task(task)
        if not valid:
            self.logger.error(f"업데이트된 작업 유효성 검사 실패: {error_msg}")
            return False
        
        # 실행 중이면 스케줄 재설정
        if self.scheduler_engine.is_running:
            self.scheduler_engine.unschedule_task(task_id)
            if task.enabled:
                self.scheduler_engine.schedule_task(task)
        
        self.save_tasks()
        self.logger.info(f"스케줄 작업 업데이트: {task.name}")
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """스케줄 작업 제거"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks.pop(task_id)
        
        # 스케줄에서 제거
        if self.scheduler_engine.is_running:
            self.scheduler_engine.unschedule_task(task_id)
        
        self.save_tasks()
        self.logger.info(f"스케줄 작업 제거: {task.name}")
        return True
    
    def start(self):
        """스케줄러 시작"""
        if self.scheduler_engine.is_running:
            self.logger.warning("스케줄러가 이미 실행 중입니다")
            return
        
        # 모든 활성 작업 스케줄링
        for task in self.tasks.values():
            if task.enabled:
                self.scheduler_engine.schedule_task(task)
        
        # 스케줄러 엔진 시작
        self.scheduler_engine.start()
        
        self.logger.info("배치 스케줄러 시작")
    
    def stop(self):
        """스케줄러 중지"""
        self.scheduler_engine.stop()
        self.logger.info("배치 스케줄러 중지")
    
    def _execute_task(self, task_id: str):
        """작업 실행 (내부 콜백)"""
        if task_id not in self.tasks:
            self.logger.warning(f"존재하지 않는 작업 실행 요청: {task_id}")
            return
        
        task = self.tasks[task_id]
        
        # 작업 실행
        success = self.task_executor.execute_task(task)
        
        # 저장
        self.save_tasks()
        
        # ONCE 타입은 실행 후 스케줄에서 제거
        if task.frequency == ScheduleFrequency.ONCE and not task.enabled:
            self.scheduler_engine.unschedule_task(task_id)
    
    def get_next_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """다음 실행 예정 작업 목록"""
        next_runs = []
        
        for task in self.tasks.values():
            if task.enabled and task.next_run:
                try:
                    next_time = datetime.fromisoformat(task.next_run)
                    next_runs.append({
                        'task_id': task.id,
                        'name': task.name,
                        'next_run': next_time,
                        'frequency': task.frequency.value
                    })
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"다음 실행 시간 파싱 실패 {task.id}: {e}")
        
        # 시간순 정렬
        next_runs.sort(key=lambda x: x['next_run'])
        
        return next_runs[:limit]
    
    def get_task_history(self, task_id: str) -> Dict[str, Any]:
        """작업 실행 이력"""
        if task_id not in self.tasks:
            return {}
        
        task = self.tasks[task_id]
        
        return {
            'task_id': task.id,
            'name': task.name,
            'run_count': task.run_count,
            'error_count': task.error_count,
            'last_run': task.last_run,
            'next_run': task.next_run,
            'success_rate': task.success_rate
        }
    
    @property
    def is_running(self) -> bool:
        """스케줄러 실행 상태"""
        return self.scheduler_engine.is_running
    
    def get_all_tasks(self) -> List[ScheduleTask]:
        """모든 작업 목록"""
        return list(self.tasks.values())
    
    def get_task(self, task_id: str) -> Optional[ScheduleTask]:
        """특정 작업 조회"""
        return self.tasks.get(task_id)