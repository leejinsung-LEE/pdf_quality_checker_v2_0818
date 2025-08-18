# src/processing/pipeline/progress.py
"""
진행률 추적 및 관리
"""

from typing import Optional, Callable
import logging

from .enums import ProcessingStatus


class ProgressManager:
    """파이프라인 진행률 관리"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        self.callback: Optional[Callable] = None
        self.current_progress: dict = {}  # file_id별 진행 상태 저장
    
    def set_callback(self, callback: Callable[[str, ProcessingStatus, int, str], None]):
        """
        진행 상태 콜백 설정
        
        Args:
            callback: (file_id, status, progress_percent, message) 콜백
        """
        self.callback = callback
    
    def update(self,
              file_id: Optional[str],
              status: ProcessingStatus,
              progress: int,
              message: str):
        """
        진행 상태 업데이트
        
        Args:
            file_id: 파일 식별자
            status: 처리 상태
            progress: 진행률 (0-100)
            message: 상태 메시지
        """
        # 진행 상태 저장
        if file_id:
            self.current_progress[file_id] = {
                'status': status,
                'progress': progress,
                'message': message
            }
        
        # 콜백 호출
        if self.callback and file_id:
            try:
                self.callback(file_id, status, progress, message)
            except Exception as e:
                self.logger.error(f"진행률 콜백 오류: {e}")
        
        # 로깅
        self.logger.debug(f"[{file_id or 'unknown'}] {status.value}: {progress}% - {message}")
    
    def get_progress(self, file_id: str) -> Optional[dict]:
        """
        특정 파일의 현재 진행 상태 조회
        
        Args:
            file_id: 파일 식별자
            
        Returns:
            진행 상태 정보
        """
        return self.current_progress.get(file_id)
    
    def clear_progress(self, file_id: str):
        """
        특정 파일의 진행 상태 제거
        
        Args:
            file_id: 파일 식별자
        """
        if file_id in self.current_progress:
            del self.current_progress[file_id]
    
    def clear_all(self):
        """모든 진행 상태 제거"""
        self.current_progress.clear()