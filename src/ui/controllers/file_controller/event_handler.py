# src/ui/controllers/file_controller/event_handler.py
"""
이벤트 처리 관리

UI 콜백 설정과 처리기 이벤트 처리를 담당합니다.
"""

import threading
from typing import Optional, Callable, Any, TYPE_CHECKING
from datetime import datetime

from ....processing import ProcessingResult
from ....processing.queue_manager import TaskType

if TYPE_CHECKING:
    from .base import FileControllerBase, FileStatus, FileItem


class EventHandler:
    """이벤트 처리 관리 클래스"""
    
    def __init__(self, parent: 'FileControllerBase'):
        self.parent = parent
        
        # 처리기 콜백 설정
        self._setup_processor_callbacks()
        
        # 결과 처리 스레드
        self.result_thread = threading.Thread(target=self._process_results, daemon=True)
        self.result_thread.start()
    
    def _setup_processor_callbacks(self):
        """처리기 콜백 설정"""
        self.parent.processor.set_callbacks(
            on_start=self._on_processing_start,
            on_progress=self._on_processing_progress,
            on_complete=self._on_processing_complete,
            on_error=self._on_processing_error
        )
    
    def set_ui_callbacks(self,
                        on_file_added: Optional[Callable] = None,
                        on_file_status_changed: Optional[Callable] = None,
                        on_file_progress: Optional[Callable] = None,
                        on_file_completed: Optional[Callable] = None,
                        on_file_error: Optional[Callable] = None):
        """
        UI 콜백 설정
        
        Args:
            on_file_added: 파일 추가 콜백 (FileItem)
            on_file_status_changed: 상태 변경 콜백 (file_id, FileStatus)
            on_file_progress: 진행률 콜백 (file_id, progress, message)
            on_file_completed: 완료 콜백 (file_id, FileItem)
            on_file_error: 오류 콜백 (file_id, error_message)
        """
        self.parent.on_file_added = on_file_added
        self.parent.on_file_status_changed = on_file_status_changed
        self.parent.on_file_progress = on_file_progress
        self.parent.on_file_completed = on_file_completed
        self.parent.on_file_error = on_file_error
    
    def _on_processing_start(self, file_info):
        """처리 시작 콜백"""
        # file_info에서 파일 경로나 ID 추출
        if hasattr(file_info, 'file_path'):
            file_path = file_info.file_path
        elif isinstance(file_info, dict) and 'file_path' in file_info:
            file_path = file_info['file_path']
        else:
            return
        
        # 해당 파일 아이템 찾기
        for file_id, file_item in self.parent.file_items.items():
            if str(file_item.path) == str(file_path):
                file_item.message = "처리 시작"
                break
    
    def _on_processing_progress(self, file_id: str, status: str, progress: int, message: str):
        """처리 진행률 콜백"""
        if file_id in self.parent.file_items:
            file_item = self.parent.file_items[file_id]
            file_item.progress = progress
            file_item.message = message
            
            # UI 콜백
            if self.parent.on_file_progress:
                self.parent.on_file_progress(file_id, progress, message)
    
    def _on_processing_complete(self, file_info, result: ProcessingResult):
        """처리 완료 콜백"""
        # file_info에서 파일 경로나 ID 추출
        if hasattr(file_info, 'file_path'):
            file_path = file_info.file_path
        elif isinstance(file_info, dict) and 'file_path' in file_info:
            file_path = file_info['file_path']
        else:
            return
        
        # 해당 파일 아이템 찾기
        file_id = None
        for fid, file_item in self.parent.file_items.items():
            if str(file_item.path) == str(file_path):
                file_id = fid
                break
        
        if not file_id:
            return
        
        file_item = self.parent.file_items[file_id]
        
        # 상태 업데이트
        from .base import FileStatus
        file_item.status = FileStatus.COMPLETED
        file_item.end_time = datetime.now()
        if file_item.start_time:
            file_item.processing_time = (file_item.end_time - file_item.start_time).total_seconds()
        
        # 결과 정보 업데이트
        if hasattr(result, 'issues') and result.issues:
            file_item.error_count = len([i for i in result.issues if i.severity == 'error'])
            file_item.warning_count = len([i for i in result.issues if i.severity == 'warning'])
        
        if hasattr(result, 'quality_score'):
            file_item.quality_score = result.quality_score
        
        if hasattr(result, 'report_paths'):
            file_item.report_paths = result.report_paths
        
        file_item.message = "처리 완료"
        
        # UI 콜백
        if self.parent.on_file_status_changed:
            self.parent.on_file_status_changed(file_id, FileStatus.COMPLETED)
        
        if self.parent.on_file_completed:
            self.parent.on_file_completed(file_id, file_item)
    
    def _on_processing_error(self, file_info, error_message: str):
        """처리 오류 콜백"""
        # file_info에서 파일 경로나 ID 추출
        if hasattr(file_info, 'file_path'):
            file_path = file_info.file_path
        elif isinstance(file_info, dict) and 'file_path' in file_info:
            file_path = file_info['file_path']
        else:
            return
        
        # 해당 파일 아이템 찾기
        file_id = None
        for fid, file_item in self.parent.file_items.items():
            if str(file_item.path) == str(file_path):
                file_id = fid
                break
        
        if not file_id:
            return
        
        file_item = self.parent.file_items[file_id]
        
        # 상태 업데이트
        from .base import FileStatus
        file_item.status = FileStatus.ERROR
        file_item.end_time = datetime.now()
        file_item.message = error_message
        
        # UI 콜백
        if self.parent.on_file_status_changed:
            self.parent.on_file_status_changed(file_id, FileStatus.ERROR)
        
        if self.parent.on_file_error:
            self.parent.on_file_error(file_id, error_message)
    
    def _process_results(self):
        """결과 처리 스레드"""
        while True:
            try:
                # 결과 큐에서 대기
                result = self.parent.queue_manager.result_queue.get(timeout=1.0)
                
                # 결과 처리
                if result.task_type == TaskType.PROCESS_FILE:
                    # 파일 처리 결과는 processor 콜백에서 이미 처리됨
                    pass
                
            except:
                # 타임아웃 또는 오류 - 계속 진행
                pass