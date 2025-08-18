# src/ui/controllers/file_controller/base.py
"""
파일 컨트롤러 기본 클래스

FileController의 핵심 구조와 데이터 모델을 정의합니다.
"""

import threading
from typing import Dict, List, Optional, Callable, Any, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
import logging
from enum import Enum

from ....processing import (
    PDFProcessor,
    BatchProcessor,
    QueueManager,
    ProcessingResult,
    ProcessingStatus,
    get_processor,
    get_queue_manager
)
from ....processing.queue_manager import TaskType, TaskPriority
from ....core.profiles import ProfileManager, get_profile_manager


class FileStatus(Enum):
    """파일 처리 상태"""
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class FileItem:
    """UI에 표시할 파일 정보"""
    file_id: str
    path: Path
    status: FileStatus = FileStatus.WAITING
    progress: int = 0
    message: str = ""
    profile: str = "default"
    
    # 처리 정보
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    processing_time: float = 0.0
    
    # 결과 정보
    error_count: int = 0
    warning_count: int = 0
    quality_score: float = 0.0
    report_paths: Dict[str, Path] = field(default_factory=dict)
    
    # 폴더 감시 정보
    folder_name: Optional[str] = None
    folder_config: Optional[Dict[str, Any]] = None
    
    @property
    def filename(self) -> str:
        """파일명"""
        return self.path.name
    
    @property
    def size_mb(self) -> float:
        """파일 크기 (MB)"""
        try:
            return self.path.stat().st_size / (1024 * 1024)
        except:
            return 0.0
    
    @property
    def has_issues(self) -> bool:
        """문제가 있는지 확인"""
        return self.error_count > 0 or self.warning_count > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'file_id': self.file_id,
            'filename': self.filename,
            'path': str(self.path),
            'status': self.status.value,
            'progress': self.progress,
            'message': self.message,
            'profile': self.profile,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'quality_score': self.quality_score,
            'processing_time': self.processing_time,
            'folder_name': self.folder_name
        }


class FileControllerBase:
    """
    파일 처리 컨트롤러 기본 클래스
    
    UI의 파일 처리 요청을 받아 v2 처리 시스템과 연동합니다.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        컨트롤러 초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 처리 시스템
        self.processor = get_processor()
        self.queue_manager = get_queue_manager()
        self.profile_manager = get_profile_manager()
        
        # 폴더 감시 시스템
        from ....processing.folder_watcher import FolderWatcher
        self.folder_watcher = FolderWatcher()
        
        # 파일 관리
        self.file_items: Dict[str, FileItem] = {}
        
        # 일시정지 상태
        self.is_paused: bool = False
        
        # UI 콜백
        self.on_file_added: Optional[Callable[[FileItem], None]] = None
        self.on_file_status_changed: Optional[Callable[[str, FileStatus], None]] = None
        self.on_file_progress: Optional[Callable[[str, int, str], None]] = None
        self.on_file_completed: Optional[Callable[[str, FileItem], None]] = None
        self.on_file_error: Optional[Callable[[str, str], None]] = None
    
    def _generate_file_id(self, file_path: Path) -> str:
        """파일 ID 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        name_part = file_path.stem[:20]
        return f"{name_part}_{timestamp}"
    
    def _count_completed_today(self) -> int:
        """오늘 완료된 파일 수"""
        today = datetime.now().date()
        count = 0
        
        for item in self.file_items.values():
            if (item.status == FileStatus.COMPLETED and 
                item.end_time and 
                item.end_time.date() == today):
                count += 1
        
        return count