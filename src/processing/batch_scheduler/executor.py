# -*- coding: utf-8 -*-
"""
작업 실행기

스케줄된 작업의 실제 실행을 담당
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Callable, List, Dict

from .models import ScheduleTask, ScheduleFrequency


class TaskExecutor:
    """
    작업 실행기
    
    스케줄된 작업을 실행하고 결과를 처리
    """
    
    def __init__(self,
                 batch_processor: Optional[Any] = None,
                 logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            batch_processor: 배치 처리기
            logger: 로거
        """
        self.batch_processor = batch_processor
        self.logger = logger or logging.getLogger(__name__)
        
        # 실행 콜백
        self.on_task_start: Optional[Callable[[ScheduleTask], None]] = None
        self.on_task_complete: Optional[Callable[[ScheduleTask, bool], None]] = None
        self.on_task_error: Optional[Callable[[ScheduleTask, Exception], None]] = None
    
    def execute_task(self, task: ScheduleTask) -> bool:
        """
        작업 실행
        
        Args:
            task: 실행할 스케줄 작업
            
        Returns:
            실행 성공 여부
        """
        # 실행 시작 알림
        self._notify_start(task)
        
        try:
            # 작업 실행
            result = self._run_task(task)
            
            # 통계 업데이트
            task.update_stats(success=result)
            
            # 완료 알림
            self._notify_complete(task, result)
            
            return result
            
        except Exception as e:
            # 오류 처리
            self._handle_error(task, e)
            return False
    
    def _run_task(self, task: ScheduleTask) -> bool:
        """
        실제 작업 실행
        
        Args:
            task: 스케줄 작업
            
        Returns:
            실행 성공 여부
        """
        self.logger.info(f"작업 실행 시작: {task.name}")
        
        # 폴더 경로 확인
        folder_path = Path(task.folder_path)
        if not folder_path.exists():
            raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")
        
        # PDF 파일 수집
        pdf_files = self._collect_files(folder_path, task)
        
        if not pdf_files:
            self.logger.info("처리할 PDF 파일이 없습니다")
            return True  # 파일이 없어도 성공으로 처리
        
        self.logger.info(f"처리할 파일 {len(pdf_files)}개 발견")
        
        # 배치 처리 실행
        if self.batch_processor:
            return self._process_batch(pdf_files, task)
        else:
            self.logger.warning("배치 처리기가 설정되지 않았습니다")
            return False
    
    def _collect_files(self, folder_path: Path, task: ScheduleTask) -> List[Path]:
        """
        처리할 파일 수집
        
        Args:
            folder_path: 폴더 경로
            task: 스케줄 작업
            
        Returns:
            PDF 파일 목록
        """
        pattern = task.file_pattern or "*.pdf"
        
        if task.recursive:
            # 재귀적으로 검색
            files = list(folder_path.rglob(pattern))
        else:
            # 현재 폴더만 검색
            files = list(folder_path.glob(pattern))
        
        # 파일만 필터링 (디렉토리 제외)
        return [f for f in files if f.is_file()]
    
    def _process_batch(self, files: List[Path], task: ScheduleTask) -> bool:
        """
        배치 처리 실행
        
        Args:
            files: 처리할 파일 목록
            task: 스케줄 작업
            
        Returns:
            처리 성공 여부
        """
        try:
            # 프로파일 설정
            if hasattr(self.batch_processor, 'set_profile'):
                self.batch_processor.set_profile(task.profile)
            
            # 자동 수정 설정
            if hasattr(self.batch_processor, 'set_auto_fix'):
                self.batch_processor.set_auto_fix(task.auto_fix)
            
            # 배치 처리 실행
            if hasattr(self.batch_processor, 'process_batch'):
                results = self.batch_processor.process_batch(files)
                
                # 결과 분석
                success_count = sum(1 for r in results if r.get('success', False))
                total_count = len(results)
                
                self.logger.info(
                    f"배치 처리 완료: {success_count}/{total_count} 성공"
                )
                
                # 전체 성공 여부 판단
                return success_count == total_count
            else:
                self.logger.error("배치 처리기에 process_batch 메서드가 없습니다")
                return False
                
        except Exception as e:
            self.logger.error(f"배치 처리 중 오류: {e}")
            return False
    
    def _notify_start(self, task: ScheduleTask):
        """작업 시작 알림"""
        if self.on_task_start:
            try:
                self.on_task_start(task)
            except Exception as e:
                self.logger.error(f"작업 시작 콜백 오류: {e}")
    
    def _notify_complete(self, task: ScheduleTask, success: bool):
        """작업 완료 알림"""
        if self.on_task_complete:
            try:
                self.on_task_complete(task, success)
            except Exception as e:
                self.logger.error(f"작업 완료 콜백 오류: {e}")
        
        self.logger.info(
            f"작업 완료: {task.name} (성공: {success})"
        )
    
    def _handle_error(self, task: ScheduleTask, error: Exception):
        """오류 처리"""
        # 통계 업데이트
        task.update_stats(success=False)
        
        # 오류 알림
        if self.on_task_error:
            try:
                self.on_task_error(task, error)
            except Exception as e:
                self.logger.error(f"작업 오류 콜백 실패: {e}")
        
        self.logger.error(f"작업 실패 {task.name}: {error}")
    
    def validate_task(self, task: ScheduleTask) -> tuple[bool, str]:
        """
        작업 유효성 검사
        
        Args:
            task: 스케줄 작업
            
        Returns:
            (유효 여부, 오류 메시지)
        """
        # 폴더 경로 확인
        if not task.folder_path:
            return False, "폴더 경로가 지정되지 않았습니다"
        
        folder_path = Path(task.folder_path)
        if not folder_path.exists():
            return False, f"폴더가 존재하지 않습니다: {folder_path}"
        
        if not folder_path.is_dir():
            return False, f"디렉토리가 아닙니다: {folder_path}"
        
        # 시간 형식 확인
        if task.time:
            try:
                datetime.strptime(task.time, "%H:%M")
            except ValueError:
                return False, f"잘못된 시간 형식: {task.time} (HH:MM 형식 필요)"
        
        # 요일 확인
        if task.frequency == ScheduleFrequency.WEEKLY:
            if task.weekday is None or not (0 <= task.weekday <= 6):
                return False, "주간 스케줄에는 유효한 요일(0-6)이 필요합니다"
        
        return True, ""