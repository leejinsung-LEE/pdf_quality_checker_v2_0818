# src/ui/controllers/file_controller/__init__.py
"""
파일 컨트롤러 모듈

모듈화된 파일 컨트롤러를 통합하고 외부에 FileController를 제공합니다.
기존 API 호환성을 유지하면서 내부 구조를 모듈화했습니다.

모듈 구조:
- base.py: 기본 클래스와 데이터 모델 (FileStatus, FileItem, FileControllerBase)
- file_operations.py: 파일 처리 작업 관리 (add_files, cancel_file, retry_file 등)
- event_handler.py: 이벤트 처리 관리 (UI 콜백, 처리기 콜백)
- status_tracker.py: 상태 추적 및 통계 관리 (get_statistics, clear_completed 등)
"""

from typing import Dict, List, Optional, Callable, Any, Tuple
from pathlib import Path
import logging

from .base import FileControllerBase, FileStatus, FileItem
from .file_operations import FileOperations
from .event_handler import EventHandler
from .status_tracker import StatusTracker


class FileController(FileControllerBase):
    """
    파일 처리 컨트롤러 - 모듈화된 버전
    
    기존 API와 호환성을 유지하면서 내부를 모듈화한 파일 컨트롤러입니다.
    각 기능별로 모듈이 분리되어 있어 유지보수가 용이합니다.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        # 기본 클래스 초기화
        super().__init__(logger)
        
        # 모듈 초기화
        self.file_operations = FileOperations(self)
        self.event_handler = EventHandler(self)
        self.status_tracker = StatusTracker(self)
    
    # === 파일 작업 메서드들 (FileOperations에서 위임) ===
    
    def add_files(self, 
                 file_paths: List[Path],
                 profile: Optional[str] = None,
                 priority = None,  # TaskPriority import를 피하기 위해 Any 대신 None
                 auto_fix: bool = False) -> List[str]:
        """파일 처리 요청 추가"""
        from ....processing.queue_manager import TaskPriority
        if priority is None:
            priority = TaskPriority.NORMAL
        return self.file_operations.add_files(file_paths, profile, priority, auto_fix)
    
    def add_folder_file(self, file_path: Path, folder_config: Dict[str, Any]) -> str:
        """폴더 감시에서 발견된 파일 추가"""
        return self.file_operations.add_folder_file(file_path, folder_config)
    
    def process_immediately(self, file_path: Path, profile: Optional[str] = None, auto_fix: bool = False) -> str:
        """파일 즉시 처리"""
        return self.file_operations.process_immediately(file_path, profile, auto_fix)
    
    def cancel_file(self, file_id: str) -> bool:
        """파일 처리 취소"""
        return self.file_operations.cancel_file(file_id)
    
    def retry_file(self, file_id: str) -> bool:
        """파일 처리 재시도"""
        return self.file_operations.retry_file(file_id)
    
    def pause_processing(self) -> bool:
        """처리 일시정지"""
        return self.file_operations.pause_processing()
    
    def resume_processing(self) -> bool:
        """처리 재개"""
        return self.file_operations.resume_processing()
    
    def toggle_pause(self) -> bool:
        """처리 일시정지/재개 토글"""
        return self.file_operations.toggle_pause()
    
    # === 이벤트 처리 메서드들 (EventHandler에서 위임) ===
    
    def set_ui_callbacks(self,
                        on_file_added: Optional[Callable] = None,
                        on_file_status_changed: Optional[Callable] = None,
                        on_file_progress: Optional[Callable] = None,
                        on_file_completed: Optional[Callable] = None,
                        on_file_error: Optional[Callable] = None):
        """UI 콜백 설정"""
        self.event_handler.set_ui_callbacks(
            on_file_added,
            on_file_status_changed,
            on_file_progress,
            on_file_completed,
            on_file_error
        )
    
    # === 상태 추적 메서드들 (StatusTracker에서 위임) ===
    
    def get_file_item(self, file_id: str) -> Optional[FileItem]:
        """파일 아이템 조회"""
        return self.status_tracker.get_file_item(file_id)
    
    def get_all_files(self) -> List[FileItem]:
        """모든 파일 아이템 조회"""
        return self.status_tracker.get_all_files()
    
    def get_files_by_status(self, status: FileStatus) -> List[FileItem]:
        """상태별 파일 아이템 조회"""
        return self.status_tracker.get_files_by_status(status)
    
    def get_statistics(self) -> Dict[str, Any]:
        """처리 통계 조회"""
        return self.status_tracker.get_statistics()
    
    def clear_completed(self):
        """완료된 파일 목록에서 제거"""
        self.status_tracker.clear_completed()
    
    def clear_by_status(self, status: FileStatus):
        """특정 상태의 파일들을 목록에서 제거"""
        self.status_tracker.clear_by_status(status)
    
    def get_files_with_issues(self) -> List[FileItem]:
        """문제가 있는 파일들 조회"""
        return self.status_tracker.get_files_with_issues()
    
    def get_folder_files(self, folder_name: str) -> List[FileItem]:
        """특정 폴더의 파일들 조회"""
        return self.status_tracker.get_folder_files(folder_name)
    
    def get_profile_files(self, profile: str) -> List[FileItem]:
        """특정 프로파일로 처리된 파일들 조회"""
        return self.status_tracker.get_profile_files(profile)
    
    def get_files_summary(self) -> Dict[str, Any]:
        """파일 처리 요약 정보"""
        return self.status_tracker.get_files_summary()
    
    # === 기존 호환성을 위한 private 메서드들 ===
    
    def _setup_processor_callbacks(self):
        """처리기 콜백 설정 (기존 호환성)"""
        # 이미 EventHandler에서 처리됨
        pass
    
    def _on_processing_start(self, file_info):
        """처리 시작 콜백 (기존 호환성)"""
        return self.event_handler._on_processing_start(file_info)
    
    def _on_processing_progress(self, file_id: str, status: str, progress: int, message: str):
        """처리 진행률 콜백 (기존 호환성)"""
        return self.event_handler._on_processing_progress(file_id, status, progress, message)
    
    def _on_processing_complete(self, file_info, result):
        """처리 완료 콜백 (기존 호환성)"""
        return self.event_handler._on_processing_complete(file_info, result)
    
    def _on_processing_error(self, file_info, error_message: str):
        """처리 오류 콜백 (기존 호환성)"""
        return self.event_handler._on_processing_error(file_info, error_message)
    
    def _process_results(self):
        """결과 처리 스레드 (기존 호환성)"""
        # 이미 EventHandler에서 처리됨
        pass
    
    def _handle_task_result(self, file_id: str, result: Any):
        """작업 결과 처리 (기존 호환성)"""
        return self.file_operations._handle_task_result(file_id, result)


# 전역 컨트롤러 인스턴스
from functools import lru_cache


@lru_cache(maxsize=1)
def get_file_controller() -> FileController:
    """전역 파일 컨트롤러 인스턴스 반환 (스레드 안전)
    
    LRU 캐시를 사용하여 싱글톤 패턴을 구현합니다.
    Python 내장 기능으로 스레드 안전성이 보장됩니다.
    
    Returns:
        FileController: 싱글톤 인스턴스
    """
    return FileController()


# 외부 사용을 위한 export
__all__ = ['FileController', 'FileStatus', 'FileItem', 'get_file_controller']