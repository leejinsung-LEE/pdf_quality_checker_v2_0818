# src/ui/controllers/file_controller/file_operations.py
"""
파일 처리 작업 관리

파일 추가, 처리, 취소, 재시도 등 파일 조작 기능을 제공합니다.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
from pathlib import Path
from datetime import datetime

from ....processing.queue_manager import TaskType, TaskPriority

if TYPE_CHECKING:
    from .base import FileControllerBase, FileStatus, FileItem


class FileOperations:
    """파일 작업 관리 클래스"""
    
    def __init__(self, parent: 'FileControllerBase'):
        self.parent = parent
    
    def add_files(self, 
                 file_paths: List[Path],
                 profile: Optional[str] = None,
                 priority: TaskPriority = TaskPriority.NORMAL,
                 auto_fix: bool = False) -> List[str]:
        """
        파일 처리 요청 추가
        
        Args:
            file_paths: PDF 파일 경로 목록
            profile: 사용할 프로파일
            priority: 처리 우선순위
            auto_fix: 자동 수정 여부
            
        Returns:
            List[str]: 추가된 파일 ID 목록
        """
        if profile is None:
            profile = self.parent.profile_manager.current_profile_name or "default"
        
        file_ids = []
        
        for file_path in file_paths:
            # 파일 아이템 생성
            file_id = self.parent._generate_file_id(file_path)
            from .base import FileItem, FileStatus
            file_item = FileItem(
                file_id=file_id,
                path=file_path,
                profile=profile
            )
            
            # 관리 목록에 추가
            self.parent.file_items[file_id] = file_item
            
            # UI 콜백
            if self.parent.on_file_added:
                self.parent.on_file_added(file_item)
            
            # 작업 큐에 추가
            task_data = {
                'file_path': str(file_path),
                'profile': profile,
                'auto_fix': auto_fix
            }
            
            # 작업 시작 상태로 변경
            file_item.status = FileStatus.PROCESSING
            file_item.start_time = datetime.now()
            if self.parent.on_file_status_changed:
                self.parent.on_file_status_changed(file_id, FileStatus.PROCESSING)
            
            self.parent.queue_manager.add_task(
                TaskType.PROCESS_FILE,
                task_data,
                priority,
                callback=lambda result, fid=file_id: self._handle_task_result(fid, result)
            )
            
            file_ids.append(file_id)
            self.parent.logger.info(f"파일 추가: {file_path.name} (ID: {file_id})")
        
        return file_ids
    
    def add_folder_file(self,
                       file_path: Path,
                       folder_config: Dict[str, Any]) -> str:
        """
        폴더 감시에서 발견된 파일 추가
        
        Args:
            file_path: PDF 파일 경로
            folder_config: 폴더 설정
            
        Returns:
            str: 파일 ID
        """
        file_id = self.parent._generate_file_id(file_path)
        
        # 폴더 설정에서 프로파일 가져오기
        profile = folder_config.get('profile', 'default')
        priority = TaskPriority(folder_config.get('priority', 'normal'))
        auto_fix = folder_config.get('auto_fix', False)
        
        from .base import FileItem, FileStatus
        file_item = FileItem(
            file_id=file_id,
            path=file_path,
            profile=profile,
            folder_name=folder_config.get('name'),
            folder_config=folder_config
        )
        
        # 관리 목록에 추가
        self.parent.file_items[file_id] = file_item
        
        # UI 콜백
        if self.parent.on_file_added:
            self.parent.on_file_added(file_item)
        
        # 작업 큐에 추가
        task_data = {
            'file_path': str(file_path),
            'profile': profile,
            'auto_fix': auto_fix,
            'folder_config': folder_config
        }
        
        # 작업 시작 상태로 변경
        file_item.status = FileStatus.PROCESSING
        file_item.start_time = datetime.now()
        if self.parent.on_file_status_changed:
            self.parent.on_file_status_changed(file_id, FileStatus.PROCESSING)
        
        self.parent.queue_manager.add_task(
            TaskType.PROCESS_FILE,
            task_data,
            priority,
            callback=lambda result, fid=file_id: self._handle_task_result(fid, result)
        )
        
        self.parent.logger.info(f"폴더 파일 추가: {file_path.name} (폴더: {folder_config.get('name')})")
        return file_id
    
    def process_immediately(self,
                          file_path: Path,
                          profile: Optional[str] = None,
                          auto_fix: bool = False) -> str:
        """
        파일 즉시 처리 (높은 우선순위)
        
        Args:
            file_path: PDF 파일 경로
            profile: 사용할 프로파일
            auto_fix: 자동 수정 여부
            
        Returns:
            str: 파일 ID
        """
        if profile is None:
            profile = self.parent.profile_manager.current_profile_name or "default"
        
        file_id = self.parent._generate_file_id(file_path)
        from .base import FileItem, FileStatus
        file_item = FileItem(
            file_id=file_id,
            path=file_path,
            profile=profile
        )
        
        # 관리 목록에 추가
        self.parent.file_items[file_id] = file_item
        
        # UI 콜백
        if self.parent.on_file_added:
            self.parent.on_file_added(file_item)
        
        # 작업 큐에 즉시 처리로 추가
        task_data = {
            'file_path': str(file_path),
            'profile': profile,
            'auto_fix': auto_fix
        }
        
        # 작업 시작 상태로 변경
        file_item.status = FileStatus.PROCESSING
        file_item.start_time = datetime.now()
        if self.parent.on_file_status_changed:
            self.parent.on_file_status_changed(file_id, FileStatus.PROCESSING)
        
        self.parent.queue_manager.add_task(
            TaskType.PROCESS_FILE,
            task_data,
            TaskPriority.HIGH,
            callback=lambda result, fid=file_id: self._handle_task_result(fid, result)
        )
        
        self.parent.logger.info(f"즉시 처리 요청: {file_path.name}")
        return file_id
    
    def cancel_file(self, file_id: str) -> bool:
        """
        파일 처리 취소
        
        Args:
            file_id: 취소할 파일 ID
            
        Returns:
            bool: 취소 성공 여부
        """
        if file_id not in self.parent.file_items:
            return False
        
        file_item = self.parent.file_items[file_id]
        
        # 대기 중이거나 처리 중인 경우만 취소 가능
        from .base import FileStatus
        if file_item.status not in [FileStatus.WAITING, FileStatus.PROCESSING]:
            return False
        
        # 큐에서 제거 시도
        removed = self.parent.queue_manager.cancel_task(file_id)
        
        # 상태 업데이트
        file_item.status = FileStatus.CANCELLED
        file_item.end_time = datetime.now()
        file_item.message = "사용자에 의해 취소됨"
        
        # UI 콜백
        if self.parent.on_file_status_changed:
            self.parent.on_file_status_changed(file_id, FileStatus.CANCELLED)
        
        self.parent.logger.info(f"파일 취소: {file_item.filename}")
        return True
    
    def retry_file(self, file_id: str) -> bool:
        """
        파일 처리 재시도
        
        Args:
            file_id: 재시도할 파일 ID
            
        Returns:
            bool: 재시도 성공 여부
        """
        if file_id not in self.parent.file_items:
            return False
        
        file_item = self.parent.file_items[file_id]
        
        # 오류 상태인 경우만 재시도 가능
        from .base import FileStatus
        if file_item.status != FileStatus.ERROR:
            return False
        
        # 상태 초기화
        file_item.status = FileStatus.PROCESSING
        file_item.start_time = datetime.now()
        file_item.end_time = None
        file_item.progress = 0
        file_item.message = "재시도 중..."
        file_item.error_count = 0
        file_item.warning_count = 0
        
        # UI 콜백
        if self.parent.on_file_status_changed:
            self.parent.on_file_status_changed(file_id, FileStatus.PROCESSING)
        
        # 작업 큐에 다시 추가
        task_data = {
            'file_path': str(file_item.path),
            'profile': file_item.profile,
            'auto_fix': False
        }
        
        self.parent.queue_manager.add_task(
            TaskType.PROCESS_FILE,
            task_data,
            TaskPriority.NORMAL,
            callback=lambda result, fid=file_id: self._handle_task_result(fid, result)
        )
        
        self.parent.logger.info(f"파일 재시도: {file_item.filename}")
        return True
    
    def _handle_task_result(self, file_id: str, result: Any):
        """작업 결과 처리"""
        if file_id not in self.parent.file_items:
            return
        
        file_item = self.parent.file_items[file_id]
        
        # 결과에 따른 상태 업데이트
        if hasattr(result, 'success') and result.success:
            from .base import FileStatus
            file_item.status = FileStatus.COMPLETED
            file_item.end_time = datetime.now()
            file_item.processing_time = (file_item.end_time - file_item.start_time).total_seconds()
            
            # 결과 정보 업데이트
            if hasattr(result, 'error_count'):
                file_item.error_count = result.error_count
            if hasattr(result, 'warning_count'):
                file_item.warning_count = result.warning_count
            if hasattr(result, 'quality_score'):
                file_item.quality_score = result.quality_score
            if hasattr(result, 'report_paths'):
                file_item.report_paths = result.report_paths
            
            file_item.message = "처리 완료"
            
            # UI 콜백
            if self.parent.on_file_completed:
                self.parent.on_file_completed(file_id, file_item)
        else:
            from .base import FileStatus
            file_item.status = FileStatus.ERROR
            file_item.end_time = datetime.now()
            error_message = getattr(result, 'error_message', '알 수 없는 오류')
            file_item.message = error_message
            
            # UI 콜백
            if self.parent.on_file_error:
                self.parent.on_file_error(file_id, error_message)
        
        # 상태 변경 콜백
        if self.parent.on_file_status_changed:
            self.parent.on_file_status_changed(file_id, file_item.status)
    
    def pause_processing(self) -> bool:
        """
        처리 일시정지
        
        Returns:
            bool: 일시정지 성공 여부
        """
        if self.parent.is_paused:
            return False  # 이미 일시정지 상태
        
        self.parent.is_paused = True
        
        # 큐 매니저에 일시정지 요청
        if hasattr(self.parent.queue_manager, 'pause'):
            self.parent.queue_manager.pause()
        
        # 모든 대기 중인 파일 상태 업데이트
        from .base import FileStatus
        for file_id, file_item in self.parent.file_items.items():
            if file_item.status == FileStatus.WAITING:
                file_item.message = "일시정지됨"
                if self.parent.on_file_status_changed:
                    self.parent.on_file_status_changed(file_id, file_item.status)
        
        self.parent.logger.info("처리 일시정지됨")
        return True
    
    def resume_processing(self) -> bool:
        """
        처리 재개
        
        Returns:
            bool: 재개 성공 여부
        """
        if not self.parent.is_paused:
            return False  # 일시정지 상태가 아님
        
        self.parent.is_paused = False
        
        # 큐 매니저에 재개 요청
        if hasattr(self.parent.queue_manager, 'resume'):
            self.parent.queue_manager.resume()
        
        # 모든 대기 중인 파일 상태 업데이트
        from .base import FileStatus
        for file_id, file_item in self.parent.file_items.items():
            if file_item.status == FileStatus.WAITING:
                file_item.message = "대기 중"
                if self.parent.on_file_status_changed:
                    self.parent.on_file_status_changed(file_id, file_item.status)
        
        self.parent.logger.info("처리 재개됨")
        return True
    
    def toggle_pause(self) -> bool:
        """
        처리 일시정지/재개 토글
        
        Returns:
            bool: 현재 일시정지 상태 (True: 일시정지, False: 실행 중)
        """
        if self.parent.is_paused:
            self.resume_processing()
            return False
        else:
            self.pause_processing()
            return True